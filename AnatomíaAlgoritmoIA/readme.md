# Regresión Logística con Solapamiento

Este código implementa un modelo de **regresión logística** para clasificar **naranjas** y **mandarinas** en función de su diámetro y peso. Además, incluye una animación del proceso de optimización por descenso de gradiente.

## Pasos del código

1. **Generación de datos:** Se crean muestras de naranjas y mandarinas con cierto solapamiento utilizando distribuciones normales.
2. **Normalización:** Se estandarizan el diámetro y el peso con la puntuación Z (Z-score).
3. **Implementación de la regresión logística:**
   - Se define la **función sigmoide** para transformar valores lineales en probabilidades.
   - Se define la **función de costo** basada en entropía cruzada.
   - Se implementa el **descenso de gradiente** para optimizar los parámetros del modelo.
4. **Entrenamiento del modelo:** Se ajustan los pesos θ mediante iteraciones del descenso de gradiente.
5. **Visualización del proceso de optimización:**
   - Se grafica la frontera de decisión en cada iteración.
   - Se crea una animación de la convergencia del modelo.
   - Se guarda la animación como un archivo GIF.

## Requisitos

Para ejecutar este código, se necesitan las siguientes bibliotecas:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
```

## Resultados

- Se genera una frontera de decisión que separa naranjas y mandarinas.
- Se observa la convergencia del modelo a medida que la función de costo disminuye.
- Se produce una animación que muestra la optimización iterativa de la frontera de decisión.

