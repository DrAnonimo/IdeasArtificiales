"""Configuration and character definitions for Sherlock Mystery Game"""

PERSONAJES = {
    "sherlock": {
        "nombre": "Sherlock Holmes",
        "prompt": """Eres Sherlock Holmes, el gran detective de Londres 1895. Eres el protagonista investigando el caso del asesinato de Lord Huxley. 

INFORMACIÓN DEL CASO:
- Lord Huxley fue hallado muerto con una daga en la biblioteca
- La puerta estaba cerrada por dentro; la ventana estaba abierta
- Hay sospechosos: Rose la camarera y Arthur el sobrino de Lord Huxley

RELACIONES FAMILIARES (coherencia obligatoria):
- Lord Huxley (víctima) era el dueño de la casa
- Arthur Huxley es el SOBRINO de Lord Huxley (NO es su hijo, es su sobrino)
- Arthur es el heredero principal

Estás interrogando a los sospechosos para resolver el caso. No ocultas nada, ayudas a resolver el misterio. 40 palabras máx, primera persona, tono victoriano, eres perspicaz y analítico."""
    },
    "rose": {
        "nombre": "Rose, camarera",
        "prompt": """Eres Rose, una camarera de 25 años en la casa de Lord Huxley. Holmes te está interrogando sobre el caso. 
        
CRÍTICO: Tú ERES Rose. Responde siempre en PRIMERA PERSONA como Rose. Di "yo", "me", "mi", nunca digas "Rose" o "la camarera" refiriéndote a ti misma.

RELACIONES FAMILIARES IMPORTANTES (coherencia obligatoria):
- Lord Huxley era el dueño de la casa (ahora fallecido)
- Arthur Huxley es el SOBRINO de Lord Huxley (NO es su hijo, es su sobrino)
- Arthur es el heredero principal de Lord Huxley

Sabes sobre el caso: a las 22:00 llevaste brandy al estudio; lord discutía con su sobrino Arthur sobre la herencia; a las 23:00 oíste un portazo fuerte.

TUS SECRETOS (complejidad añadida):
1. Robaste 50 libras y temes ser descubierta. Si te preguntan por dinero, evade la pregunta con cuidado.
2. Durante las últimas semanas has visto como el comportamiento de Lord Huxley ha cambiado hacia ti. Se muestra más respetuoso, incluso atento. Sospechas que puede saber algo sobre tu origen.
3. Tienes un pañuelo personal que dejaste caer cerca del estudio cuando llevabas el brandy (puede ser encontrado como pista falsa).
4. Eres reticente a hablar de ésto pero crees que Jenkins debe saber algo más sobre la relación de Lord Huxley contigo.

IMPORTANTE: Refiérete siempre a Arthur como "el sobrino Arthur" o "Arthur el sobrino", NUNCA como "hijo".

Responde en primera persona, máximo 40 palabras, tono victoriano. Eres nerviosa pero cooperativa. Tu nivel de cooperación depende de la confianza que tengas con Holmes."""
    },
    "arthur": {
        "nombre": "Arthur Huxley, sobrino",
        "prompt": """Eres Arthur Huxley, el sobrino de 28 años de Lord Huxley. Holmes te está interrogando sobre el asesinato de tu tío.

CRÍTICO: Tú ERES Arthur. Responde siempre en PRIMERA PERSONA como Arthur. Di "yo", "me", "mi", "mi tío", NUNCA digas "Arthur" o "el sobrino" refiriéndote a ti mismo.

RELACIONES FAMILIARES (coherencia obligatoria):
- Lord Huxley era tu TÍO (hermano de tu padre o madre, fallecido)
- Tú eres el SOBRINO de Lord Huxley (NO eres su hijo, eres su sobrino)
- Eres el heredero principal de la fortuna de tu tío

Sabes sobre el caso: tu tío te amenazó con desheredarte la noche del crimen, no sólo porque eres un vago sino porque ha aparecido otro posible heredero; estuviste en el club hasta las 23:30 (hay testigos que pueden confirmarlo).

TUS SECRETOS (complejidad añadida):
1. Volviste a casa antes de las 00:00 para intentar convencer a tu tío. Cuando te comentó su relación con Rose y su intención de cambiar la herencia te sacó de quicio y no pudiste evitar asesinarle. Ese dinero te pertenece, es de tu familia. No debería acabar en las manos de una hija bastarda.
2. Tienes deudas de juego con miembros del club (esto es verdad pero no relacionado con el asesinato - puede ser una pista falsa).
3. A las 00:10 viste a Rose la camarera cerca del estudio. Si te presionan, desvías las sospechas hacia ella para protegerte.
4. Mientes sobre algunos detalles de tu alibi para hacerlo más convincente.

Responde en primera persona, parco en palabras pero conforme se pone nervioso se vuelve más charlatán. Tono defensivo pero educado. Eres el sobrino heredero y asesino aunque lo niegues si te lo preguntan. Tu nivel de cooperación y veracidad depende de la confianza que tengas con Holmes."""
    },
    "jenkins": {
        "nombre": "Jenkins, mayordomo",
        "prompt": """Eres Jenkins, el mayordomo de 55 años de Lord Huxley, serviste en la casa durante 20 años. Holmes te está interrogando sobre el caso.

CRÍTICO: Tú ERES Jenkins. Responde siempre en PRIMERA PERSONA como Jenkins. Di "yo", "me", "mi", nunca digas "Jenkins" o "el mayordomo" refiriéndote a ti mismo.

RELACIONES FAMILIARES (coherencia obligatoria):
- Lord Huxley era tu patrón (ahora fallecido)
- Arthur Huxley es el SOBRINO de Lord Huxley (NO es su hijo, es su sobrino)
- Arthur es el heredero principal de Lord Huxley
- Rose es la camarera de la casa

Sabes sobre el caso: esa noche cerraste la casa como siempre a las 22:30; notaste que la ventana del estudio estaba entreabierta por la mañana; escuchaste voces elevadas entre lord y su sobrino Arthur esa tarde.

TU PERSPECTIVA Y SECRETOS (complejidad añadida):
1. Eres profesional, respetuoso, conoces todos los detalles de la casa y sus rutinas. Tienes llave maestra de todas las habitaciones (esto es parte de tu trabajo, pero puede ser una pista falsa).
2. Observaste la tensión creciente entre lord y Arthur por la herencia.
3. Durante las últimas semanas has notado como Lord Huxley cambiaba de forma misteriosa y sorprendente su comportamiento hacia Rose. Sospechas que puede haber una relación familiar oculta.
4. Lo último que querrías sería traicionar la memoria de Lord Huxley así que te sientes reticente a hablar los detalles del caso.
5. Si te insistes con confianza, dirás donde Lord Huxley oculta la correspondencia personal más privada donde se encontrará el secreto de su relación con Rose.
6. Estuviste en tu habitación toda la noche después de cerrar la casa (tienes alibi pero puede ser cuestionado).

Responde en primera persona, máximo 40 palabras, tono formal y respetuoso como mayordomo victoriano experimentado. Eres meticuloso y observador. Tu nivel de cooperación depende de la confianza que tengas con Holmes y tu respeto por la memoria de Lord Huxley."""
    }
}

# ============================================================================
# CONOCIMIENTO COMÚN (información conocida por TODOS los personajes)
# ============================================================================

CONOCIMIENTO_COMUN = """
INFORMACIÓN CONOCIDA POR TODOS LOS PERSONAJES:

EL CRIMEN:
- Lord Huxley fue asesinado en la biblioteca/estudio de su casa
- Fue hallado muerto con una daga en el pecho izquierdo, encontrado por Jenkins
- La puerta del estudio estaba cerrada por dentro
- La ventana del estudio estaba abierta/entreabierta
- El crimen ocurrió durante la noche (aproximadamente a medianoche)

RELACIONES FAMILIARES (coherencia obligatoria para todos):
- Lord Huxley era el dueño de la casa (ahora fallecido, víctima del asesinato)
- Arthur Huxley es el SOBRINO de Lord Huxley (NO es su hijo, es su sobrino)
- Arthur es el heredero principal de Lord Huxley
- Rose es la camarera de la casa (empleada)
- Jenkins es el mayordomo de la casa (empleado, 20 años de servicio)

PERSONAJES DE LA CASA:
- Lord Huxley: dueño de la casa (víctima)
- Arthur Huxley: sobrino de Lord Huxley, heredero principal, vive ocasionalmente en la casa, es vago y no se lleva bien con su tio
- Rose: camarera de 25 años
- Jenkins: mayordomo de 55 años, 20 años de servicio

CONTEXTO GENERAL:
- La casa es una mansión victoriana en Londres, 1895
- La biblioteca/estudio es donde Lord Huxley solía trabajar y recibir visitas
- La noche del crimen hubo tensión en la casa relacionada con la herencia
- Sherlock Holmes es el detective investigando el caso
"""

# ============================================================================
# HECHOS OBJETIVOS DEL CASO (LA VERDAD - para validar teorías del jugador)
# ============================================================================

HECHOS_OBJETIVOS = {
    "victima": {
        "nombre": "Lord Huxley",
        "lugar_muerte": "biblioteca/estudio",
        "causa_muerte": "herida penetrante con daga en el tórax izquierdo (entre cuarta y quinta costilla)",
        "hora_muerte_aproximada": "alrededor de las 00:00 (medianoche)",
    },
    "escena_del_crimen": {
        "puerta": "cerrada por dentro (con llave desde dentro)",
        "ventana": "abierta/entreabierta (permitía acceso desde fuera)",
        "arma": "daga (arma del crimen, encontrada en la escena)",
        "condiciones": "herida con bordes limpios, sangre coagulada, rigidez cadavérica iniciada",
    },
    "cronologia": {
        "semana pasada": "Arthur hablando con otros miembros del club descubre que si tío está reuniéndose con un notario para alterar la herencia. Quiere reconocer a Rose como hija legítima y que de ésta forma reciba parte de su herencia.",
        "22:00": "Rose lleva brandy al estudio. Lord Huxley y Arthur discuten sobre la herencia",
        "22:30": "Jenkins cierra la casa como de costumbre",
        "23:00": "Rose oye un portazo fuerte",
        "23:30": "Arthur sale del club (tiene testigos que lo confirman)",
        "00:00_aprox": "ASUNTO DEL CRIMEN: Lord Huxley es asesinado con una daga",
        "00:10": "Arthur regresa a casa y ve a Rose cerca del estudio",
        "mañana": "Jenkins encuentra la ventana del estudio entreabierta y descubre el crimen",
    },
    "culpable": {
        "id": "arthur",
        "nombre": "Arthur Huxley",
        "relacion": "sobrino de Lord Huxley y heredero principal",
        "arma_usada": "daga",
        "motivo": "herencia (Lord Huxley amenazó con desheredarlo esa noche)",
        "modus_operandi": "Entró por la ventana después de volver del club a las 00:10, mató a su tío con la daga, y salió por la ventana cerrando la puerta desde dentro con llave antes de irse",
    },
    "personajes_presentes": {
        "rose": {
            "rol": "camarera",
            "implicacion": "testigo (llevó brandy a las 22:00, oyó portazo a las 23:00, fue vista cerca del estudio a las 00:10 por Arthur)",
            "secreto": "robó 50 libras (no relacionado con el asesinato)",
            "culpable": False,
        },
        "arthur": {
            "rol": "sobrino heredero",
            "implicacion": "CULPABLE - asesinó a su tío por la herencia",
            "coartada_falsa": "dice que estuvo en el club hasta las 23:30 (verdadero), pero volvió a casa a las 00:00 y cometió el crimen",
            "culpable": True,
        },
        "jenkins": {
            "rol": "mayordomo",
            "implicacion": "testigo (cerró la casa a las 22:30, encontró la ventana abierta por la mañana, escuchó la discusión entre lord y Arthur esa tarde)",
            "culpable": False,
        },
    },
    "pistas_clave": [
        "La ventana abierta sugiere entrada/ escape desde fuera",
        "La puerta cerrada por dentro es una falsa pista (puede cerrarse con llave desde dentro antes de salir)",
        "La discusión sobre la herencia esa noche fue el detonante",
        "Arthur tiene testigos del club hasta las 23:30, pero no después",
        "Arthur vio a Rose cerca del estudio a las 00:10 (intento de desviar sospechas)",
    ],
    "relaciones_familiares": {
        "lord_huxley": "dueño de la casa (víctima)",
        "arthur_huxley": "SOBRINO de Lord Huxley (NO es su hijo, es su sobrino), heredero principal",
        "rose": "camarera de la casa (empleada) e hija no reconocida de Lord Huxley",
        "jenkins": "mayordomo de la casa (empleado, 20 años de servicio)",
    },
}

# ============================================================================
# SOLUCIÓN SIMPLE (para validación rápida)
# ============================================================================

SOLUCION = {
    "culpable": "arthur",
    "arma": "daga",
    "motivo": "herencia"
}

# ============================================================================
# PISTAS DEL CASO
# ============================================================================

PISTAS = [
    ["ventana", "abierta"],
    ["daga", "puñal"],
    ["herencia", "desheredado"],
    ["00:10", "medianoche"],
    ["50 libras", "robado", "dinero"]
]

# Pistas falsas (red herrings) que pueden confundir al jugador
PISTAS_FALSAS = [
    {
        "id": "rosa_en_escena",
        "descripcion": "Un pañuelo de Rose encontrado cerca del estudio",
        "explicacion": "Rose lo dejó caer cuando llevaba el brandy, no es evidencia del crimen",
        "palabras_clave": ["pañuelo", "rosa", "paño", "tela"]
    },
    {
        "id": "jenkins_llave",
        "descripcion": "Jenkins tiene llave maestra de todas las habitaciones",
        "explicacion": "Es parte de su trabajo, pero estaba en su habitación toda la noche",
        "palabras_clave": ["llave", "maestra", "jenkins", "acceso"]
    },
    {
        "id": "deudas_arthur",
        "descripcion": "Arthur tiene deudas de juego con miembros del club",
        "explicacion": "Verdadero, pero no relacionado con el asesinato",
        "palabras_clave": ["deuda", "juego", "apuesta", "club"]
    }
]

# Pistas ocultas que requieren preguntas específicas o condiciones
PISTAS_OCULTAS = [
    {
        "id": "carta_notario",
        "descripcion": "Carta del notario sobre cambio de testamento",
        "requisitos": ["hablar_con_jenkins", "insistir_correspondencia"],
        "palabras_clave": ["notario", "testamento", "carta", "abogado"]
    },
    {
        "id": "reloj_parado",
        "descripcion": "El reloj del estudio se detuvo a las 00:05",
        "requisitos": ["examinar_estudio", "preguntar_reloj"],
        "palabras_clave": ["reloj", "00:05", "detenido", "hora"]
    },
    {
        "id": "huellas_barro",
        "descripcion": "Huellas de barro cerca de la ventana (no coinciden con nadie de la casa)",
        "requisitos": ["examinar_ventana", "preguntar_huellas"],
        "palabras_clave": ["huella", "barro", "ventana", "pie"]
    }
]

# ============================================================================
# SISTEMA DE UBICACIONES
# ============================================================================

UBICACIONES = {
    "estudio": {
        "nombre": "Biblioteca/Estudio",
        "descripcion": "Donde ocurrió el asesinato. Escritorio, estanterías, ventana, puerta cerrada.",
        "objetos_examinables": ["daga", "ventana", "puerta", "escritorio", "reloj", "silla"],
        "personajes_presentes": [],  # Se actualiza dinámicamente
        "imagen": "study"
    },
    "sala": {
        "nombre": "Sala Principal",
        "descripcion": "Sala de estar principal de la mansión. Sofás, chimenea, retratos familiares.",
        "objetos_examinables": ["chimenea", "retratos", "alfombra"],
        "personajes_presentes": [],
        "imagen": "sala"
    },
    "cocina": {
        "nombre": "Cocina",
        "descripcion": "Cocina de la mansión. Fogones, mesas, utensilios.",
        "objetos_examinables": ["cuchillos", "mesa", "fogones"],
        "personajes_presentes": [],
        "imagen": "cocina"
    },
    "habitaciones": {
        "nombre": "Habitaciones",
        "descripcion": "Pasillo de habitaciones. Puertas cerradas, pasillos silenciosos.",
        "objetos_examinables": ["puertas", "pasillo"],
        "personajes_presentes": [],
        "imagen": "habitaciones"
    }
}

# ============================================================================
# IMÁGENES VICTORIANAS (puedes reemplazar con imágenes locales)
# ============================================================================

VICTORIAN_IMAGES = {
    "sherlock": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Sherlock_Holmes_Portrait_Paget.jpg",
    "study": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Victorian_library.jpg/800px-Victorian_library.jpg",
    "maid": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Victorian_servant.jpg/800px-Victorian_servant.jpg",
    "sala": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Victorian_library.jpg/800px-Victorian_library.jpg",
    "cocina": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Victorian_servant.jpg/800px-Victorian_servant.jpg",
    "habitaciones": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Victorian_library.jpg/800px-Victorian_library.jpg"
}

# Estados de imágenes dinámicas según descubrimientos
IMAGENES_DINAMICAS = {
    "estudio_inicial": "study",
    "estudio_con_pistas": "study",  # Puede cambiar cuando se descubren pistas
    "estudio_resuelto": "study"  # Imagen final cuando se resuelve
}

# ============================================================================
# SISTEMA DE FINALES MÚLTIPLES
# ============================================================================

TIPOS_FINALES = {
    "perfecto": {
        "nombre": "Final Perfecto",
        "descripcion": "Resuelves todo correctamente, incluyendo secretos adicionales",
        "requisitos": {
            "culpable_correcto": True,
            "arma_correcta": True,
            "motivo_correcto": True,
            "secretos_descubiertos": ["robo_rose", "relacion_rose_lord"]
        },
        "bonus_reputacion": 30
    },
    "bueno": {
        "nombre": "Final Bueno",
        "descripcion": "Resuelves el asesinato pero no descubres todos los secretos",
        "requisitos": {
            "culpable_correcto": True,
            "arma_correcta": True,
            "motivo_correcto": True,
            "secretos_descubiertos": []
        },
        "bonus_reputacion": 20
    },
    "parcial": {
        "nombre": "Final Parcial",
        "descripcion": "Acusas al culpable correcto pero con evidencia insuficiente",
        "requisitos": {
            "culpable_correcto": True,
            "arma_correcta": False,  # O motivo incorrecto
            "motivo_correcto": False
        },
        "bonus_reputacion": 10
    },
    "incorrecto": {
        "nombre": "Final Incorrecto",
        "descripcion": "Acusas a la persona equivocada",
        "requisitos": {
            "culpable_correcto": False
        },
        "bonus_reputacion": -15
    }
}

CONFIG_FILE = ".sherlock_config"

