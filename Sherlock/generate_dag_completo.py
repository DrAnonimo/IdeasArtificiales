"""
Script para generar el DAG completo de la arquitectura del juego
Muestra: Sherlock (Usuario), Watson (Narrador), y Agentes LangGraph (NPCs)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from config import PERSONAJES
import os

def generar_dag_arquitectura_completa():
    """Genera el DAG completo de la arquitectura del sistema"""
    personajes_activos = [pid for pid in PERSONAJES.keys() if pid != "sherlock"]
    
    fig, ax = plt.subplots(1, 1, figsize=(22, 16))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Título principal
    ax.text(11, 15.5, 'Sherlock Mystery Game - Arquitectura Completa', 
            ha='center', va='center', fontsize=22, fontweight='bold')
    ax.text(11, 15, 'Sistema de Juego con Agentes LangGraph', 
            ha='center', va='center', fontsize=15, style='italic', color='darkblue')
    
    # ========== SHERLOCK (Usuario/Input) ==========
    sherlock_x = 1
    sherlock_y = 12
    sherlock_w = 3.5
    sherlock_h = 2
    sherlock_box = FancyBboxPatch((sherlock_x, sherlock_y), sherlock_w, sherlock_h, 
                                   boxstyle="round,pad=0.15", 
                                   facecolor='#FFD700', 
                                   edgecolor='black', linewidth=3)
    ax.add_patch(sherlock_box)
    ax.text(sherlock_x + sherlock_w/2, sherlock_y + sherlock_h - 0.2, 'SHERLOCK HOLMES', 
            ha='center', va='center', fontsize=13, fontweight='bold')
    ax.text(sherlock_x + sherlock_w/2, sherlock_y + sherlock_h - 0.6, '(Usuario/Input)', 
            ha='center', va='center', fontsize=10, style='italic')
    ax.text(sherlock_x + sherlock_w/2, sherlock_y + sherlock_h - 0.9, '• El usuario JUEGA como Holmes', 
            ha='center', va='center', fontsize=9)
    ax.text(sherlock_x + sherlock_w/2, sherlock_y + sherlock_h - 1.2, '• NO es un agente LangGraph', 
            ha='center', va='center', fontsize=9, color='darkred', fontweight='bold')
    ax.text(sherlock_x + sherlock_w/2, sherlock_y + sherlock_h - 1.5, '• Sus preguntas son INPUT', 
            ha='center', va='center', fontsize=9)
    
    # ========== WATSON (Narrador/Sistema) ==========
    watson_x = 17.5
    watson_y = 12
    watson_w = 3.5
    watson_h = 2
    watson_box = FancyBboxPatch((watson_x, watson_y), watson_w, watson_h, 
                                 boxstyle="round,pad=0.15", 
                                 facecolor='#90EE90', 
                                 edgecolor='black', linewidth=3)
    ax.add_patch(watson_box)
    ax.text(watson_x + watson_w/2, watson_y + watson_h - 0.2, 'DR. WATSON', 
            ha='center', va='center', fontsize=13, fontweight='bold')
    ax.text(watson_x + watson_w/2, watson_y + watson_h - 0.6, '(Narrador/Sistema)', 
            ha='center', va='center', fontsize=10, style='italic')
    ax.text(watson_x + watson_w/2, watson_y + watson_h - 0.9, '• Sistema programático', 
            ha='center', va='center', fontsize=9)
    ax.text(watson_x + watson_w/2, watson_y + watson_h - 1.2, '• NO es un agente LangGraph', 
            ha='center', va='center', fontsize=9, color='darkred', fontweight='bold')
    ax.text(watson_x + watson_w/2, watson_y + watson_h - 1.5, '• Genera comentarios/resúmenes', 
            ha='center', va='center', fontsize=9)
    
    # ========== AGENTES LANGGRAPH (NPCs) ==========
    colores = {
        'rose': '#FFB6C1',      # Rosa claro
        'arthur': '#87CEEB',    # Azul cielo
        'jenkins': '#D2B48C'    # Beige
    }
    
    nombres_completos = {
        'rose': 'Rose\n(Camarera)',
        'arthur': 'Arthur\n(Sobrino)',
        'jenkins': 'Jenkins\n(Mayordomo)'
    }
    
    caracteristicas = {
        'rose': 'Evade preguntas\nsobre dinero',
        'arthur': 'Charlatán si\nestá nervioso',
        'jenkins': 'Revela correspondencia\nsolo si se insiste'
    }
    
    # Calcular posiciones de agentes para evitar solapamiento
    x_inicio = 6
    ancho_agente = 3
    espacio = 0.5
    y_base_agentes = 8.5
    altura_agente = 5.5
    
    # Título de la sección de agentes
    ax.text(11, 10.5, 'AGENTES LANGGRAPH (NPCs)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Guardar posiciones de agentes para las flechas
    posiciones_agentes = []
    
    for i, personaje_id in enumerate(personajes_activos):
        x_centro = x_inicio + i * (ancho_agente + espacio)
        y_base = y_base_agentes
        
        posiciones_agentes.append({
            'x_centro': x_centro,
            'x_izq': x_centro - 1.3,
            'x_der': x_centro + 1.3,
            'y_top': y_base + 0.3,
            'y_bottom': y_base - altura_agente + 0.3
        })
        
        # Contenedor del agente completo
        agente_container = FancyBboxPatch((x_centro - 1.3, y_base - altura_agente + 0.3), 
                                          2.6, altura_agente, 
                                          boxstyle="round,pad=0.1", 
                                          facecolor='white', 
                                          edgecolor='black', linewidth=2,
                                          linestyle='--')
        ax.add_patch(agente_container)
        
        # Título del agente
        ax.text(x_centro, y_base + 0.1, nombres_completos[personaje_id], 
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Característica especial
        ax.text(x_centro, y_base - 0.2, caracteristicas[personaje_id], 
                ha='center', va='center', fontsize=8, style='italic', color='darkred')
        
        # Nodo START
        start_y = y_base - 0.8
        start_box = FancyBboxPatch((x_centro - 0.5, start_y - 0.2), 1, 0.4, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='lightgreen', 
                                   edgecolor='black', linewidth=1.5)
        ax.add_patch(start_box)
        ax.text(x_centro, start_y, 'START', ha='center', va='center', 
                fontsize=8, fontweight='bold')
        
        # Nodo procesar (personalizado por personaje)
        procesar_y = y_base - 1.8
        procesar_box = FancyBboxPatch((x_centro - 1.1, procesar_y - 0.4), 2.2, 0.8, 
                                      boxstyle="round,pad=0.08", 
                                      facecolor=colores.get(personaje_id, 'lightblue'), 
                                      edgecolor='black', linewidth=2)
        ax.add_patch(procesar_box)
        ax.text(x_centro, procesar_y, 'procesar', ha='center', va='center', 
                fontsize=9, fontweight='bold')
        ax.text(x_centro, procesar_y - 0.25, 'Lógica específica', ha='center', va='center', 
                fontsize=7)
        
        # Nodo generar_respuesta
        generar_y = y_base - 3.0
        generar_box = FancyBboxPatch((x_centro - 1.1, generar_y - 0.4), 2.2, 0.8, 
                                      boxstyle="round,pad=0.08", 
                                      facecolor='lightblue', 
                                      edgecolor='black', linewidth=2)
        ax.add_patch(generar_box)
        ax.text(x_centro, generar_y, 'generar', ha='center', va='center', 
                fontsize=8, fontweight='bold')
        ax.text(x_centro, generar_y - 0.25, 'LLM (gpt-3.5-turbo)', ha='center', va='center', 
                fontsize=7)
        
        # Nodo END
        end_y = y_base - 4.4
        end_box = FancyBboxPatch((x_centro - 0.5, end_y - 0.2), 1, 0.4, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='lightcoral', 
                                 edgecolor='black', linewidth=1.5)
        ax.add_patch(end_box)
        ax.text(x_centro, end_y, 'END', ha='center', va='center', 
                fontsize=8, fontweight='bold')
        
        # Flechas internas del agente
        arrow1 = FancyArrowPatch((x_centro, start_y - 0.2), (x_centro, procesar_y + 0.4), 
                                arrowstyle='->', mutation_scale=12, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow1)
        
        arrow2 = FancyArrowPatch((x_centro, procesar_y - 0.4), (x_centro, generar_y + 0.4), 
                                arrowstyle='->', mutation_scale=12, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow2)
        
        arrow3 = FancyArrowPatch((x_centro, generar_y - 0.4), (x_centro, end_y + 0.2), 
                                arrowstyle='->', mutation_scale=12, 
                                linewidth=1.5, color='black')
        ax.add_patch(arrow3)
    
    # ========== FLECHAS DE INTERACCIÓN ==========
    
    # Sherlock → Agentes (Preguntas)
    # Punto de salida: borde derecho de Sherlock
    sherlock_salida_x = sherlock_x + sherlock_w
    sherlock_salida_y = sherlock_y + sherlock_h/2
    
    for i, pos in enumerate(posiciones_agentes):
        # Punto de entrada: borde izquierdo del agente, en la parte superior
        agente_entrada_x = pos['x_izq']
        agente_entrada_y = pos['y_top']
        
        arrow_sherlock = FancyArrowPatch(
            (sherlock_salida_x, sherlock_salida_y), 
            (agente_entrada_x, agente_entrada_y), 
            arrowstyle='->', mutation_scale=20, 
            linewidth=2.5, color='#FF6B00', linestyle='-')
        ax.add_patch(arrow_sherlock)
        
        if i == 0:
            # Etiqueta solo para la primera flecha
            mid_x = (sherlock_salida_x + agente_entrada_x) / 2
            mid_y = (sherlock_salida_y + agente_entrada_y) / 2
            ax.text(mid_x, mid_y + 0.3, 'Preguntas', ha='center', va='bottom', 
                    fontsize=10, fontweight='bold', color='#FF6B00',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#FF6B00'))
    
    # Agentes → Watson (Respuestas/Eventos)
    # Punto de entrada: borde izquierdo de Watson
    watson_entrada_x = watson_x
    watson_entrada_y = watson_y + watson_h/2
    
    for i, pos in enumerate(posiciones_agentes):
        # Punto de salida: borde derecho del agente, en la parte superior
        agente_salida_x = pos['x_der']
        agente_salida_y = pos['y_top']
        
        arrow_watson = FancyArrowPatch(
            (agente_salida_x, agente_salida_y), 
            (watson_entrada_x, watson_entrada_y), 
            arrowstyle='->', mutation_scale=20, 
            linewidth=2.5, color='#0066CC', linestyle='-')
        ax.add_patch(arrow_watson)
        
        if i == len(posiciones_agentes) - 1:
            # Etiqueta solo para la última flecha
            mid_x = (agente_salida_x + watson_entrada_x) / 2
            mid_y = (agente_salida_y + watson_entrada_y) / 2
            ax.text(mid_x, mid_y - 0.3, 'Respuestas/\nEventos', ha='center', va='top', 
                    fontsize=10, fontweight='bold', color='#0066CC',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#0066CC'))
    
    # ========== CONOCIMIENTO COMÚN ==========
    conocimiento_x = 9.5
    conocimiento_y = 1.5
    conocimiento_w = 3
    conocimiento_h = 1.5
    conocimiento_box = FancyBboxPatch((conocimiento_x, conocimiento_y), conocimiento_w, conocimiento_h, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor='#E6E6FA', 
                                      edgecolor='black', linewidth=2)
    ax.add_patch(conocimiento_box)
    ax.text(conocimiento_x + conocimiento_w/2, conocimiento_y + conocimiento_h - 0.2, 
            'CONOCIMIENTO COMUN', ha='center', va='center', 
            fontsize=10, fontweight='bold')
    ax.text(conocimiento_x + conocimiento_w/2, conocimiento_y + conocimiento_h - 0.6, 
            'Parte del AgentState', ha='center', va='center', 
            fontsize=9, style='italic')
    ax.text(conocimiento_x + conocimiento_w/2, conocimiento_y + conocimiento_h - 0.9, 
            'Compartido por todos', ha='center', va='center', 
            fontsize=8)
    ax.text(conocimiento_x + conocimiento_w/2, conocimiento_y + conocimiento_h - 1.2, 
            'los agentes', ha='center', va='center', 
            fontsize=8)
    
    # Flecha desde conocimiento común a agentes
    conocimiento_salida_x = conocimiento_x + conocimiento_w/2
    conocimiento_salida_y = conocimiento_y + conocimiento_h
    
    for i, pos in enumerate(posiciones_agentes):
        # Punto de entrada: parte inferior del agente (donde está el estado)
        agente_entrada_x = pos['x_centro']
        agente_entrada_y = pos['y_bottom']
        
        arrow_conocimiento = FancyArrowPatch(
            (conocimiento_salida_x, conocimiento_salida_y), 
            (agente_entrada_x, agente_entrada_y), 
            arrowstyle='->', mutation_scale=15, 
            linewidth=1.5, color='purple', 
            linestyle='--', alpha=0.7)
        ax.add_patch(arrow_conocimiento)
        
        if i == 1:
            # Etiqueta solo para el agente del medio
            mid_x = (conocimiento_salida_x + agente_entrada_x) / 2
            mid_y = (conocimiento_salida_y + agente_entrada_y) / 2
            ax.text(mid_x - 0.5, mid_y, 'Estado\ncompartido', ha='center', va='center', 
                    fontsize=8, style='italic', color='purple',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ========== NOTAS EXPLICATIVAS ==========
    ax.text(11, 0.5, 'Arquitectura: Usuario (Sherlock) → Agentes LangGraph (NPCs) → Narrador (Watson)', 
            ha='center', va='center', fontsize=9, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor='#FFD700', label='Sherlock (Usuario)'),
        mpatches.Patch(facecolor='#90EE90', label='Watson (Narrador)'),
        mpatches.Patch(facecolor='#E6E6FA', label='Conocimiento Común (Estado)'),
        mpatches.Patch(facecolor='#FFB6C1', label='Rose'),
        mpatches.Patch(facecolor='#87CEEB', label='Arthur'),
        mpatches.Patch(facecolor='#D2B48C', label='Jenkins'),
        mpatches.Patch(facecolor='lightblue', label='LLM (gpt-3.5-turbo)')
    ]
    ax.legend(handles=legend_elements, loc='upper center', 
              bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=9)
    
    plt.tight_layout()
    output_file = 'dag_arquitectura_completa.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ DAG de arquitectura completa generado: {output_file}")
    return output_file

if __name__ == "__main__":
    print("Generando DAG de arquitectura completa...\n")
    generar_dag_arquitectura_completa()
    print("\n✅ Diagrama generado exitosamente!")

