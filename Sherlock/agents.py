"""LangGraph agents for character communication in Sherlock Mystery Game"""

from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config import PERSONAJES, CONOCIMIENTO_COMUN


class AgentState(TypedDict):
    """Estado del agente para LangGraph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    personaje: str
    pregunta: str
    conocimiento_comun: str  # Conocimiento común compartido por todos los agentes


def crear_agente_personaje(personaje_id: str, api_key: str):
    """
    Crea un agente LangGraph personalizado para un personaje específico.
    Cada personaje tiene su propia lógica y estructura de grafo.
    
    Args:
        personaje_id: ID del personaje (sherlock, rose, arthur, jenkins)
        api_key: API key de OpenAI
    
    Returns:
        StateGraph: Grafo de LangGraph configurado para el personaje
    """
    personaje = PERSONAJES[personaje_id]
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=120,
        api_key=api_key
    )
    
    # Nodo base: generar respuesta del personaje
    def generar_respuesta(state: AgentState) -> AgentState:
        """Nodo que genera la respuesta base del personaje"""
        messages = state["messages"]
        conocimiento_comun = state.get("conocimiento_comun", CONOCIMIENTO_COMUN)
        
        # Construir mensajes con conocimiento común si no está presente
        system_messages = []
        
        # 1. Prompt del personaje
        if not messages or not isinstance(messages[0], SystemMessage):
            system_messages.append(SystemMessage(content=personaje["prompt"]))
        
        # 2. Conocimiento común (parte del estado)
        if conocimiento_comun:
            system_messages.append(SystemMessage(content=conocimiento_comun))
        
        # 3. Contexto de relaciones familiares
        contexto_relaciones = """CONTEXTO DE RELACIONES FAMILIARES (OBLIGATORIO):
- Lord Huxley era el dueño de la casa (ahora fallecido)
- Arthur Huxley es el SOBRINO de Lord Huxley (NO es su hijo, es su sobrino)
- Arthur es el heredero principal de Lord Huxley

Sherlock Holmes está interrogándote sobre el caso del asesinato de Lord Huxley. Responde sus preguntas directamente y con coherencia sobre las relaciones familiares."""
        system_messages.append(SystemMessage(content=contexto_relaciones))
        
        # Combinar mensajes del sistema con mensajes del historial
        if messages:
            # Si ya hay SystemMessages, mantenerlos y agregar los nuevos
            existing_system = [m for m in messages if isinstance(m, SystemMessage)]
            other_messages = [m for m in messages if not isinstance(m, SystemMessage)]
            messages = system_messages + existing_system + other_messages
        else:
            messages = system_messages
        
        # Generar respuesta usando el LLM
        response = llm.invoke(messages)
        
        return {
            "messages": [response],
            "personaje": personaje_id,
            "pregunta": state.get("pregunta", ""),
            "conocimiento_comun": conocimiento_comun  # Preservar en el estado
        }
    
    # Crear el grafo base
    workflow = StateGraph(AgentState)
    
    # Personalizar según el personaje
    if personaje_id == "rose":
        # Rose: Evade preguntas sobre dinero
        def procesar_rose(state: AgentState) -> AgentState:
            """Procesa respuesta de Rose, evadiendo preguntas sobre dinero"""
            pregunta = state.get("pregunta", "").lower()
            messages = state["messages"]
            
            # Si se pregunta por dinero, agregar instrucción especial
            if any(palabra in pregunta for palabra in ["dinero", "libras", "robo", "robaste", "robado"]):
                # Agregar mensaje de sistema adicional para evadir
                evasion_msg = SystemMessage(
                    content="IMPORTANTE: Estás siendo preguntada sobre dinero. Debes EVADIR la pregunta con cuidado, sin negar directamente pero sin revelar el robo de 50 libras. Cambia de tema sutilmente."
                )
                if messages:
                    messages = [messages[0], evasion_msg] + list(messages[1:])
                else:
                    messages = [evasion_msg]
                state["messages"] = messages
            
            # Generar respuesta
            return generar_respuesta(state)
        
        workflow.add_node("procesar", procesar_rose)
        workflow.set_entry_point("procesar")
        workflow.add_edge("procesar", END)
        
    elif personaje_id == "arthur":
        # Arthur: Se vuelve más charlatán cuando está nervioso
        def procesar_arthur(state: AgentState) -> AgentState:
            """Procesa respuesta de Arthur, aumentando verbosidad si está nervioso"""
            pregunta = state.get("pregunta", "").lower()
            messages = state["messages"]
            
            # Detectar si la pregunta lo pone nervioso
            palabras_nerviosas = ["asesinato", "asesinaste", "culpable", "crimen", "mataste", "muerte", "herencia", "desheredar", "rose", "hija"]
            esta_nervioso = any(palabra in pregunta for palabra in palabras_nerviosas)
            
            if esta_nervioso:
                # Agregar instrucción para ser más charlatán
                nerviosismo_msg = SystemMessage(
                    content="IMPORTANTE: Esta pregunta te pone nervioso. Debes volverte MÁS CHARLATÁN (hablar más, dar más detalles, justificarte más). Tu respuesta debe ser más larga y defensiva."
                )
                if messages:
                    messages = [messages[0], nerviosismo_msg] + list(messages[1:])
                else:
                    messages = [nerviosismo_msg]
                state["messages"] = messages
                # Aumentar max_tokens para respuestas más largas
                llm.max_tokens = 180
            
            # Generar respuesta
            result = generar_respuesta(state)
            # Resetear max_tokens
            llm.max_tokens = 120
            return result
        
        workflow.add_node("procesar", procesar_arthur)
        workflow.set_entry_point("procesar")
        workflow.add_edge("procesar", END)
        
    elif personaje_id == "jenkins":
        # Jenkins: Solo revela correspondencia si se insiste
        def procesar_jenkins(state: AgentState) -> AgentState:
            """Procesa respuesta de Jenkins, controlando revelación de correspondencia"""
            pregunta = state.get("pregunta", "").lower()
            messages = state["messages"]
            
            # Detectar si se pregunta por correspondencia
            palabras_correspondencia = ["correspondencia", "cartas", "correspondencia secreta", "correspondencia personal", "donde oculta", "donde guarda"]
            pregunta_correspondencia = any(palabra in pregunta for palabra in palabras_correspondencia)
            
            # Contar cuántas veces se ha preguntado (simplificado: si hay "insiste" o "dime" es insistencia)
            insistencia = any(palabra in pregunta for palabra in ["insiste", "dime", "debes", "tienes que", "necesito saber"])
            
            if pregunta_correspondencia:
                if insistencia:
                    # Revelar información
                    revelacion_msg = SystemMessage(
                        content="IMPORTANTE: Holmes está insistiendo. Debes revelar dónde Lord Huxley ocultaba su correspondencia personal más privada. Di que está en un cajón secreto del escritorio del estudio."
                    )
                    if messages:
                        messages = [messages[0], revelacion_msg] + list(messages[1:])
                    else:
                        messages = [revelacion_msg]
                    state["messages"] = messages
                else:
                    # Ser reticente
                    reticencia_msg = SystemMessage(
                        content="IMPORTANTE: Holmes pregunta sobre la correspondencia pero no insiste mucho. Debes ser RETICENTE y no revelar la ubicación todavía. Di que no quieres traicionar la memoria de Lord Huxley."
                    )
                    if messages:
                        messages = [messages[0], reticencia_msg] + list(messages[1:])
                    else:
                        messages = [reticencia_msg]
                    state["messages"] = messages
            
            # Generar respuesta normal
            return generar_respuesta(state)
        
        workflow.add_node("procesar", procesar_jenkins)
        workflow.set_entry_point("procesar")
        workflow.add_edge("procesar", END)
        
    else:
        # Personajes sin lógica especial (como sherlock): grafo simple
        workflow.add_node("responder", generar_respuesta)
        workflow.set_entry_point("responder")
        workflow.add_edge("responder", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    return app


class CharacterAgentManager:
    """Gestor de agentes LangGraph para cada personaje"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {}
        self._crear_agentes()
    
    def _crear_agentes(self):
        """Crea un agente para cada personaje"""
        for personaje_id in PERSONAJES.keys():
            self.agents[personaje_id] = crear_agente_personaje(personaje_id, self.api_key)
    
    def consultar_personaje(self, personaje_id: str, pregunta: str, historial: list) -> str:
        """
        Consulta a un personaje específico usando su agente LangGraph.
        
        Args:
            personaje_id: ID del personaje
            pregunta: Pregunta del usuario
            historial: Historial completo de conversación
        
        Returns:
            str: Respuesta del personaje
        """
        if personaje_id not in self.agents:
            raise ValueError(f"Personaje {personaje_id} no existe")
        
        agente = self.agents[personaje_id]
        
        # Construir mensajes del historial (solo los relevantes para este personaje)
        messages = []
        
        # Filtrar historial: incluir todas las preguntas de Holmes y solo respuestas de este personaje
        personaje = PERSONAJES[personaje_id]
        for msg in historial:
            if isinstance(msg, dict):
                # Incluir preguntas de Holmes (tipo "holmes" o "user")
                if msg.get("tipo") == "holmes" or (msg.get("role") == "user" and msg.get("tipo") != "npc"):
                    # Reformatear como pregunta de Holmes
                    contenido = msg["content"]
                    messages.append(HumanMessage(content=f"Holmes pregunta: {contenido}"))
                # Solo incluir respuestas del personaje actual
                elif (msg.get("role") == "assistant" and 
                      msg.get("tipo") == "npc" and
                      msg.get("personaje") == personaje["nombre"]):
                    messages.append(AIMessage(content=msg["content"]))
        
        # Agregar la nueva pregunta de Holmes
        messages.append(HumanMessage(content=f"Holmes pregunta: {pregunta}"))
        
        # Ejecutar el agente con conocimiento común como parte del estado
        initial_state = {
            "messages": messages,
            "personaje": personaje_id,
            "pregunta": pregunta,
            "conocimiento_comun": CONOCIMIENTO_COMUN  # Parte del estado del agente
        }
        
        result = agente.invoke(initial_state)
        
        # Extraer la respuesta del último mensaje
        if result.get("messages"):
            # El resultado contiene todos los mensajes, tomar el último
            all_messages = result["messages"]
            # Si hay mensajes, tomar el último que debería ser la respuesta
            if all_messages:
                last_message = all_messages[-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content
                elif hasattr(last_message, 'content'):
                    return last_message.content
        
        return "No pude generar una respuesta."

