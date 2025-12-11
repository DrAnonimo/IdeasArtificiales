"""Game logic and clue detection for Sherlock Mystery Game"""

from config import PISTAS, HECHOS_OBJETIVOS, PISTAS_FALSAS, PISTAS_OCULTAS, TIPOS_FINALES


def detectar_pista(texto: str, pistas_descubiertas: set) -> list:
    """
    Detecta si el texto contiene alguna pista nueva.
    Retorna lista de pistas encontradas.
    """
    nuevas_pistas = []
    texto_lower = texto.lower()
    
    for arr_pista in PISTAS:
        # Verificar si alguna palabra clave de la pista está en el texto
        if any(palabra in texto_lower for palabra in arr_pista):
            key = arr_pista[0]
            if key not in pistas_descubiertas:
                pistas_descubiertas.add(key)
                nuevas_pistas.append("/".join(arr_pista))
    
    return nuevas_pistas


def detectar_pista_falsa(texto: str, pistas_falsas_descubiertas: set) -> list:
    """
    Detecta si el texto contiene alguna pista falsa (red herring).
    Retorna lista de pistas falsas encontradas.
    """
    nuevas_pistas_falsas = []
    texto_lower = texto.lower()
    
    for pista_falsa in PISTAS_FALSAS:
        if pista_falsa["id"] not in pistas_falsas_descubiertas:
            # Verificar si alguna palabra clave está en el texto
            if any(palabra in texto_lower for palabra in pista_falsa["palabras_clave"]):
                pistas_falsas_descubiertas.add(pista_falsa["id"])
                nuevas_pistas_falsas.append({
                    "id": pista_falsa["id"],
                    "descripcion": pista_falsa["descripcion"],
                    "explicacion": pista_falsa["explicacion"]
                })
    
    return nuevas_pistas_falsas


def verificar_pista_oculta(pregunta: str, contexto: dict) -> dict:
    """
    Verifica si se cumplen los requisitos para revelar una pista oculta.
    
    Args:
        pregunta: La pregunta del jugador
        contexto: Dict con información del contexto (ubicación, personajes hablados, etc.)
    
    Returns:
        dict con información de la pista oculta si se cumple, None si no
    """
    pregunta_lower = pregunta.lower()
    
    for pista_oculta in PISTAS_OCULTAS:
        if pista_oculta["id"] in contexto.get("pistas_ocultas_descubiertas", set()):
            continue  # Ya descubierta
        
        # Verificar palabras clave
        tiene_palabras_clave = any(palabra in pregunta_lower for palabra in pista_oculta["palabras_clave"])
        
        if not tiene_palabras_clave:
            continue
        
        # Verificar requisitos
        requisitos_cumplidos = True
        for requisito in pista_oculta["requisitos"]:
            if requisito == "hablar_con_jenkins":
                if "jenkins" not in contexto.get("personajes_hablados", []):
                    requisitos_cumplidos = False
            elif requisito == "insistir_correspondencia":
                if not contexto.get("correspondencia_insistida", False):
                    requisitos_cumplidos = False
            elif requisito == "examinar_estudio":
                if contexto.get("ubicacion_actual") != "estudio":
                    requisitos_cumplidos = False
            elif requisito == "preguntar_reloj":
                if "reloj" not in pregunta_lower:
                    requisitos_cumplidos = False
            elif requisito == "examinar_ventana":
                if "ventana" not in pregunta_lower and contexto.get("ubicacion_actual") != "estudio":
                    requisitos_cumplidos = False
            elif requisito == "preguntar_huellas":
                if "huella" not in pregunta_lower and "barro" not in pregunta_lower:
                    requisitos_cumplidos = False
        
        if requisitos_cumplidos:
            return {
                "id": pista_oculta["id"],
                "descripcion": pista_oculta["descripcion"]
            }
    
    return None


def determinar_tipo_final(culpable: str, arma: str, motivo: str, 
                           secretos_descubiertos: list) -> dict:
    """
    Determina el tipo de final basándose en la solución y secretos descubiertos.
    
    Returns:
        dict con información del final
    """
    hechos = HECHOS_OBJETIVOS
    
    culpable_lower = culpable.lower().strip()
    arma_lower = arma.lower().strip()
    motivo_lower = motivo.lower().strip()
    
    # Validar elementos básicos
    ok_culpable = (culpable_lower == hechos["culpable"]["id"].lower() or 
                   culpable_lower == hechos["culpable"]["nombre"].lower())
    ok_arma = (arma_lower == hechos["culpable"]["arma_usada"].lower() or 
               arma_lower in hechos["escena_del_crimen"]["arma"].lower())
    ok_motivo = ("herencia" in motivo_lower or 
                 motivo_lower in hechos["culpable"]["motivo"].lower())
    
    # Determinar tipo de final
    if not ok_culpable:
        tipo_final = "incorrecto"
    elif ok_culpable and ok_arma and ok_motivo:
        # Verificar secretos descubiertos
        secretos_requeridos = ["robo_rose", "relacion_rose_lord"]
        secretos_encontrados = sum(1 for s in secretos_requeridos if s in secretos_descubiertos)
        
        if secretos_encontrados == len(secretos_requeridos):
            tipo_final = "perfecto"
        elif secretos_encontrados > 0:
            tipo_final = "bueno"
        else:
            tipo_final = "bueno"  # Resolvió el crimen pero sin secretos
    elif ok_culpable and (ok_arma or ok_motivo):
        tipo_final = "parcial"
    else:
        tipo_final = "incorrecto"
    
    final_info = TIPOS_FINALES[tipo_final].copy()
    final_info["tipo"] = tipo_final
    
    return final_info


def validar_solucion(culpable: str, arma: str, motivo: str, solucion: dict, 
                     secretos_descubiertos: list = None) -> tuple:
    """
    Valida si la solución propuesta es correcta usando HECHOS_OBJETIVOS.
    Retorna (es_correcta, titulo, mensaje_detallado)
    """
    # Validar usando HECHOS_OBJETIVOS
    hechos = HECHOS_OBJETIVOS
    
    culpable_lower = culpable.lower().strip()
    arma_lower = arma.lower().strip()
    motivo_lower = motivo.lower().strip()
    
    # Validar culpable
    culpable_correcto_id = hechos["culpable"]["id"].lower()
    ok_culpable = culpable_lower == culpable_correcto_id or culpable_lower == hechos["culpable"]["nombre"].lower()
    
    # Validar arma
    arma_correcta = hechos["culpable"]["arma_usada"].lower()
    ok_arma = arma_lower == arma_correcta or arma_lower in hechos["escena_del_crimen"]["arma"].lower()
    
    # Validar motivo
    motivo_correcto = hechos["culpable"]["motivo"].lower()
    # Buscar palabras clave del motivo (herencia, desheredar, etc.)
    ok_motivo = (motivo_lower in motivo_correcto or 
                 motivo_correcto.split()[0] in motivo_lower or
                 "herencia" in motivo_lower)
    
    es_correcta = ok_culpable and ok_arma and ok_motivo
    
    # Determinar tipo de final
    if secretos_descubiertos is None:
        secretos_descubiertos = []
    
    final_info = determinar_tipo_final(culpable, arma, motivo, secretos_descubiertos)
    
    if es_correcta:
        titulo = f"¡Caso resuelto! - {final_info['nombre']}"
        culpable_nombre = hechos["culpable"]["nombre"]
        arma_nombre = hechos["culpable"]["arma_usada"]
        motivo_nombre = hechos["culpable"]["motivo"].split("(")[0].strip()
        modus = hechos["culpable"]["modus_operandi"]
        
        mensaje = f"""¡Enhorabuena, caso resuelto!

{culpable_nombre} mató a Lord Huxley con una {arma_nombre} por {motivo_nombre}.

{modus}

{final_info['descripcion']}

Has demostrado ser un detective excepcional, Holmes."""
    else:
        titulo = f"Solución incorrecta - {final_info['nombre']}"
        feedback = []
        
        if not ok_culpable:
            feedback.append(f"❌ Culpable incorrecto. No es {culpable.title()}.")
        if not ok_arma:
            feedback.append(f"❌ Arma incorrecta. No fue {arma.title()}.")
        if not ok_motivo:
            feedback.append(f"❌ Motivo incorrecto. No fue por {motivo.title()}.")
        
        feedback.append(f"\n{final_info['descripcion']}")
        feedback.append("\n💡 Consejo: Revisa las pistas descubiertas y los testimonios de los sospechosos.")
        mensaje = "\n".join(feedback)
    
    return es_correcta, titulo, mensaje, final_info


def validar_teoria_completa(teoria: dict) -> dict:
    """
    Valida una teoría completa del jugador con detalles adicionales.
    
    Args:
        teoria: dict con campos opcionales:
            - culpable (requerido)
            - arma (requerido)
            - motivo (requerido)
            - hora_crimen (opcional)
            - lugar_crimen (opcional)
            - modus_operandi (opcional)
    
    Returns:
        dict con:
            - es_correcta: bool
            - puntuacion: float (0-1)
            - feedback: dict con detalles de validación
            - mensaje: str con mensaje formateado
    """
    hechos = HECHOS_OBJETIVOS
    feedback = {
        "culpable": {"correcto": False, "detalles": ""},
        "arma": {"correcto": False, "detalles": ""},
        "motivo": {"correcto": False, "detalles": ""},
        "hora_crimen": {"correcto": False, "detalles": ""},
        "lugar_crimen": {"correcto": False, "detalles": ""},
        "modus_operandi": {"correcto": False, "detalles": ""},
    }
    
    # Validar culpable
    culpable_teoria = teoria.get("culpable", "").lower().strip()
    culpable_real = hechos["culpable"]["id"].lower()
    feedback["culpable"]["correcto"] = (culpable_teoria == culpable_real or 
                                        culpable_teoria == hechos["culpable"]["nombre"].lower())
    
    # Validar arma
    arma_teoria = teoria.get("arma", "").lower().strip()
    arma_real = hechos["culpable"]["arma_usada"].lower()
    feedback["arma"]["correcto"] = arma_teoria == arma_real
    
    # Validar motivo
    motivo_teoria = teoria.get("motivo", "").lower().strip()
    motivo_real = hechos["culpable"]["motivo"].lower()
    feedback["motivo"]["correcto"] = ("herencia" in motivo_teoria or 
                                       motivo_teoria in motivo_real)
    
    # Validar hora (opcional)
    if "hora_crimen" in teoria:
        hora_teoria = teoria["hora_crimen"].lower()
        hora_real = hechos["cronologia"]["00:00_aprox"]
        # Buscar referencias a medianoche, 00:00, etc.
        feedback["hora_crimen"]["correcto"] = any(
            palabra in hora_teoria for palabra in ["00:00", "medianoche", "media noche", "media noche"]
        )
    
    # Validar lugar (opcional)
    if "lugar_crimen" in teoria:
        lugar_teoria = teoria["lugar_crimen"].lower()
        lugar_real = hechos["victima"]["lugar_muerte"].lower()
        feedback["lugar_crimen"]["correcto"] = any(
            palabra in lugar_teoria for palabra in lugar_real.split("/")
        )
    
    # Validar modus operandi (opcional, usando similitud de palabras clave)
    if "modus_operandi" in teoria:
        modus_teoria = teoria["modus_operandi"].lower()
        modus_real = hechos["culpable"]["modus_operandi"].lower()
        palabras_clave = ["ventana", "00:10", "club", "daga"]
        palabras_encontradas = sum(1 for palabra in palabras_clave if palabra in modus_teoria)
        feedback["modus_operandi"]["correcto"] = palabras_encontradas >= 2
    
    # Calcular puntuación
    elementos_validados = sum(1 for v in feedback.values() if v["correcto"])
    elementos_totales = sum(1 for k in feedback.keys() if teoria.get(k) is not None)
    puntuacion = elementos_validados / elementos_totales if elementos_totales > 0 else 0.0
    
    es_correcta = (feedback["culpable"]["correcto"] and 
                   feedback["arma"]["correcto"] and 
                   feedback["motivo"]["correcto"])
    
    # Generar mensaje de feedback
    mensaje_parts = []
    if es_correcta:
        mensaje_parts.append("✅ ¡Teoría correcta!")
    else:
        mensaje_parts.append("❌ Teoría incorrecta o incompleta.")
    
    mensaje_parts.append(f"\n📊 Puntuación: {puntuacion*100:.0f}%")
    
    return {
        "es_correcta": es_correcta,
        "puntuacion": puntuacion,
        "feedback": feedback,
        "mensaje": "\n".join(mensaje_parts)
    }


def obtener_informacion_caso() -> dict:
    """
    Retorna información completa del caso desde HECHOS_OBJETIVOS.
    Útil para generar pistas o ayuda.
    """
    return HECHOS_OBJETIVOS.copy()


def generar_mensaje_lestrade(es_correcta: bool, reputacion_anterior: int, reputacion_nueva: int) -> str:
    """
    Genera el mensaje del Inspector Lestrade según si la solución es correcta o no.
    
    Args:
        es_correcta: Si la solución propuesta es correcta
        reputacion_anterior: Reputación antes de resolver
        reputacion_nueva: Reputación después de resolver
    
    Returns:
        str: Mensaje de Lestrade
    """
    if es_correcta:
        mensajes_correctos = [
            f"¡Excelente trabajo, Holmes! Debo admitir que has superado todas mis expectativas una vez más. El Inspector Lestrade de Scotland Yard reconoce tu genialidad en este caso.",
            f"Holmes, mi más sincera felicitación. Has demostrado una vez más por qué eres considerado el mejor detective de Londres. Lestrade te saluda con respeto.",
            f"¡Impresionante, Holmes! Como Inspector Lestrade de Scotland Yard, debo reconocer tu extraordinaria habilidad para resolver este complejo caso. ¡Brillante!",
            f"Holmes, has vuelto a sorprenderme. A pesar de nuestra... competencia, debo reconocer tu destreza. Lestrade te felicita sinceramente por este caso resuelto."
        ]
        import random
        mensaje_base = random.choice(mensajes_correctos)
        return mensaje_base
    else:
        # Calcular cuánta reputación se perdió
        reputacion_perdida = reputacion_anterior - reputacion_nueva
        
        mensajes_incorrectos = [
            f"Lestrade frunce el ceño y cruza los brazos: 'Holmes, me temo que te has equivocado en este caso. Esperaba más de ti. Tu reputación ha sufrido con este error. Scotland Yard necesita detectives confiables.'",
            f"El Inspector Lestrade te mira con desaprobación: 'Holmes, he oído de tu fracaso en este caso. A pesar de tu reputación, has cometido un error grave. Esto no será fácil de olvidar.'",
            f"Lestrade sacude la cabeza con decepción: 'Holmes, creí que tenías este caso resuelto. Tu solución incorrecta ha manchado tu reputación. Scotland Yard esperaba mejor de ti.'"
        ]
        import random
        mensaje_base = random.choice(mensajes_incorrectos)
        
        if reputacion_perdida > 0:
            mensaje_base += f"\n\nTu reputación ha disminuido en {reputacion_perdida} puntos (de {reputacion_anterior} a {reputacion_nueva})."
        
        return mensaje_base


def calcular_reputacion(es_correcta: bool, reputacion_actual: int, 
                        tipo_final: str = None) -> tuple:
    """
    Calcula la nueva reputación basándose en si la solución es correcta y el tipo de final.
    
    Args:
        es_correcta: Si la solución propuesta es correcta
        reputacion_actual: Reputación actual de Sherlock
        tipo_final: Tipo de final alcanzado (perfecto, bueno, parcial, incorrecto)
    
    Returns:
        tuple: (reputacion_nueva, puntos_cambiados)
    """
    if es_correcta and tipo_final:
        # Bonus según tipo de final
        bonus = TIPOS_FINALES.get(tipo_final, {}).get("bonus_reputacion", 20)
        nueva_reputacion = min(reputacion_actual + bonus, 200)  # Máximo 200
        return nueva_reputacion, bonus
    elif es_correcta:
        # Ganar reputación por resolver correctamente (fallback)
        puntos_ganados = 20
        nueva_reputacion = min(reputacion_actual + puntos_ganados, 200)
        return nueva_reputacion, puntos_ganados
    else:
        # Perder reputación por resolver incorrectamente
        puntos_perdidos = 15
        nueva_reputacion = max(reputacion_actual - puntos_perdidos, 0)  # Mínimo 0
        return nueva_reputacion, -puntos_perdidos

