"""Sherlock Mystery Game - Main Streamlit Application"""

import streamlit as st
import os
import json
from config import PERSONAJES, SOLUCION, CONFIG_FILE, VICTORIAN_IMAGES, UBICACIONES, IMAGENES_DINAMICAS
from game_logic import (
    detectar_pista, validar_solucion, calcular_reputacion, generar_mensaje_lestrade,
    detectar_pista_falsa, verificar_pista_oculta
)
from agents import CharacterAgentManager
from character_detection import detectar_menciones_personajes
from confidence_system import (
    inicializar_confianza, analizar_tono_pregunta, actualizar_confianza,
    obtener_efecto_confianza, generar_mensaje_confianza
)
from watson_narrator import (
    generar_descripcion_inicial, 
    obtener_comentario_watson,
    detectar_mencion_correspondencia,
    generar_intervencion_correspondencia,
    detectar_peticion_resumen,
    generar_resumen_caso
)
import time
from PIL import Image
import requests
from io import BytesIO


def cargar_api_key():
    """Carga la API key desde archivo de configuración o sesión"""
    if "api_key" in st.session_state and st.session_state.api_key:
        return st.session_state.api_key
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                api_key = config.get("openai_key", "")
                if api_key:
                    st.session_state.api_key = api_key
                    return api_key
        except Exception as e:
            st.error(f"Error leyendo configuración: {e}")
    
    return None


def guardar_api_key(api_key: str):
    """Guarda la API key en archivo de configuración y sesión"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"openai_key": api_key}, f)
        st.session_state.api_key = api_key
        st.success("API key guardada correctamente")
    except Exception as e:
        st.error(f"Error guardando configuración: {e}")


def inicializar_juego():
    """Inicializa el estado del juego. El usuario juega como Sherlock Holmes."""
    if "historia" not in st.session_state:
        st.session_state.historia = []
    
    # Interlocutor actual: con quién está hablando Holmes (Rose o Arthur)
    # NOTA: El usuario ES Holmes, no habla CON Holmes
    if "interlocutor_actual" not in st.session_state:
        st.session_state.interlocutor_actual = None  # Inicialmente nadie, Watson presenta el caso
    
    if "pistas_descubiertas" not in st.session_state:
        st.session_state.pistas_descubiertas = set()
    
    if "notas" not in st.session_state:
        st.session_state.notas = []
    
    if "mensajes_iniciales" not in st.session_state:
        st.session_state.mensajes_iniciales = True
    
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = None
    
    if "personajes_disponibles" not in st.session_state:
        # Personajes con los que Holmes puede hablar (NO incluye a Holmes ni a Watson)
        st.session_state.personajes_disponibles = set()
    
    if "correspondencia_leida" not in st.session_state:
        # Flag para evitar mostrar la correspondencia múltiples veces
        st.session_state.correspondencia_leida = False
    
    if "reputacion" not in st.session_state:
        # Sistema de reputación de Sherlock Holmes (inicialmente 100 puntos)
        st.session_state.reputacion = 100
    
    if "confianza" not in st.session_state:
        # Sistema de confianza con personajes
        st.session_state.confianza = inicializar_confianza()
    
    if "pistas_falsas_descubiertas" not in st.session_state:
        # Pistas falsas (red herrings) descubiertas
        st.session_state.pistas_falsas_descubiertas = set()
    
    if "pistas_ocultas_descubiertas" not in st.session_state:
        # Pistas ocultas descubiertas
        st.session_state.pistas_ocultas_descubiertas = set()
    
    if "ubicacion_actual" not in st.session_state:
        # Sistema de ubicaciones
        st.session_state.ubicacion_actual = "estudio"
    
    if "personajes_hablados" not in st.session_state:
        # Personajes con los que se ha hablado (para pistas ocultas)
        st.session_state.personajes_hablados = []
    
    if "tiempo_inicio" not in st.session_state:
        # Sistema de tensión temporal
        st.session_state.tiempo_inicio = time.time()
        st.session_state.tiempo_limite = 7200  # 2 horas en segundos (ajustable)
    
    if "secretos_descubiertos" not in st.session_state:
        # Secretos adicionales descubiertos (para múltiples finales)
        st.session_state.secretos_descubiertos = []
    
    if "mostrar_form_resolver" not in st.session_state:
        # Flag para mostrar el formulario de resolución
        st.session_state.mostrar_form_resolver = False


def agregar_mensaje_inicial():
    """Agrega mensajes iniciales del juego con Watson como narrador. El usuario es Holmes."""
    if st.session_state.mensajes_iniciales:
        # Watson describe el caso inicialmente
        mensaje_watson = generar_descripcion_inicial()
        mensaje_holmes = "Interesante, Watson. Observemos los detalles. Debo interrogar a los sospechosos para resolver este caso."
        
        st.session_state.historia.append({
            "role": "system",
            "content": mensaje_watson,
            "tipo": "narrador",
            "autor": "Dr. Watson"
        })
        st.session_state.historia.append({
            "role": "assistant",
            "content": mensaje_holmes,
            "tipo": "holmes",
            "personaje": "Sherlock Holmes"
        })
        
        # Sugerir que mencione a los sospechosos
        st.session_state.historia.append({
            "role": "system",
            "content": "Dr. Watson sugiere: Holmes, hay varios testigos disponibles: Rose la camarera, Arthur el sobrino, y Jenkins el mayordomo. Menciona sus nombres para interrogarlos.",
            "tipo": "narrador",
            "autor": "Dr. Watson"
        })
        
        st.session_state.mensajes_iniciales = False


def obtener_agent_manager(api_key: str):
    """Obtiene o crea el gestor de agentes LangGraph"""
    # Si no existe o la API key cambió, crear uno nuevo
    if (st.session_state.agent_manager is None or 
        (hasattr(st.session_state, 'agent_manager') and 
         hasattr(st.session_state.agent_manager, 'api_key') and
         st.session_state.agent_manager.api_key != api_key)):
        st.session_state.agent_manager = CharacterAgentManager(api_key)
    return st.session_state.agent_manager


def consultar_ia(pregunta: str, api_key: str):
    """
    Procesa la pregunta de Holmes (el usuario) al interlocutor actual o mencionado.
    El usuario ES Holmes, por lo que la pregunta se muestra como de Holmes.
    Si menciona a alguien, ese personaje se convierte automáticamente en el interlocutor.
    """
    try:
        interlocutor_id = st.session_state.interlocutor_actual
        
        # Detectar si es una petición de resumen a Watson
        if detectar_peticion_resumen(pregunta):
            # Generar resumen de Watson
            resumen = generar_resumen_caso(
                st.session_state.historia,
                st.session_state.pistas_descubiertas,
                st.session_state.notas
            )
            
            # Agregar el resumen a la historia
            st.session_state.historia.append({
                "role": "system",
                "content": resumen,
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
            
            return None, None  # No hay respuesta de personaje, solo el resumen
        
        # El usuario ES Holmes, su pregunta se guarda como de Holmes
        # Agregar pregunta de Holmes a la historia
        st.session_state.historia.append({
            "role": "user",
            "content": pregunta,
            "tipo": "holmes",
            "personaje": "Sherlock Holmes"
        })
        
        # Detectar si es un comando para cambiar de interlocutor (antes de procesar la pregunta)
        pregunta_lower = pregunta.lower()
        comandos_cambio = [
            "quiero hablar con", "hablar con", "cambiar a", "preguntar a",
            "necesito hablar", "llama a", "trae a", "cambiar interlocutor a"
        ]
        es_comando_cambio = any(comando in pregunta_lower for comando in comandos_cambio)
        
        # Detectar menciones de personajes en la pregunta de Holmes
        personajes_mencionados_pregunta = detectar_menciones_personajes(pregunta)
        
        # LÓGICA MEJORADA: 
        # 1. Si hay interlocutor actual: solo agregar menciones a disponibles, NO cambiar automáticamente
        # 2. Si NO hay interlocutor: el primer personaje mencionado se convierte en interlocutor
        # 3. Solo cambiar si es un comando explícito
        
        if personajes_mencionados_pregunta:
            # Buscar el primer personaje mencionado que no sea Holmes
            personaje_objetivo = None
            for personaje_id in personajes_mencionados_pregunta:
                if personaje_id != "sherlock":
                    personaje_objetivo = personaje_id
                    break
            
            if personaje_objetivo:
                # Agregar a personajes disponibles si no está
                if personaje_objetivo not in st.session_state.personajes_disponibles:
                    st.session_state.personajes_disponibles.add(personaje_objetivo)
                    nombre_nuevo = PERSONAJES[personaje_objetivo]["nombre"]
                    st.session_state.historia.append({
                        "role": "system",
                        "content": f"Dr. Watson observa: {nombre_nuevo} es mencionado y se acerca a la escena.",
                        "tipo": "narrador",
                        "autor": "Dr. Watson"
                    })
                
                # SOLO cambiar el interlocutor si:
                # 1. Es un comando explícito de cambio, O
                # 2. No hay interlocutor actual (primera mención)
                if es_comando_cambio:
                    # Comando explícito: cambiar interlocutor SIEMPRE, incluso si hay interlocutor actual
                    if interlocutor_id != personaje_objetivo:
                        interlocutor_id = personaje_objetivo
                        st.session_state.interlocutor_actual = personaje_objetivo
                        nombre_nuevo = PERSONAJES[personaje_objetivo]["nombre"]
                        st.session_state.historia.append({
                            "role": "system",
                            "content": f"Dr. Watson observa: Holmes se dirige ahora hacia {nombre_nuevo}.",
                            "tipo": "narrador",
                            "autor": "Dr. Watson"
                        })
                    # Si era un comando de cambio, no enviar la pregunta original al personaje
                    return None, None  # Solo cambiar interlocutor, no procesar pregunta
                elif not interlocutor_id:
                    # No hay interlocutor actual: el personaje mencionado se convierte en interlocutor
                    interlocutor_id = personaje_objetivo
                    st.session_state.interlocutor_actual = personaje_objetivo
                    nombre_nuevo = PERSONAJES[personaje_objetivo]["nombre"]
                    st.session_state.historia.append({
                        "role": "system",
                        "content": f"Dr. Watson observa: Holmes se dirige ahora hacia {nombre_nuevo}.",
                        "tipo": "narrador",
                        "autor": "Dr. Watson"
                    })
                # Si hay interlocutor actual Y NO es comando: NO cambiar, solo agregar a disponibles
        
        # Si era un comando pero no se encontró personaje, avisar
        if es_comando_cambio and not personajes_mencionados_pregunta:
            return None, "Menciona el nombre del personaje con quien quieres hablar (Rose, Arthur, Jenkins, etc.)."
        
        # Si todavía no hay interlocutor, no se puede procesar
        if not interlocutor_id or interlocutor_id not in PERSONAJES:
            return None, "No hay interlocutor. Menciona a alguien (Rose, Arthur) o selecciona un interlocutor del panel."
        
        # ========== SISTEMA DE CONFIANZA ==========
        # Analizar tono de la pregunta y actualizar confianza
        tono = analizar_tono_pregunta(pregunta)
        nueva_confianza, cambio_confianza = actualizar_confianza(
            interlocutor_id, 
            st.session_state.confianza, 
            tono
        )
        
        # Generar mensaje de Watson sobre cambio de confianza (si es significativo)
        if abs(cambio_confianza) >= 3:
            mensaje_confianza = generar_mensaje_confianza(
                interlocutor_id, 
                nueva_confianza, 
                cambio_confianza
            )
            if mensaje_confianza:
                st.session_state.historia.append({
                    "role": "system",
                    "content": mensaje_confianza,
                    "tipo": "narrador",
                    "autor": "Dr. Watson"
                })
        
        # Obtener efectos de la confianza actual
        efectos_confianza = obtener_efecto_confianza(interlocutor_id, nueva_confianza)
        
        # Agregar personaje a la lista de personajes hablados (para pistas ocultas)
        if interlocutor_id not in st.session_state.personajes_hablados:
            st.session_state.personajes_hablados.append(interlocutor_id)
        
        # Obtener el gestor de agentes
        agent_manager = obtener_agent_manager(api_key)
        interlocutor = PERSONAJES[interlocutor_id]
        
        # Construir historial para el interlocutor (solo mensajes relevantes con este interlocutor)
        historial_interlocutor = []
        for msg in st.session_state.historia:
            # Solo incluir interacciones con este interlocutor específico
            if msg.get("tipo") == "holmes":
                # Mensajes de Holmes (solo si hay un interlocutor actual o fue dirigido a este)
                historial_interlocutor.append({
                    "role": "user",
                    "content": msg["content"],
                    "tipo": "holmes"
                })
            elif msg.get("tipo") == "npc" and msg.get("personaje") == interlocutor["nombre"]:
                # Respuestas del interlocutor
                historial_interlocutor.append({
                    "role": "assistant",
                    "content": msg["content"],
                    "tipo": "npc",
                    "personaje": interlocutor["nombre"]
                })
        
        # Consultar al interlocutor usando LangGraph
        respuesta = agent_manager.consultar_personaje(
            interlocutor_id,
            pregunta,
            historial_interlocutor
        )
        
        # Ajustar respuesta según nivel de confianza (si es muy baja, puede ser más evasiva)
        if efectos_confianza["puede_mentir"] and tono == "agresiva":
            # Con muy baja confianza y pregunta agresiva, respuesta puede ser más evasiva
            pass  # Los agentes ya manejan esto en sus prompts
        
        # Agregar respuesta del interlocutor
        st.session_state.historia.append({
            "role": "assistant",
            "content": respuesta,
            "tipo": "npc",
            "personaje": interlocutor["nombre"]
        })
        
        # ========== DETECCIÓN DE PISTAS ==========
        # Detectar pistas normales
        nuevas_pistas = detectar_pista(respuesta, st.session_state.pistas_descubiertas)
        for pista in nuevas_pistas:
            if pista not in st.session_state.notas:
                st.session_state.notas.append(pista)
        
        # Detectar pistas falsas (red herrings)
        nuevas_pistas_falsas = detectar_pista_falsa(
            respuesta, 
            st.session_state.pistas_falsas_descubiertas
        )
        for pista_falsa in nuevas_pistas_falsas:
            st.session_state.historia.append({
                "role": "system",
                "content": f"🔍 Pista encontrada: {pista_falsa['descripcion']}\n\n⚠️ Watson nota: Esta pista parece sospechosa. {pista_falsa['explicacion']}",
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
        
        # Verificar pistas ocultas
        contexto_pista_oculta = {
            "personajes_hablados": st.session_state.personajes_hablados,
            "ubicacion_actual": st.session_state.ubicacion_actual,
            "correspondencia_insistida": st.session_state.correspondencia_leida,
            "pistas_ocultas_descubiertas": st.session_state.pistas_ocultas_descubiertas
        }
        pista_oculta = verificar_pista_oculta(pregunta, contexto_pista_oculta)
        if pista_oculta:
            st.session_state.pistas_ocultas_descubiertas.add(pista_oculta["id"])
            st.session_state.historia.append({
                "role": "system",
                "content": f"🔍✨ Pista oculta descubierta: {pista_oculta['descripcion']}",
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
        
        # Detectar mención a la correspondencia secreta
        # Verificar tanto en la pregunta del usuario como en la respuesta del personaje
        menciona_correspondencia = (
            detectar_mencion_correspondencia(pregunta) or 
            detectar_mencion_correspondencia(respuesta)
        )
        
        if menciona_correspondencia and not st.session_state.correspondencia_leida:
            # Watson lee las cartas
            intervencion_correspondencia = generar_intervencion_correspondencia()
            st.session_state.historia.append({
                "role": "system",
                "content": intervencion_correspondencia,
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
            st.session_state.correspondencia_leida = True
        
        # Detectar menciones de personajes en la respuesta del interlocutor
        personajes_mencionados_respuesta = detectar_menciones_personajes(respuesta)
        for personaje_id in personajes_mencionados_respuesta:
            # Excluir a Holmes y al interlocutor actual
            if personaje_id != "sherlock" and personaje_id != interlocutor_id:
                if personaje_id not in st.session_state.personajes_disponibles:
                    st.session_state.personajes_disponibles.add(personaje_id)
                    nombre_nuevo = PERSONAJES[personaje_id]["nombre"]
                    st.session_state.historia.append({
                        "role": "system",
                        "content": f"Dr. Watson nota: {nombre_nuevo} es mencionado y ahora está presente en la escena.",
                        "tipo": "narrador",
                        "autor": "Dr. Watson"
                    })
        
        # Comentario ocasional de Watson (30% de probabilidad)
        comentario_watson = obtener_comentario_watson(probabilidad=0.3)
        if comentario_watson:
            st.session_state.historia.append({
                "role": "system",
                "content": comentario_watson,
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
        
        return respuesta, None
    
    except Exception as e:
        return None, str(e)


def cambiar_interlocutor(personaje_id: str = None):
    """
    Cambia el interlocutor con quien Holmes está hablando.
    Holmes (el usuario) NO puede elegirse a sí mismo.
    """
    if personaje_id:
        # Cambiar al interlocutor específico
        if personaje_id in PERSONAJES and personaje_id != "sherlock" and personaje_id in st.session_state.personajes_disponibles:
            st.session_state.interlocutor_actual = personaje_id
            nombre_nuevo = PERSONAJES[personaje_id]["nombre"]
            st.session_state.historia.append({
                "role": "system",
                "content": f"Dr. Watson observa: Holmes se dirige ahora hacia {nombre_nuevo}.",
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
    else:
        # Cambiar al siguiente interlocutor disponible
        personajes_disponibles = sorted([p for p in st.session_state.personajes_disponibles if p != "sherlock"])
        if len(personajes_disponibles) > 0:
            if st.session_state.interlocutor_actual in personajes_disponibles:
                idx_actual = personajes_disponibles.index(st.session_state.interlocutor_actual)
                idx_siguiente = (idx_actual + 1) % len(personajes_disponibles)
            else:
                idx_siguiente = 0
            
            st.session_state.interlocutor_actual = personajes_disponibles[idx_siguiente]
            nombre_nuevo = PERSONAJES[st.session_state.interlocutor_actual]["nombre"]
            st.session_state.historia.append({
                "role": "system",
                "content": f"Dr. Watson observa: Holmes se dirige ahora hacia {nombre_nuevo}.",
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })


def cargar_imagen(url_or_path: str):
    """Carga una imagen desde URL o ruta local"""
    try:
        if url_or_path.startswith("http"):
            response = requests.get(url_or_path, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            return Image.open(url_or_path)
    except Exception as e:
        # No mostrar warning aquí, se maneja en el código que llama
        return None


def buscar_imagen_local(base_path: str):
    """Busca una imagen local con diferentes extensiones"""
    extensiones = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    for ext in extensiones:
        path_con_ext = base_path.replace('.jpg', ext).replace('.jpeg', ext).replace('.png', ext)
        if not path_con_ext.endswith(ext):
            # Si no tiene extensión en el path original, agregar la extensión
            if '.' not in os.path.basename(base_path):
                path_con_ext = base_path + ext
            else:
                # Reemplazar la extensión existente
                path_sin_ext = os.path.splitext(base_path)[0]
                path_con_ext = path_sin_ext + ext
        
        if os.path.exists(path_con_ext):
            img = cargar_imagen(path_con_ext)
            if img:
                return img
    return None


def mostrar_panel_personajes_sidebar():
    """
    Muestra el panel de personajes disponibles en el sidebar.
    El usuario ES Holmes, por lo que Holmes NO aparece en el panel.
    Solo se muestran los interlocutores disponibles (Rose, Arthur, etc.)
    """
    if len(st.session_state.personajes_disponibles) == 0:
        st.sidebar.header("👥 Interlocutores")
        st.sidebar.info("Aún no hay interlocutores disponibles. Interroga y menciona a los sospechosos para que aparezcan.")
        return
    
    st.sidebar.header("👥 Interlocutores")
    st.sidebar.caption("Eres Holmes. Haz clic para hablar con alguien")
    
    # Ordenar personajes disponibles (excluir a Holmes)
    personajes_disponibles = sorted([p for p in st.session_state.personajes_disponibles if p != "sherlock"], 
                                    key=lambda x: list(PERSONAJES.keys()).index(x))
    
    interlocutor_actual_id = st.session_state.interlocutor_actual
    
    # Mostrar interlocutor actual primero (grande)
    if interlocutor_actual_id and interlocutor_actual_id in personajes_disponibles:
        interlocutor_actual = PERSONAJES[interlocutor_actual_id]
        nombre_actual = interlocutor_actual["nombre"]
        nombre_corto_actual = nombre_actual.split(',')[0] if ',' in nombre_actual else nombre_actual
        
        # Cargar imagen del interlocutor actual
        personaje_img_path = f"images/{interlocutor_actual_id}"
        img_interlocutor_actual = buscar_imagen_local(personaje_img_path)
        
        st.sidebar.markdown("### 🟢 Hablando ahora")
        if img_interlocutor_actual:
            # Imagen grande para el interlocutor actual
            st.sidebar.markdown('<div style="border: 3px solid #b58900; border-radius: 10px; padding: 5px; background-color: #eee8d5; margin-bottom: 1rem;">', unsafe_allow_html=True)
            st.sidebar.image(img_interlocutor_actual, use_container_width=True, caption=f"{nombre_corto_actual}")
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f'<div style="border: 3px solid #b58900; border-radius: 10px; padding: 10px; background-color: #eee8d5; text-align: center; margin-bottom: 1rem;"><strong>{nombre_corto_actual}</strong></div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Mostrar otros interlocutores disponibles (pequeños, clickeables)
    otros_interlocutores = [p for p in personajes_disponibles if p != interlocutor_actual_id]
    
    if otros_interlocutores:
        st.sidebar.markdown("### 👤 Otros disponibles")
        
        for personaje_id in otros_interlocutores:
            personaje = PERSONAJES[personaje_id]
            nombre = personaje["nombre"]
            nombre_corto = nombre.split(',')[0] if ',' in nombre else nombre
            
            # Cargar imagen del personaje
            personaje_img_path = f"images/{personaje_id}"
            img_personaje = buscar_imagen_local(personaje_img_path)
            
            # Crear contenedor clickeable para el personaje
            if img_personaje:
                # Mostrar imagen pequeña
                st.sidebar.markdown(f'<div style="border: 2px solid #ccc; border-radius: 5px; padding: 5px; margin-bottom: 0.5rem; text-align: center;">', unsafe_allow_html=True)
                st.sidebar.image(img_personaje, width=80, caption=nombre_corto)
                st.sidebar.markdown('</div>', unsafe_allow_html=True)
                
                # Botón clickeable
                if st.sidebar.button(
                    f"Hablar con {nombre_corto}",
                    key=f"btn_personaje_{personaje_id}",
                    use_container_width=True,
                    type="secondary"
                ):
                    cambiar_interlocutor(personaje_id)
                    st.rerun()
            else:
                # Si no hay imagen, mostrar solo el botón
                if st.sidebar.button(
                    f"👤 {nombre_corto}",
                    key=f"btn_personaje_{personaje_id}",
                    use_container_width=True,
                    type="secondary"
                ):
                    cambiar_interlocutor(personaje_id)
                    st.rerun()


def main():
    """Función principal de la aplicación"""
    st.set_page_config(
        page_title="Sherlock Mystery Game",
        page_icon="🔍",
        layout="wide"
    )
    
    # CSS personalizado con estilo victoriano
    st.markdown("""
    <style>
    .stApp {
        background-color: #fdf6e3;
        font-family: Georgia, serif;
    }
    .victorian-header {
        background-color: #b58900;
        color: #fdf6e3;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    .message-user {
        background-color: #073642;
        color: #fdf6e3;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 3px;
    }
    .message-npc {
        background-color: #eee8d5;
        color: #586e75;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 3px;
        border-left: 3px solid #b58900;
    }
    .message-narrator {
        background-color: #cb4b16;
        color: #fdf6e3;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 3px;
        font-style: italic;
    }
    .character-panel {
        background-color: #eee8d5;
        padding: 1rem;
        border-radius: 5px;
        border: 2px solid #b58900;
        margin: 1rem 0;
    }
    .character-active {
        border: 3px solid #b58900 !important;
        background-color: #eee8d5 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.markdown('<div class="victorian-header"><h1>🔍 Sherlock Mystery Game</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Verificar API key
    api_key = cargar_api_key()
    
    if not api_key:
        # Formulario para ingresar API key
        st.header("🔑 Autenticación")
        st.info("Por favor, ingresa tu API key de OpenAI para comenzar.")
        
        api_key_input = st.text_input(
            "OpenAI API Key (sk-...):",
            type="password",
            placeholder="sk-XXXXXXXXXX"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Guardar y comenzar", type="primary"):
                if api_key_input and api_key_input.strip().startswith("sk-"):
                    guardar_api_key(api_key_input.strip())
                    st.rerun()
                else:
                    st.error("Por favor ingresa una API key válida que comience con 'sk-'")
        
        # Información sobre cómo obtener la API key
        with st.expander("¿Cómo obtener una API key de OpenAI?"):
            st.markdown("""
            1. Visita [platform.openai.com](https://platform.openai.com)
            2. Crea una cuenta o inicia sesión
            3. Ve a "API Keys" en tu perfil
            4. Crea una nueva API key
            5. Copia la clave (comienza con `sk-`)
            
            **Nota:** La clave se guarda localmente en tu máquina en el archivo `.sherlock_config`
            """)
        
        return
    
    # Inicializar juego
    inicializar_juego()
    
    # Layout principal
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_main:
        # Mostrar imagen del caso (siempre visible al inicio)
        st.subheader("🖼️ Escena del Crimen")
        imagen_caso_path = "images/case"
        imagen_caso_url = VICTORIAN_IMAGES.get("study", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Victorian_library.jpg/800px-Victorian_library.jpg")
        
        # Buscar imagen local con diferentes extensiones
        img_cargada = buscar_imagen_local(imagen_caso_path)
        
        # Si no existe local, intentar cargar desde URL (pero sin error si falla)
        if img_cargada is None:
            img_cargada = cargar_imagen(imagen_caso_url)
            if img_cargada is None:
                st.info("ℹ️ No se pudo cargar la imagen del caso. Asegúrate de tener `case.jpg` o `case.jpeg` en la carpeta `images/`.")
        
        # Mostrar la imagen si se cargó correctamente
        if img_cargada:
            st.image(img_cargada, caption="La biblioteca de Lord Huxley - Escena del crimen", use_container_width=True)
        
        st.markdown("---")
        
        # Agregar mensajes iniciales si es necesario
        agregar_mensaje_inicial()
        
        # Mostrar historial de conversación
        st.subheader("📜 Conversación")
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.historia:
                if msg.get("tipo") == "holmes" or msg.get("tipo") == "user":
                    # Mensajes de Holmes (el usuario)
                    nombre_holmes = msg.get("personaje", "Sherlock Holmes")
                    st.markdown(f'<div class="message-user"><strong>{nombre_holmes}:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                elif msg.get("tipo") == "narrador":
                    autor = msg.get("autor", "Narrador")
                    st.markdown(f'<div class="message-narrator"><strong>{autor}:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                elif msg.get("tipo") == "npc":
                    nombre = msg.get("personaje", "Interlocutor")
                    st.markdown(f'<div class="message-npc"><strong>{nombre}:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Input con soporte para Enter (usando st.chat_input)
        # Siempre habilitado - Holmes puede mencionar a alguien directamente
        if st.session_state.interlocutor_actual:
            interlocutor_nombre = PERSONAJES[st.session_state.interlocutor_actual]["nombre"]
            placeholder_text = f"Pregunta a {interlocutor_nombre} como Holmes... (Presiona Enter para enviar)"
        else:
            placeholder_text = "Como Holmes, pregunta a los sospechosos... (Menciona a Rose o Arthur, o selecciona del panel)"
        
        pregunta = st.chat_input(
            placeholder=placeholder_text,
            key="chat_input"
        )
        
        # Procesar pregunta cuando se presiona Enter
        if pregunta:
            with st.spinner("Pensando..."):
                respuesta, error = consultar_ia(pregunta, api_key)
                if error:
                    st.warning(f"⚠️ {error}")
                    st.rerun()
                elif respuesta is None and error is None:
                    # Solo cambio de interlocutor, sin respuesta
                    st.rerun()
                else:
                    st.rerun()
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Cambiar interlocutor (siguiente)", use_container_width=True, disabled=len(st.session_state.personajes_disponibles) == 0):
                cambiar_interlocutor()  # Cambiar al siguiente disponible
                st.rerun()
        
        with col2:
            if st.button("✅ Resolver crimen", use_container_width=True):
                st.session_state.mostrar_form_resolver = True
                st.rerun()
        
        with col3:
            if st.button("🔄 Reiniciar juego", use_container_width=True):
                # Limpiar todo el estado excepto la API key
                api_key_backup = st.session_state.get("api_key")
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                if api_key_backup:
                    st.session_state.api_key = api_key_backup
                st.rerun()
        
        # Mostrar resultado de la solución después del rerun (si existe)
        if st.session_state.get("solucion_verificada", False):
            es_correcta = st.session_state.solucion_es_correcta
            titulo = st.session_state.solucion_titulo
            mensaje = st.session_state.solucion_mensaje
            puntos_cambiados = st.session_state.solucion_puntos_cambiados
            reputacion_nueva = st.session_state.solucion_reputacion_nueva
            
            # Mostrar resultado en la UI
            if es_correcta:
                st.success(f"🎉 {titulo}")
                st.balloons()
                if puntos_cambiados > 0:
                    st.success(f"🌟 Tu reputación ha aumentado en {puntos_cambiados} puntos (ahora: {reputacion_nueva})")
            else:
                st.error(f"❌ {titulo}")
                if puntos_cambiados < 0:
                    st.warning(f"📉 Tu reputación ha disminuido en {abs(puntos_cambiados)} puntos (ahora: {reputacion_nueva})")
            
            st.info(mensaje)
            
            # Limpiar el flag para que no se muestre de nuevo
            st.session_state.solucion_verificada = False
        
        # Modal de solución
        if st.session_state.mostrar_form_resolver:
            with st.form("form_resolver"):
                st.subheader("Resolver el crimen")
                culpable = st.selectbox(
                    "¿Quién es el culpable?",
                    ["", "sherlock", "rose", "arthur", "jenkins"]
                )
                arma = st.text_input("¿Qué arma se usó?", placeholder="daga")
                motivo = st.text_input("¿Cuál fue el motivo?", placeholder="herencia")
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("✅ Verificar solución", use_container_width=True)
                with col_cancel:
                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                        st.session_state.mostrar_form_resolver = False
                        st.rerun()
                
                if submitted:
                    # Validar que todos los campos estén llenos
                    if not culpable or culpable == "":
                        st.error("❌ Por favor, selecciona un culpable.")
                    elif not arma or arma.strip() == "":
                        st.error("❌ Por favor, ingresa el arma utilizada.")
                    elif not motivo or motivo.strip() == "":
                        st.error("❌ Por favor, ingresa el motivo del crimen.")
                    else:
                        # Obtener reputación actual
                        reputacion_anterior = st.session_state.get("reputacion", 100)
                        
                        # Validar solución con múltiples finales
                        es_correcta, titulo, mensaje, final_info = validar_solucion(
                            culpable, arma, motivo, SOLUCION,
                            st.session_state.secretos_descubiertos
                        )
                        
                        # Calcular nueva reputación (con bonus según tipo de final)
                        reputacion_nueva, puntos_cambiados = calcular_reputacion(
                            es_correcta, reputacion_anterior, final_info.get("tipo")
                        )
                        st.session_state.reputacion = reputacion_nueva
                        
                        # Generar mensaje de Lestrade
                        mensaje_lestrade = generar_mensaje_lestrade(es_correcta, reputacion_anterior, reputacion_nueva)
                        
                        # Agregar mensaje de Lestrade a la historia ANTES de mostrar los resultados
                        st.session_state.historia.append({
                            "role": "system",
                            "content": mensaje_lestrade,
                            "tipo": "narrador",
                            "autor": "Inspector Lestrade"
                        })
                        
                        # Guardar el estado de la solución para mostrarlo después del rerun
                        st.session_state.solucion_verificada = True
                        st.session_state.solucion_es_correcta = es_correcta
                        st.session_state.solucion_titulo = titulo
                        st.session_state.solucion_mensaje = mensaje
                        st.session_state.solucion_puntos_cambiados = puntos_cambiados
                        st.session_state.solucion_reputacion_nueva = reputacion_nueva
                        st.session_state.mostrar_form_resolver = False  # Cerrar el formulario
                        
                        # Hacer rerun para mostrar el mensaje de Lestrade en el chat
                        st.rerun()
    
    with col_sidebar:
        # ========== SISTEMA DE TENSIÓN TEMPORAL ==========
        tiempo_transcurrido = time.time() - st.session_state.tiempo_inicio
        tiempo_restante = max(0, st.session_state.tiempo_limite - tiempo_transcurrido)
        horas_restantes = int(tiempo_restante // 3600)
        minutos_restantes = int((tiempo_restante % 3600) // 60)
        
        st.sidebar.header("⏰ Tiempo Restante")
        if tiempo_restante > 0:
            if tiempo_restante < 1800:  # Menos de 30 minutos
                st.sidebar.error(f"⚠️ {horas_restantes}h {minutos_restantes}m - ¡Urgente!")
            elif tiempo_restante < 3600:  # Menos de 1 hora
                st.sidebar.warning(f"⏳ {horas_restantes}h {minutos_restantes}m")
            else:
                st.sidebar.info(f"🕐 {horas_restantes}h {minutos_restantes}m")
        else:
            st.sidebar.error("⏰ ¡Tiempo agotado! Lestrade llegará pronto...")
        st.sidebar.markdown("---")
        
        # ========== SISTEMA DE UBICACIONES ==========
        st.sidebar.header("📍 Ubicación Actual")
        ubicacion_actual = st.session_state.ubicacion_actual
        ubicacion_info = UBICACIONES.get(ubicacion_actual, {})
        st.sidebar.info(f"**{ubicacion_info.get('nombre', ubicacion_actual)}**\n\n{ubicacion_info.get('descripcion', '')}")
        
        # Selector de ubicación
        ubicaciones_disponibles = list(UBICACIONES.keys())
        nueva_ubicacion = st.sidebar.selectbox(
            "Cambiar ubicación:",
            ubicaciones_disponibles,
            index=ubicaciones_disponibles.index(ubicacion_actual) if ubicacion_actual in ubicaciones_disponibles else 0
        )
        if nueva_ubicacion != ubicacion_actual:
            st.session_state.ubicacion_actual = nueva_ubicacion
            st.session_state.historia.append({
                "role": "system",
                "content": f"Dr. Watson: Holmes se mueve hacia {UBICACIONES[nueva_ubicacion]['nombre']}.",
                "tipo": "narrador",
                "autor": "Dr. Watson"
            })
            st.rerun()
        st.sidebar.markdown("---")
        
        # ========== SISTEMA DE CONFIANZA ==========
        st.sidebar.header("🤝 Confianza con Personajes")
        for personaje_id, confianza in st.session_state.confianza.items():
            if personaje_id in PERSONAJES:
                nombre = PERSONAJES[personaje_id]["nombre"]
                nivel = obtener_efecto_confianza(personaje_id, confianza)["nivel"]
                
                # Barra de progreso visual
                if nivel in ["muy_alta", "alta"]:
                    st.sidebar.success(f"**{nombre}**: {confianza}% ⭐")
                elif nivel == "media":
                    st.sidebar.info(f"**{nombre}**: {confianza}%")
                else:
                    st.sidebar.warning(f"**{nombre}**: {confianza}% ⚠️")
        st.sidebar.markdown("---")
        
        # Mostrar panel de personajes en el sidebar (con personaje actual grande y otros pequeños)
        mostrar_panel_personajes_sidebar()
        
        # Mostrar reputación de Holmes
        reputacion_actual = st.session_state.get("reputacion", 100)
        st.sidebar.header("⭐ Reputación de Holmes")
        if reputacion_actual >= 150:
            st.sidebar.success(f"🌟 Excelente: {reputacion_actual} puntos")
        elif reputacion_actual >= 100:
            st.sidebar.info(f"✨ Buena: {reputacion_actual} puntos")
        elif reputacion_actual >= 50:
            st.sidebar.warning(f"⚠️ Regular: {reputacion_actual} puntos")
        else:
            st.sidebar.error(f"❌ Baja: {reputacion_actual} puntos")
        st.sidebar.markdown("---")
        
        st.sidebar.header("📔 Cuaderno de pistas")
        if st.session_state.notas:
            for nota in st.session_state.notas:
                st.sidebar.markdown(f"• {nota}")
        else:
            st.sidebar.info("Aún no has descubierto pistas. Haz preguntas a los personajes.")
        
        # Mostrar pistas falsas descubiertas
        if st.session_state.pistas_falsas_descubiertas:
            st.sidebar.markdown("---")
            st.sidebar.header("⚠️ Pistas Falsas")
            st.sidebar.warning(f"Has encontrado {len(st.session_state.pistas_falsas_descubiertas)} pista(s) falsa(s). ¡Ten cuidado!")
        
        # Mostrar pistas ocultas descubiertas
        if st.session_state.pistas_ocultas_descubiertas:
            st.sidebar.markdown("---")
            st.sidebar.header("✨ Pistas Ocultas")
            st.sidebar.success(f"Has descubierto {len(st.session_state.pistas_ocultas_descubiertas)} pista(s) oculta(s).")
        
        st.sidebar.markdown("---")
        
        st.sidebar.header("⚙️ Configuración")
        if st.sidebar.button("Cambiar API Key"):
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            if "api_key" in st.session_state:
                del st.session_state.api_key
            st.rerun()
        
        # Información del juego
        with st.sidebar.expander("ℹ️ Sobre el juego"):
            st.markdown("""
            **Sherlock Mystery Game**
            
            Eres un detective investigando el asesinato de Lord Huxley.
            
            - Interroga a los personajes haciendo preguntas
            - Cambia de personaje cuando quieras
            - Las pistas se descubren automáticamente
            - Intenta resolver el caso con toda la información
            
            **Personajes:**
            - 🔍 Sherlock Holmes
            - 👤 Rose (camarera)
            - 👔 Arthur (sobrino)
            """)


if __name__ == "__main__":
    main()

