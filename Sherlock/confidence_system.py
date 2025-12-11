"""Sistema de confianza/relación con personajes"""

from typing import Dict
from config import PERSONAJES

# Niveles de confianza iniciales
CONFIANZA_INICIAL = {
    "rose": 50,      # Neutral
    "arthur": 30,    # Bajo (es el culpable, es defensivo)
    "jenkins": 60    # Alto (profesional, respetuoso)
}

# Palabras clave que afectan la confianza
PALABRAS_AGRESIVAS = [
    "culpable", "asesino", "mentiroso", "mentiras", "mientes", "engaño",
    "arrestar", "prisión", "evidencia", "confesión", "confiesa", "delito"
]

PALABRAS_EMPATICAS = [
    "comprender", "entender", "ayudar", "apoyar", "confiar", "creer",
    "difícil", "situación", "lo siento", "lamento", "respeto"
]

# Cambios de confianza según tipo de pregunta
CAMBIO_CONFIANZA = {
    "agresiva": -10,
    "empatica": +5,
    "neutral": 0,
    "confianza_alta_revelacion": +15  # Bonus por revelar información con alta confianza
}

# Niveles de confianza y sus efectos
NIVELES_CONFIANZA = {
    "muy_alta": (80, 100),  # Revela información muy sensible
    "alta": (60, 79),       # Revela información sensible
    "media": (40, 59),      # Información normal
    "baja": (20, 39),       # Información limitada, defensivo
    "muy_baja": (0, 19)     # Muy defensivo, puede mentir
}


def inicializar_confianza() -> Dict[str, int]:
    """Inicializa el sistema de confianza para todos los personajes"""
    return CONFIANZA_INICIAL.copy()


def analizar_tono_pregunta(pregunta: str) -> str:
    """
    Analiza el tono de una pregunta para determinar su impacto en la confianza.
    
    Returns:
        "agresiva", "empatica", o "neutral"
    """
    pregunta_lower = pregunta.lower()
    
    palabras_agresivas_encontradas = sum(1 for palabra in PALABRAS_AGRESIVAS if palabra in pregunta_lower)
    palabras_empaticas_encontradas = sum(1 for palabra in PALABRAS_EMPATICAS if palabra in pregunta_lower)
    
    if palabras_agresivas_encontradas > palabras_empaticas_encontradas:
        return "agresiva"
    elif palabras_empaticas_encontradas > 0:
        return "empatica"
    else:
        return "neutral"


def actualizar_confianza(personaje_id: str, confianza_actual: Dict[str, int], 
                        tono_pregunta: str) -> tuple:
    """
    Actualiza la confianza de un personaje basándose en el tono de la pregunta.
    
    Returns:
        (nueva_confianza, cambio_aplicado)
    """
    if personaje_id not in confianza_actual:
        confianza_actual[personaje_id] = CONFIANZA_INICIAL.get(personaje_id, 50)
    
    cambio = CAMBIO_CONFIANZA.get(tono_pregunta, 0)
    nueva_confianza = max(0, min(100, confianza_actual[personaje_id] + cambio))
    
    cambio_aplicado = nueva_confianza - confianza_actual[personaje_id]
    confianza_actual[personaje_id] = nueva_confianza
    
    return nueva_confianza, cambio_aplicado


def obtener_nivel_confianza(confianza: int) -> str:
    """Obtiene el nivel de confianza basado en el valor numérico"""
    for nivel, (min_val, max_val) in NIVELES_CONFIANZA.items():
        if min_val <= confianza <= max_val:
            return nivel
    return "media"


def obtener_efecto_confianza(personaje_id: str, confianza: int) -> Dict[str, any]:
    """
    Obtiene los efectos de la confianza actual en las respuestas del personaje.
    
    Returns:
        dict con información sobre cómo afecta la confianza
    """
    nivel = obtener_nivel_confianza(confianza)
    
    efectos = {
        "nivel": nivel,
        "cooperacion": "alta" if nivel in ["muy_alta", "alta"] else "normal" if nivel == "media" else "baja",
        "revela_secretos": nivel in ["muy_alta", "alta"],
        "defensivo": nivel in ["baja", "muy_baja"],
        "puede_mentir": nivel == "muy_baja"
    }
    
    return efectos


def generar_mensaje_confianza(personaje_id: str, confianza: int, cambio: int) -> str:
    """
    Genera un mensaje de Watson sobre el cambio en la confianza.
    """
    if abs(cambio) < 3:  # Cambios muy pequeños no se mencionan
        return None
    
    personaje = PERSONAJES.get(personaje_id, {}).get("nombre", "el personaje")
    nivel = obtener_nivel_confianza(confianza)
    
    if cambio > 0:
        mensajes = [
            f"Watson nota: {personaje} parece más abierto y confiado tras tu pregunta empática.",
            f"Watson observa: {personaje} muestra más disposición a cooperar.",
            f"Watson anota: La confianza con {personaje} ha mejorado."
        ]
    else:
        mensajes = [
            f"Watson nota: {personaje} se muestra más defensivo tras tu pregunta agresiva.",
            f"Watson observa: {personaje} parece menos cooperativo ahora.",
            f"Watson anota: La relación con {personaje} se ha tensado."
        ]
    
    import random
    return random.choice(mensajes)

