import numpy as np
import matplotlib.pyplot as plt

# Generar 100 puntos aleatorios con etiquetas
np.random.seed(42)  # Para reproducibilidad
n_puntos = 100
X = np.random.rand(n_puntos, 2) * 10  # Puntos en el rango [0, 10]
# Etiquetas: 0 si x1 + x2 < 10, 1 si x1 + x2 >= 10
etiquetas = (X[:, 0] + X[:, 1] >= 10).astype(int)

# Inicialización de pesos y sesgo
w = np.random.rand(2)  # Pesos para x1 y x2
b = np.random.rand()   # Sesgo
tasa_aprendizaje = 0.01

# Función de activación (escalón)
def funcion_activacion(z):
    return 1 if z >= 0 else 0

# Entrenamiento del perceptrón
for _ in range(100):  # 100 iteraciones
    for i in range(n_puntos):
        x1, x2 = X[i]
        etiqueta = etiquetas[i]
        # Suma ponderada
        z = w[0] * x1 + w[1] * x2 + b
        # Salida del perceptrón
        y = funcion_activacion(z)
        # Actualización de pesos y sesgo
        w[0] += tasa_aprendizaje * (etiqueta - y) * x1
        w[1] += tasa_aprendizaje * (etiqueta - y) * x2
        b += tasa_aprendizaje * (etiqueta - y)

# Visualización de la línea de decisión
x = np.linspace(0, 10, 100)
y_linea = (-w[0] * x - b) / w[1]

plt.scatter(X[:, 0], X[:, 1], c=etiquetas, cmap='bwr')
plt.plot(x, y_linea, 'g--', label="Línea de decisión")
plt.title("Perceptrón: Clasificación de 100 puntos")
plt.xlabel("x1")
plt.ylabel("x2")
plt.legend()
plt.show()
