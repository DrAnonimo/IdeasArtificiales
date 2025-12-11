"""Watson narrator system for Sherlock Mystery Game"""

import random
from config import PERSONAJES


WATSON_PROMPT = """Eres el Doctor John H. Watson, narrador y compañero de Sherlock Holmes en Londres 1895. Escribes en primera persona como observador médico y cronista de los casos. Tu estilo es profesional pero accesible, con observaciones médicas precisas y descripciones vivas. Tienes admiración por Holmes pero también notas humanas. 50-80 palabras máximo, tono victoriano formal."""

CASO_INICIAL = """Observé con detenimiento médico la escena del crimen. Lord Huxley yacía en el suelo de la biblioteca, boca arriba. El cuerpo mostraba una herida penetrante en el tórax izquierdo, entre la cuarta y quinta costilla, con bordes limpios que sugerían un arma afilada. La sangre había dejado de fluir hacía tiempo, la rigidez cadavérica ya había comenzado. La temperatura corporal indicaba que el fallecimiento había ocurrido varias horas atrás. La biblioteca permanecía cerrada por dentro, pero la ventana entreabierta permitía el paso de una brisa fría que movía las cortinas. Holmes ya había comenzado su inspección metódica."""

COMENTARIOS_WATSON = [
    "Anoté mentalmente este detalle. La observación de Holmes era, como siempre, perspicaz.",
    "Holmes movió su mirada analítica. El detalle mencionado podría ser significativo.",
    "Como médico, noté que la información revelada conectaba con los hallazgos anatómicos del cadáver.",
    "Holmes asintió levemente. Esta pista encajaba con su teoría inicial.",
    "Registré cuidadosamente esta declaración. Podría ser crucial para el caso.",
    "La expresión de Holmes denotaba interés. Esta información era nueva.",
    "Observé que Holmes tomaba nota mental. El testimonio era relevante.",
]


def obtener_comentario_watson(probabilidad=0.3):
    """
    Obtiene un comentario ocasional de Watson basado en probabilidad.
    
    Args:
        probabilidad: Probabilidad de que Watson comente (0.0 a 1.0)
    
    Returns:
        str o None: Comentario de Watson o None si no comenta
    """
    if random.random() < probabilidad:
        return random.choice(COMENTARIOS_WATSON)
    return None


def generar_descripcion_inicial():
    """Genera la descripción inicial del caso por Watson"""
    return CASO_INICIAL


def detectar_mencion_correspondencia(texto: str) -> bool:
    """
    Detecta si el texto menciona la correspondencia secreta de Lord Huxley.
    
    Args:
        texto: Texto a analizar
    
    Returns:
        bool: True si se menciona la correspondencia secreta
    """
    texto_lower = texto.lower()
    palabras_clave = [
        "correspondencia",
        "correspondencia secreta",
        "correspondencia personal",
        "correspondencia privada",
        "cartas",
        "cartas secretas",
        "cartas de lord huxley",
        "correspondencia de lord huxley",
        "donde lord huxley oculta",
        "donde oculta la correspondencia",
        "donde guarda la correspondencia",
        "donde está la correspondencia",
        "donde están las cartas",
        "correspondencia más privada"
    ]
    
    return any(palabra in texto_lower for palabra in palabras_clave)


def generar_cartas_random() -> list:
    """
    Genera cartas aleatorias con contenido victoriano genérico.
    
    Returns:
        list: Lista de cartas (dict con fecha, remitente, destinatario, contenido)
    """
    cartas = [
        {
            "fecha": "15 de marzo de 1894",
            "remitente": "Lady Margaret Ashworth",
            "destinatario": "Lord Huxley",
            "contenido": """Estimado Lord Huxley,

Espero que esta carta le encuentre en buena salud. He tenido el placer de leer sobre sus últimas adquisiciones de arte y me gustaría expresarle mi más sincera admiración por su buen gusto.

Me encantaría visitarle en su próxima reunión en el club. Quedo a la espera de su respuesta.

Con mis mejores deseos,
Lady Margaret Ashworth"""
        },
        {
            "fecha": "2 de julio de 1894",
            "remitente": "Sir Reginald Thornfield",
            "destinatario": "Lord Huxley",
            "contenido": """Mi querido Huxley,

He recibido con agrado tu invitación para la cacería del próximo mes. Los terrenos de tu finca son excepcionales y espero con ansias el evento.

Por favor, confirma la fecha final para que pueda organizar mi agenda en consecuencia.

Atentamente,
Sir Reginald Thornfield"""
        },
        {
            "fecha": "10 de noviembre de 1894",
            "remitente": "Dr. Alistair Croft",
            "destinatario": "Lord Huxley",
            "contenido": """Estimado Lord Huxley,

Le escribo en relación a su última consulta médica. Los resultados de los análisis han sido positivos y no hay motivo de preocupación.

Sin embargo, le recomiendo mantener una dieta más equilibrada y reducir el consumo de brandy. Su salud es primordial.

Con respeto médico,
Dr. Alistair Croft"""
        },
        {
            "fecha": "20 de enero de 1895",
            "remitente": "Madame Elise Dubois",
            "destinatario": "Lord Huxley",
            "contenido": """Cher Lord Huxley,

J'espère que vous vous portez bien. Votre dernière visite à Paris fut un plaisir absolu.

Les documents que vous m'avez confiés sont en sécurité. Vous pouvez compter sur ma discrétion absolue en cette affaire.

Avec toute mon amitié,
Madame Elise Dubois"""
        },
        {
            "fecha": "5 de febrero de 1895",
            "remitente": "Banco de Inglaterra",
            "destinatario": "Lord Huxley",
            "contenido": """Estimado Lord Huxley,

Confirmamos la recepción de su solicitud de transferencia de fondos. Los documentos están siendo procesados y le informaremos en breve sobre el estado de la operación.

Por favor, mantenga la confidencialidad de este asunto como indicó en su comunicación anterior.

Atentamente,
Harold P. Williams, Director de Operaciones"""
        }
    ]
    
    # Seleccionar 2-3 cartas aleatorias
    import random
    return random.sample(cartas, random.randint(2, 3))


def obtener_carta_secreta_herencia() -> dict:
    """
    Retorna la carta secreta entre Lord Huxley y su abogado sobre la herencia.
    
    Returns:
        dict: Carta con fecha, remitente, destinatario, contenido
    """
    return {
        "fecha": "25 de febrero de 1895",
        "remitente": "Lord Huxley",
        "destinatario": "Sr. Charles Whitmore, Abogado",
        "contenido": """Mi estimado Whitmore,

Le escribo con la máxima urgencia y confidencialidad sobre un asunto de la mayor importancia: mi testamento y la disposición de mi herencia.

He tomado una decisión irrevocable que debo formalizar de inmediato. Deseo que se proceda a la MODIFICACIÓN COMPLETA de mi testamento actual.

INSTRUCCIONES ESPECÍFICAS:

1. Mi sobrino Arthur Huxley debe ser COMPLETAMENTE EXCLUIDO de mi herencia. No recibirá ni un penique de mi fortuna. Su comportamiento despreocupado y su falta de respeto hacia nuestra familia han sido la gota que colmó el vaso.

2. Toda mi herencia, sin excepción, debe pasar a disposición de Rose, mi hija legítima, aunque no reconocida públicamente hasta ahora.

3. Rose debe recibir no solo la fortuna, sino también todos los títulos, propiedades y posesiones que me corresponden.

Esta decisión no es caprichosa. He descubierto verdades sobre mi familia que me obligan a actuar así. Arthur no es digno del legado de los Huxley, mientras que Rose ha demostrado, a pesar de todo, ser la verdadera heredera de nuestros valores.

Le ruego que prepare la documentación necesaria de forma discreta y urgente. Espero su confirmación para reunirnos esta semana y formalizar estos cambios ante notario.

Mantenga este asunto en absoluto secreto. Nadie debe saber de estos cambios hasta que yo lo autorice.

Su leal servidor,
Lord Edward Huxley"""
    }


def detectar_peticion_resumen(texto: str) -> bool:
    """
    Detecta si el texto es una petición de resumen a Watson.
    
    Args:
        texto: Texto a analizar
    
    Returns:
        bool: True si se solicita un resumen
    """
    texto_lower = texto.lower().strip()
    peticiones = [
        "resumen",
        "resume",
        "resúmen",
        "haz un resumen",
        "hazme un resumen",
        "dame un resumen",
        "qué hemos descubierto",
        "que hemos descubierto",
        "qué hemos encontrado",
        "que hemos encontrado",
        "qué sabemos",
        "que sabemos",
        "resumen del caso",
        "resumen del crimen",
        "resumen watson",
        "watson resumen",
        "watson, resumen",
        "watson haz un resumen",
        "qué pistas tenemos",
        "que pistas tenemos",
        "resume el caso",
        "resume lo que sabemos"
    ]
    
    return any(peticion in texto_lower for peticion in peticiones)


def generar_resumen_caso(historial: list, pistas_descubiertas: set, notas: list) -> str:
    """
    Genera un resumen del caso desde la perspectiva de Watson basado en el historial.
    
    Args:
        historial: Lista de mensajes de la conversación
        pistas_descubiertas: Set de pistas descubiertas
        notas: Lista de notas/pistas anotadas
    
    Returns:
        str: Resumen del caso en estilo de Watson
    """
    # Extraer información relevante del historial
    testimonios = []
    personajes_interrogados = set()
    detalles_importantes = []
    correspondencia_leida = False
    
    for msg in historial:
        tipo = msg.get("tipo", "")
        contenido = msg.get("content", "")
        personaje = msg.get("personaje", "")
        autor = msg.get("autor", "")
        
        # Recopilar testimonios de personajes (últimos y más relevantes)
        if tipo == "npc" and personaje:
            personajes_interrogados.add(personaje)
            if len(contenido) > 15:  # Solo testimonios sustanciales
                # Limpiar el contenido para el resumen
                contenido_limpio = contenido.strip()
                if len(contenido_limpio) > 120:
                    contenido_limpio = contenido_limpio[:120] + "..."
                testimonios.append(f"{personaje}: \"{contenido_limpio}\"")
        
        # Recopilar observaciones importantes de Watson
        if tipo == "narrador" and "Watson" in autor:
            if any(palabra in contenido.lower() for palabra in ["observa", "nota", "descubre", "encuentra"]):
                detalles_importantes.append(contenido)
        
        # Detectar si se leyó la correspondencia
        if "correspondencia" in contenido.lower() or "cartas" in contenido.lower():
            if "Watson" in autor or "Inspector" in autor:
                correspondencia_leida = True
    
    # Construir el resumen
    resumen = "Watson toma su cuaderno y comienza a leer sus anotaciones:\n\n"
    resumen += "📋 RESUMEN DEL CASO - Anotaciones del Dr. Watson\n"
    resumen += "=" * 60 + "\n\n"
    
    # Personajes interrogados
    if personajes_interrogados:
        resumen += "👥 PERSONAJES INTERROGADOS:\n"
        for personaje in sorted(personajes_interrogados):
            resumen += f"  • {personaje}\n"
        resumen += "\n"
    else:
        resumen += "👥 PERSONAJES INTERROGADOS:\n"
        resumen += "  • Ninguno aún\n\n"
    
    # Pistas descubiertas
    if pistas_descubiertas or notas:
        resumen += "🔍 PISTAS Y DESCUBRIMIENTOS:\n"
        if notas:
            for nota in notas:
                resumen += f"  • {nota}\n"
        if pistas_descubiertas:
            for pista in sorted(pistas_descubiertas):
                resumen += f"  • {pista}\n"
        resumen += "\n"
    else:
        resumen += "🔍 PISTAS Y DESCUBRIMIENTOS:\n"
        resumen += "  • Aún no se han descubierto pistas\n\n"
    
    # Testimonios clave (máximo 3-4, los más recientes)
    if testimonios:
        resumen += "💬 TESTIMONIOS CLAVE:\n"
        # Tomar los últimos testimonios (más relevantes)
        for testimonio in testimonios[-4:]:
            resumen += f"  {testimonio}\n"
        resumen += "\n"
    
    # Correspondencia
    if correspondencia_leida:
        resumen += "📜 CORRESPONDENCIA:\n"
        resumen += "  • Se ha encontrado y leído la correspondencia secreta de Lord Huxley\n"
        resumen += "  • Se descubrió la carta sobre el cambio de herencia\n\n"
    
    # Observaciones importantes
    if detalles_importantes:
        resumen += "📝 OBSERVACIONES IMPORTANTES:\n"
        for detalle in detalles_importantes[-3:]:  # Últimas 3 observaciones
            resumen += f"  • {detalle}\n"
        resumen += "\n"
    
    # Conclusión
    resumen += "─" * 60 + "\n"
    resumen += "Watson cierra su cuaderno y mira a Holmes: "
    
    total_info = len(personajes_interrogados) + len(pistas_descubiertas) + len(notas)
    
    if total_info == 0:
        resumen += "'Holmes, aún no hemos interrogado a nadie ni descubierto pistas. Deberíamos comenzar la investigación mencionando a los testigos disponibles.'"
    elif total_info < 3:
        resumen += "'Holmes, hemos comenzado a recopilar información, pero aún necesitamos interrogar a más testigos y descubrir más pistas para tener una imagen completa del caso.'"
    elif total_info < 6:
        resumen += "'Holmes, hemos avanzado en la investigación. Hemos hablado con varios testigos y descubierto algunas pistas, pero aún faltan detalles cruciales para resolver este misterio.'"
    elif correspondencia_leida:
        resumen += "'Holmes, hemos recopilado información sustancial, incluyendo la correspondencia secreta. Con todas las pistas descubiertas y los testimonios recogidos, creo que tenemos suficiente información para resolver este caso. ¿Qué opinas?'"
    else:
        resumen += "'Holmes, hemos recopilado información sustancial. Con las pistas descubiertas y los testimonios recogidos, creo que estamos cerca de resolver este caso. ¿Qué opinas?'"
    
    return resumen


def generar_intervencion_correspondencia() -> str:
    """
    Genera la intervención completa de Watson leyendo las cartas.
    
    Returns:
        str: Texto completo de la intervención de Watson con todas las cartas
    """
    cartas_random = generar_cartas_random()
    carta_secreta = obtener_carta_secreta_herencia()
    
    texto = "Watson se acerca al escritorio y, tras examinar el cajón secreto que Jenkins había indicado, encuentra un paquete de correspondencia personal. Abriendo con cuidado los sobres, comienza a leer algunas cartas en voz alta:\n\n"
    
    # Leer cartas aleatorias primero
    for i, carta in enumerate(cartas_random, 1):
        texto += f"--- CARTA {i} ---\n"
        texto += f"Fecha: {carta['fecha']}\n"
        texto += f"De: {carta['remitente']}\n"
        texto += f"Para: {carta['destinatario']}\n\n"
        texto += f"{carta['contenido']}\n\n"
    
    # Luego la carta secreta importante
    texto += "--- CARTA SECRETA ---\n"
    texto += f"Fecha: {carta_secreta['fecha']}\n"
    texto += f"De: {carta_secreta['remitente']}\n"
    texto += f"Para: {carta_secreta['destinatario']}\n\n"
    texto += f"{carta_secreta['contenido']}\n\n"
    
    texto += "Watson alza la mirada hacia Holmes con expresión de asombro: 'Holmes, esto cambia todo. Lord Huxley planeaba desheredar completamente a Arthur y dejar toda su fortuna a Rose. Si Arthur se enteró de esto...'"
    
    return texto

