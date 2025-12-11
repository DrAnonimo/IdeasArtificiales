#!/bin/bash
# Script para ejecutar el juego de Sherlock

echo "🔍 Iniciando Sherlock Mystery Game..."
echo ""

# Verificar si existe un entorno virtual
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificar si las dependencias están instaladas
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Instalando dependencias..."
    pip install -r requirements.txt
fi

# Ejecutar la aplicación
echo "🚀 Ejecutando Streamlit..."
echo "La aplicación se abrirá en http://localhost:8501"
echo ""
streamlit run app.py

