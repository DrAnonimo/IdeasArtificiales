# 📊 DAG de LangGraph - Sherlock Mystery Game

## 🎯 Arquitectura Completa del Sistema

### Componentes Externos (NO son agentes LangGraph)

#### 🔍 **Sherlock Holmes** (Usuario/Input)
- El usuario **JUEGA como Sherlock Holmes**
- **NO tiene agente LangGraph**
- Sus preguntas son el **INPUT** para los agentes NPC
- Flujo: `Usuario → Pregunta → Agente NPC → Respuesta`

#### 📝 **Dr. Watson** (Narrador/Sistema)
- Sistema de narración **programático**
- **NO tiene agente LangGraph**
- Genera mensajes automáticamente:
  - Descripción inicial del caso
  - Comentarios ocasionales (30% probabilidad)
  - Resúmenes cuando se solicitan
  - Lectura de correspondencia secreta
- Flujo: `Eventos → Watson → Mensajes narrativos`

### Agentes LangGraph (Solo para personajes NPC)

**IMPORTANTE**: Cada personaje NPC tiene su **propio agente LangGraph independiente** con lógica personalizada.

## Diagrama de Arquitectura

### Agente: ROSE (Camarera)

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: procesar (Lógica Específica)     │
│  • Detecta preguntas sobre dinero       │
│  • Agrega instrucción para EVADIR       │
│  • No revela el robo de 50 libras       │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: generar_respuesta                 │
│  • LLM (gpt-3.5-turbo)                  │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

### Agente: ARTHUR (Sobrino)

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: procesar (Lógica Específica)     │
│  • Detecta preguntas que lo ponen       │
│    nervioso (asesinato, herencia, etc.) │
│  • Aumenta verbosidad si está nervioso   │
│  • Respuestas más largas y defensivas    │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: generar_respuesta                 │
│  • LLM (gpt-3.5-turbo)                  │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

### Agente: JENKINS (Mayordomo)

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: procesar (Lógica Específica)     │
│  • Detecta preguntas sobre              │
│    correspondencia                       │
│  • Si NO hay insistencia: RETICENTE     │
│  • Si HAY insistencia: REVELA ubicación │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  NODO: generar_respuesta                 │
│  • LLM (gpt-3.5-turbo)                  │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## Características de la Arquitectura

### Un Agente por Personaje
- **Rose**: Agente con lógica para evadir preguntas sobre dinero
- **Arthur**: Agente con lógica para aumentar verbosidad cuando está nervioso
- **Jenkins**: Agente con lógica para revelación condicional de correspondencia
- **Sherlock**: Agente simple (sin lógica especial)

### Tipo de Grafos
- **Grafos lineales personalizados**: Cada personaje tiene su propia estructura
- **Nodo de procesamiento específico**: `procesar` con lógica única por personaje
- **Nodo común**: `generar_respuesta` que invoca el LLM
- **Sin ramificaciones ni loops**: Flujo directo pero personalizado

### Estado (AgentState)
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    personaje: str
    pregunta: str
```

### Flujo de Ejecución

1. **Inicialización**: Se crea un agente LangGraph por cada personaje
   - `rose` → Agente para Rose
   - `arthur` → Agente para Arthur
   - `jenkins` → Agente para Jenkins

2. **Invocación**: Cada consulta invoca el grafo con:
   ```python
   initial_state = {
       "messages": [...],  # Historial de conversación
       "personaje": "rose",
       "pregunta": "¿Qué viste esa noche?"
   }
   result = agente.invoke(initial_state)
   ```

3. **Procesamiento**: El nodo `responder`:
   - Recibe el estado inicial
   - Construye los mensajes con contexto completo
   - Invoca el LLM (gpt-3.5-turbo)
   - Genera la respuesta del personaje

4. **Retorno**: Se extrae el último mensaje del resultado

## Código del Grafo

```python
def crear_agente_personaje(personaje_id: str, api_key: str):
    # Crear el grafo
    workflow = StateGraph(AgentState)
    
    # Agregar nodos
    workflow.add_node("responder", responder_pregunta)
    
    # Configurar entrada y salida
    workflow.set_entry_point("responder")
    workflow.add_edge("responder", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    return app
```

## Notas

⚠️ **Este es un grafo muy simple**. LangGraph permite crear grafos mucho más complejos con:
- Múltiples nodos en secuencia
- Condiciones y ramificaciones (`add_conditional_edges`)
- Loops e iteraciones
- Memoria persistente entre llamadas
- Coordinación entre múltiples agentes

### Posibles Mejoras

1. **Validación de respuesta**: Agregar un nodo que valide la respuesta antes de retornarla
2. **Análisis de sentimiento**: Detectar si el personaje está nervioso o mintiendo
3. **Memoria a largo plazo**: Guardar información importante del personaje
4. **Coordinación entre agentes**: Hacer que los personajes "escuchen" lo que dicen otros

## Archivos Generados

- `dag_sherlock.txt`: Versión en texto ASCII
- `dag_sherlock_matplotlib.png`: Versión gráfica (si matplotlib está disponible)
- `dag_sherlock.png`: Versión con Graphviz (si graphviz está disponible)

Para regenerar los diagramas:
```bash
python generate_dag.py
```

