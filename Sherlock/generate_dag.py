"""
Script para generar visualización del DAG de LangGraph usado en el juego
Muestra claramente que hay un agente independiente por cada personaje
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Graphviz no está disponible. Instalando...")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os
from config import PERSONAJES

def generar_dag_graphviz():
    """Genera el DAG usando Graphviz"""
    dot = Digraph(comment='Sherlock Mystery Game - LangGraph DAG')
    dot.attr(rankdir='LR', size='8,5')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    # Nodos
    dot.node('START', 'START\n(Entrada)', shape='ellipse', fillcolor='lightgreen')
    dot.node('responder', 'Nodo: responder\n\n- Recibe: mensajes, personaje, pregunta\n- Procesa: Genera respuesta del personaje\n- Usa: LLM (gpt-3.5-turbo)\n- Retorna: mensaje de respuesta')
    dot.node('END', 'END\n(Salida)', shape='ellipse', fillcolor='lightcoral')
    
    # Aristas
    dot.edge('START', 'responder', label='invoke(initial_state)')
    dot.edge('responder', 'END', label='Respuesta generada')
    
    # Guardar
    output_file = 'dag_sherlock'
    dot.render(output_file, format='png', cleanup=True)
    print(f"✅ DAG generado: {output_file}.png")
    return output_file + '.png'

def generar_dag_matplotlib():
    """Genera el DAG usando Matplotlib mostrando todos los agentes por personaje"""
    # Filtrar personajes que tienen agentes (excluir sherlock si no tiene agente activo)
    personajes_activos = [pid for pid in PERSONAJES.keys() if pid != "sherlock"]
    num_personajes = len(personajes_activos)
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 13)
    ax.axis('off')
    
    # Título principal
    ax.text(9, 12.5, 'Sherlock Mystery Game - Arquitectura Completa', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(9, 12, 'Un Agente LangGraph por Cada Personaje NPC', 
            ha='center', va='center', fontsize=14, style='italic', color='darkblue')
    
    # Mostrar Sherlock y Watson como componentes externos
    # Sherlock (Usuario/Input)
    sherlock_box = FancyBboxPatch((0.5, 9.5), 2.5, 1.5, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#FFD700', 
                                   edgecolor='black', linewidth=2.5)
    ax.add_patch(sherlock_box)
    ax.text(1.75, 10.5, 'Sherlock Holmes', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    ax.text(1.75, 10.1, '(Usuario/Input)', ha='center', va='center', 
            fontsize=9, style='italic')
    ax.text(1.75, 9.8, 'NO es un agente', ha='center', va='center', 
            fontsize=8, color='darkred')
    
    # Watson (Narrador/Sistema)
    watson_box = FancyBboxPatch((15, 9.5), 2.5, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#90EE90', 
                                 edgecolor='black', linewidth=2.5)
    ax.add_patch(watson_box)
    ax.text(16.25, 10.5, 'Dr. Watson', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    ax.text(16.25, 10.1, '(Narrador/Sistema)', ha='center', va='center', 
            fontsize=9, style='italic')
    ax.text(16.25, 9.8, 'NO es un agente', ha='center', va='center', 
            fontsize=8, color='darkred')
    
    # Flechas desde Sherlock y hacia Watson
    arrow_sherlock = FancyArrowPatch((3, 10.25), (4, 10.25), 
                                     arrowstyle='->', mutation_scale=20, 
                                     linewidth=2, color='black', linestyle='--')
    ax.add_patch(arrow_sherlock)
    ax.text(3.5, 10.5, 'Preguntas', ha='center', va='bottom', fontsize=8)
    
    arrow_watson = FancyArrowPatch((14, 10.25), (15, 10.25), 
                                   arrowstyle='->', mutation_scale=20, 
                                   linewidth=2, color='black', linestyle='--')
    ax.add_patch(arrow_watson)
    ax.text(14.5, 10.5, 'Comentarios', ha='center', va='bottom', fontsize=8)
    
    # Dibujar cada agente por personaje
    colores = {
        'rose': '#FFB6C1',      # Rosa claro
        'arthur': '#87CEEB',    # Azul cielo
        'jenkins': '#D2B48C'    # Beige
    }
    
    nombres_completos = {
        'rose': 'Rose (Camarera)',
        'arthur': 'Arthur (Sobrino)',
        'jenkins': 'Jenkins (Mayordomo)'
    }
    
    caracteristicas = {
        'rose': 'Evade preguntas\nsobre dinero',
        'arthur': 'Se vuelve charlatán\nsi está nervioso',
        'jenkins': 'Revela correspondencia\nsolo si se insiste'
    }
    
    x_inicio = 1.5
    ancho_agente = 4
    espacio = 0.5
    
    for i, personaje_id in enumerate(personajes_activos):
        x_centro = x_inicio + i * (ancho_agente + espacio)
        y_base = 8
        
        # Título del agente
        ax.text(x_centro, y_base + 2.5, f'Agente: {nombres_completos[personaje_id]}', 
                ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Característica especial
        ax.text(x_centro, y_base + 2, caracteristicas[personaje_id], 
                ha='center', va='center', fontsize=8, style='italic', color='darkred')
        
        # Nodo START
        start_box = FancyBboxPatch((x_centro - 0.6, y_base + 0.5), 1.2, 0.6, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='lightgreen', 
                                   edgecolor='black', linewidth=1.5)
        ax.add_patch(start_box)
        ax.text(x_centro, y_base + 0.8, 'START', ha='center', va='center', 
                fontsize=9, fontweight='bold')
        
        # Nodo procesar (personalizado por personaje)
        procesar_box = FancyBboxPatch((x_centro - 1.5, y_base - 1.5), 3, 1.5, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor=colores.get(personaje_id, 'lightblue'), 
                                      edgecolor='black', linewidth=2)
        ax.add_patch(procesar_box)
        ax.text(x_centro, y_base - 0.5, 'procesar', ha='center', va='center', 
                fontsize=10, fontweight='bold')
        ax.text(x_centro, y_base - 1, 'Lógica específica', ha='center', va='center', 
                fontsize=8)
        
        # Nodo generar_respuesta
        generar_box = FancyBboxPatch((x_centro - 1.5, y_base - 3.5), 3, 1.5, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor='lightblue', 
                                      edgecolor='black', linewidth=2)
        ax.add_patch(generar_box)
        ax.text(x_centro, y_base - 2.5, 'generar_respuesta', ha='center', va='center', 
                fontsize=9, fontweight='bold')
        ax.text(x_centro, y_base - 3, 'LLM (gpt-3.5-turbo)', ha='center', va='center', 
                fontsize=8)
        
        # Nodo END
        end_box = FancyBboxPatch((x_centro - 0.6, y_base - 5), 1.2, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='lightcoral', 
                                 edgecolor='black', linewidth=1.5)
        ax.add_patch(end_box)
        ax.text(x_centro, y_base - 4.7, 'END', ha='center', va='center', 
                fontsize=9, fontweight='bold')
        
        # Flechas
        arrow1 = FancyArrowPatch((x_centro, y_base + 0.5), (x_centro, y_base), 
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow1)
        
        arrow2 = FancyArrowPatch((x_centro, y_base - 1.5), (x_centro, y_base - 2), 
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow2)
        
        arrow3 = FancyArrowPatch((x_centro, y_base - 3.5), (x_centro, y_base - 4.4), 
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow3)
    
    # Nota explicativa
    ax.text(9, 1.5, 'Cada personaje NPC tiene su propio agente LangGraph independiente con lógica personalizada', 
            ha='center', va='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Nota sobre Sherlock y Watson
    ax.text(9, 0.8, 'Sherlock (usuario) y Watson (narrador) NO son agentes LangGraph - son componentes externos', 
            ha='center', va='center', fontsize=9, style='italic', color='darkred',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor='#FFD700', label='Sherlock (Usuario)'),
        mpatches.Patch(facecolor='#90EE90', label='Watson (Narrador)'),
        mpatches.Patch(facecolor='lightgreen', label='START'),
        mpatches.Patch(facecolor='#FFB6C1', label='Rose: Evade dinero'),
        mpatches.Patch(facecolor='#87CEEB', label='Arthur: Nerviosismo'),
        mpatches.Patch(facecolor='#D2B48C', label='Jenkins: Revelación condicional'),
        mpatches.Patch(facecolor='lightblue', label='Generar Respuesta (LLM)'),
        mpatches.Patch(facecolor='lightcoral', label='END')
    ]
    ax.legend(handles=legend_elements, loc='lower center', 
              bbox_to_anchor=(0.5, -0.05), ncol=4, fontsize=8)
    
    plt.tight_layout()
    output_file = 'dag_sherlock_matplotlib.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ DAG generado: {output_file}")
    return output_file

def generar_dag_texto():
    """Genera una representación en texto del DAG mostrando todos los agentes"""
    personajes_activos = [pid for pid in PERSONAJES.keys() if pid != "sherlock"]
    
    texto = """
╔══════════════════════════════════════════════════════════════════════════════╗
║     SHERLOCK MYSTERY GAME - ARQUITECTURA COMPLETA                            ║
║     UN AGENTE LANGGRAPH POR CADA PERSONAJE NPC                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│  COMPONENTES EXTERNOS (NO son agentes LangGraph):                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🔍 SHERLOCK HOLMES (Usuario/Input)                                         │
│     • El usuario JUEGA como Sherlock Holmes                                 │
│     • NO tiene agente LangGraph                                             │
│     • Sus preguntas son el INPUT para los agentes NPC                       │
│     • Flujo: Usuario → Pregunta → Agente NPC → Respuesta                   │
│                                                                              │
│  📝 DR. WATSON (Narrador/Sistema)                                           │
│     • Sistema de narración programático                                     │
│     • NO tiene agente LangGraph                                             │
│     • Genera mensajes automáticamente:                                       │
│       - Descripción inicial del caso                                        │
│       - Comentarios ocasionales (30% probabilidad)                          │
│       - Resúmenes cuando se solicitan                                       │
│       - Lectura de correspondencia secreta                                  │
│     • Flujo: Eventos → Watson → Mensajes narrativos                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

AGENTES LANGGRAPH (Solo para personajes NPC):

"""
    
    # Dibujar cada agente
    for personaje_id in personajes_activos:
        nombre = PERSONAJES[personaje_id]["nombre"]
        nombre_upper = nombre.upper()
        texto += f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  AGENTE: {nombre_upper:<65} ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────┐
│  START  │  (Entrada del grafo)
└────┬────┘
     │ invoke(initial_state)
     │ {{"messages": [...], "personaje": "{personaje_id}", "pregunta": "..."}}
     ▼
┌─────────────────────────────────────────────────────────────┐
│              NODO: procesar (Lógica Específica)            │
"""
        
        if personaje_id == "rose":
            texto += """│                                                             │
│  • Detecta preguntas sobre dinero/libras/robo              │
│  • Agrega instrucción para EVADIR la pregunta              │
│  • No revela el robo de 50 libras                          │
"""
        elif personaje_id == "arthur":
            texto += """│                                                             │
│  • Detecta preguntas que lo ponen nervioso                 │
│  • (asesinato, herencia, Rose, etc.)                       │
│  • Aumenta verbosidad si está nervioso                     │
│  • Respuestas más largas y defensivas                       │
"""
        elif personaje_id == "jenkins":
            texto += """│                                                             │
│  • Detecta preguntas sobre correspondencia                 │
│  • Si NO hay insistencia: RETICENTE                        │
│  • Si HAY insistencia: REVELA ubicación                    │
"""
        
        texto += """└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│            NODO: generar_respuesta                          │
│                                                             │
│  Proceso:                                                    │
│    1. Construye mensajes con:                               │
│       - Prompt del sistema del personaje                    │
│       - Conocimiento común                                  │
│       - Contexto de relaciones familiares                   │
│       - Historial de conversación                           │
│       - Instrucciones especiales (si aplica)                │
│    2. Invoca LLM (gpt-3.5-turbo)                           │
│    3. Genera respuesta del personaje                        │
│                                                             │
│  Output:                                                     │
│    - AIMessage con la respuesta del personaje               │
└────┬────────────────────────────────────────────────────────┘
     │ respuesta generada
     ▼
┌─────────┐
│   END   │  (Salida del grafo)
└─────────┘

"""
    
    texto += """
═══════════════════════════════════════════════════════════════════════════════

ARQUITECTURA GENERAL:

• COMPONENTES DEL SISTEMA:
  
  🔍 SHERLOCK HOLMES (Usuario/Input):
     - El usuario JUEGA como Sherlock Holmes
     - NO tiene agente LangGraph
     - Sus preguntas son el INPUT para los agentes NPC
     - Flujo: Usuario → Pregunta → Agente NPC → Respuesta
  
  📝 DR. WATSON (Narrador/Sistema):
     - Sistema de narración programático
     - NO tiene agente LangGraph
     - Genera mensajes automáticamente:
       * Descripción inicial del caso
       * Comentarios ocasionales (30% probabilidad)
       * Resúmenes cuando se solicitan
       * Lectura de correspondencia secreta
     - Flujo: Eventos → Watson → Mensajes narrativos

• AGENTES LANGGRAPH (Solo para personajes NPC):
  UN AGENTE POR PERSONAJE: Cada personaje NPC tiene su propio agente LangGraph
  independiente con lógica personalizada.

• Agentes LangGraph activos:
"""
    
    for personaje_id in personajes_activos:
        nombre = PERSONAJES[personaje_id]["nombre"]
        texto += f"  - {personaje_id}: {nombre}\n"
    
    texto += """
• Estado: AgentState (TypedDict)
  - messages: Sequence[BaseMessage]
  - personaje: str
  - pregunta: str

• Flujo por agente:
  1. Se crea un agente LangGraph específico para cada personaje
  2. Cada consulta invoca el grafo del personaje correspondiente
  3. El nodo "procesar" aplica lógica específica del personaje
  4. El nodo "generar_respuesta" invoca el LLM
  5. Se retorna la respuesta personalizada

• Ventajas de esta arquitectura:
  - Cada personaje tiene comportamiento único y consistente
  - Fácil agregar nuevos personajes con su propia lógica
  - Aislamiento: cambios en un agente no afectan a otros
  - Escalable: cada agente puede tener su propia complejidad

═══════════════════════════════════════════════════════════════════════════════
"""
    
    with open('dag_sherlock.txt', 'w', encoding='utf-8') as f:
        f.write(texto)
    
    print("✅ DAG en texto generado: dag_sherlock.txt")
    print(texto)
    return 'dag_sherlock.txt'

if __name__ == "__main__":
    print("Generando visualización del DAG de LangGraph...\n")
    
    # Generar versión en texto (siempre disponible)
    generar_dag_texto()
    
    # Intentar generar versión gráfica
    if GRAPHVIZ_AVAILABLE:
        try:
            generar_dag_graphviz()
        except Exception as e:
            print(f"⚠️ Error con Graphviz: {e}")
            print("Intentando con Matplotlib...")
            try:
                generar_dag_matplotlib()
            except Exception as e:
                print(f"⚠️ Error con Matplotlib: {e}")
    else:
        try:
            import matplotlib
            generar_dag_matplotlib()
        except ImportError:
            print("⚠️ Ni Graphviz ni Matplotlib están disponibles.")
            print("💡 Instala con: pip install graphviz matplotlib")
            print("✅ Se generó la versión en texto: dag_sherlock.txt")

