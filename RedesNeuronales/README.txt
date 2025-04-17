# Clasificación de Dígitos MNIST con Redes Neuronales

Este repositorio contiene una implementación de una red neuronal para clasificar dígitos escritos a mano del dataset MNIST, usando TensorFlow/Keras.

## 📋 Contenido del Repositorio
- `mnist_neural_network.py`: Script principal con la implementación completa
- `README.md`: Este archivo con la documentación

## 🧠 Descripción del Modelo
Implementación de una red neuronal fully-connected (Dense) con:
- **2 capas ocultas** (128 y 64 neuronas, activación ReLU)
- **Capa de salida** (10 neuronas, activación softmax)
- Optimizador: Adam
- Función de pérdida: Categorical Crossentropy

## 🛠️ Estructura del Código

### 1. Carga y Preprocesamiento de Datos
```python
# Cargar dataset MNIST
(X_train, y_train), (X_test, y_test) = keras.datasets.mnist.load_data()

# Normalización y reshape
X_train = X_train.astype("float32") / 255
X_train = X_train.reshape((60000, 28 * 28))

### 2. Construcción del modelo
```python
model = keras.Sequential([
    layers.Dense(128, activation='relu', input_shape=(28 * 28,)),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

### 3. Ajuste de parámetros
```python
history = model.fit(X_train, y_train,
                    epochs=10,
                    batch_size=64,
                    validation_split=0.2)

### 4. Evaluación
- Gráficos de precisión y pérdida durante el entrenamiento
- Evaluación en el conjunto de test
- Función para probar predicciones individuales

📊 Resultados Esperados
- Precisión en entrenamiento: ~98%
- Precisión en validación: ~97%
- Precisión en test: ~96-97%

🚀 Cómo Ejecutar
Instalar dependencias:
```python
pip install numpy matplotlib tensorflow
Ejecutar el script:
```python
python mnist_neural_network.py

📌 Visualizaciones Incluidas
- Muestra de 10 dígitos del dataset
- Gráficos de evolución de precisión y pérdida
- Predicción en una imagen aleatoria de test
