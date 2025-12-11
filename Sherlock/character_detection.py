"""Character detection and scene management for Sherlock Mystery Game"""

from config import PERSONAJES


# Mapeo de nombres y referencias a IDs de personajes
PERSONAJE_REFERENCIAS = {
    "sherlock": ["sherlock", "holmes", "detective", "sherlock holmes", "señor holmes", "mr. holmes", "sr. holmes", "holmes mismo", "yo mismo"],
    "rose": ["rose", "camarera", "sirvienta", "criada", "servidora", "la camarera", "la sirvienta", "la chica", "la muchacha", "la empleada", "miss rose"],
    "arthur": ["arthur", "arthur huxley", "sobrino", "el sobrino", "el sobrino arthur", "arthur mismo", "el sobrino de lord huxley", "young arthur"],
    "jenkins": ["jenkins", "mayordomo", "el mayordomo", "señor jenkins", "mr. jenkins", "jenkins mismo", "el mayordomo jenkins"]
}


def detectar_menciones_personajes(texto: str) -> list:
    """
    Detecta menciones de personajes en un texto.
    Excluye el personaje que habla (no se auto-menciona).
    
    Args:
        texto: Texto a analizar
    
    Returns:
        list: Lista de IDs de personajes mencionados (excluyendo auto-menciones)
    """
    texto_lower = texto.lower()
    # Limpiar texto de signos de puntuación para mejor matching
    import re
    texto_limpio = re.sub(r'[^\w\s]', ' ', texto_lower)
    texto_limpio = ' ' + texto_limpio + ' '  # Agregar espacios para word boundaries
    
    personajes_mencionados = []
    
    for personaje_id, referencias in PERSONAJE_REFERENCIAS.items():
        for ref in referencias:
            # Usar word boundaries para evitar matches parciales
            pattern = r'\b' + re.escape(ref.lower()) + r'\b'
            if re.search(pattern, texto_limpio):
                if personaje_id not in personajes_mencionados:
                    personajes_mencionados.append(personaje_id)
                break
    
    return personajes_mencionados


def inicializar_personajes_disponibles():
    """
    Inicializa la lista de personajes disponibles para hablar.
    Al inicio, NO hay interlocutores disponibles (Holmes es el protagonista).
    Los personajes aparecerán cuando se mencionen.
    """
    return set()  # Inicialmente vacío, se llena cuando se mencionan personajes



