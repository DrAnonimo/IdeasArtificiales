# 🔍 Sherlock Mystery Game - Python Edition

Un juego interactivo de misterio estilo Sherlock Holmes donde investigas un asesinato interrogando personajes con IA.

## 📋 Requisitos

- Python 3.8 o superior
- API key de OpenAI (gratuita con límite de uso)
- Conexión a internet (para la API de OpenAI)

## 🚀 Instalación

1. **Crear entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

4. **Abrir en el navegador:**
   La aplicación se abrirá automáticamente en `http://localhost:8501`

## 🎮 Cómo jugar

1. **Primera vez:** Ingresa tu API key de OpenAI (comienza con `sk-`)
2. **Interrogar personajes:** Haz preguntas a los personajes disponibles
3. **Cambiar personaje:** Usa el botón "Cambiar personaje" para hablar con otros
4. **Descubrir pistas:** Las pistas se detectan automáticamente cuando los personajes las mencionan
5. **Resolver el caso:** Cuando tengas suficiente información, intenta resolver el crimen

## 🖼️ Imágenes Victorianas (Opcional)

Para mejorar la experiencia visual, puedes agregar imágenes victorianas en la carpeta `images/`:

- `images/sherlock.jpg` - Imagen de Sherlock Holmes
- `images/rose.jpg` o `images/maid.jpg` - Imagen de la camarera
- `images/arthur.jpg` - Imagen del sobrino
- `images/study.jpg` - Imagen de la biblioteca/estudio

**Fuentes sugeridas para imágenes:**
- [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Victorian_era)
- [Pixabay](https://pixabay.com/) - Buscar "victorian era", "sherlock holmes"
- [Unsplash](https://unsplash.com/) - Buscar términos relacionados

Si no tienes imágenes locales, la aplicación usará URLs de imágenes públicas por defecto.

## 📁 Estructura del proyecto

```
sherlock-python/
├── app.py              # Aplicación principal Streamlit
├── config.py           # Configuración y personajes
├── game_logic.py       # Lógica del juego y detección de pistas
├── requirements.txt    # Dependencias Python
├── README_PYTHON.md   # Este archivo
├── .sherlock_config    # API key guardada (se crea automáticamente)
└── images/            # Imágenes victorianas (opcional)
    ├── sherlock.jpg
    ├── rose.jpg
    ├── arthur.jpg
    └── study.jpg
```

## 🔐 Seguridad

- Tu API key se guarda localmente en el archivo `.sherlock_config`
- No se comparte con nadie ni se envía a servidores externos (excepto OpenAI)
- Puedes eliminarla usando el botón "Cambiar API Key" en la barra lateral

## 🐛 Solución de problemas

**Error: "No module named 'streamlit'"**
- Instala las dependencias: `pip install -r requirements.txt`

**Error de API: "Invalid API key"**
- Verifica que tu API key comience con `sk-`
- Asegúrate de tener créditos en tu cuenta de OpenAI

**El juego no inicia:**
- Verifica que Python 3.8+ esté instalado: `python --version`
- Asegúrate de estar en el directorio correcto

**Error al cargar imágenes:**
- Si las imágenes no se cargan, la aplicación seguirá funcionando
- Puedes usar URLs de imágenes públicas o agregar imágenes locales en `images/`

## 📝 Notas

- La aplicación funciona completamente en local
- Requiere conexión a internet para las llamadas a la API de OpenAI
- Los mensajes se mantienen durante la sesión
- Puedes reiniciar el juego en cualquier momento

## 🎯 Créditos

Basado en el proyecto original "Sherlock Local" desarrollado en JavaScript.

## 📄 Licencia

Proyecto educativo - Uso libre.

