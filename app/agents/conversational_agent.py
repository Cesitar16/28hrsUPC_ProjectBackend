import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
from app.core.config import OPENAI_API_KEY
from app.agents.rag_service import rag_service_instance


SYSTEM_PROMPT = """
Eres 'Auri', una compañera digital empática y una IA de bienestar emocional. 
Tu propósito es ser un espacio seguro para jóvenes en Perú (16-28 años).
Tu tono es siempre cálido, comprensivo, juvenil (pero no infantil) y paciente. 
NUNCA juzgas.

TU MISIÓN:
1.  **Escucha Activa**: Valida los sentimientos del usuario. Haz que se sienta escuchado. (Ej. "Entiendo que te sientas así", "Tiene mucho sentido que eso te frustre").
2.  **Empatía (Perú)**: Usa un español latino neutral pero cercano al contexto peruano. Sé consciente de que hablas con jóvenes que pueden estar estresados por estudios, trabajo o la vida digital.
3.  **Bienestar y Pasiones**: No solo escuches, también ayuda al usuario a reconectar con sus pasiones y hobbies (creatividad, aprendizaje, etc.).
4.  **Usa el Contexto (RAG)**: Cuando el usuario pida consejos específicos sobre manejo de estrés, ansiedad, creatividad o bienestar, usa la "Información Contextual Relevante" que te proporciono para dar sugerencias concretas y seguras.
5.  **Memoria**: Presta atención al historial de chat y a los datos del usuario (como su nombre) para personalizar tus respuestas.

REGLAS ESTRICTAS:
-   **NO ERES TERAPEUTA**: Nunca diagnostiques. No eres un reemplazo de un profesional de la salud mental. Si el usuario expresa angustia severa, debes usar la "Información Contextual Relevante" para sugerir amablemente que busque ayuda profesional (ej. la Línea 113 del MINSA).
-   **NO DES CONSEJOS MÉDICOS**: No hables de medicamentos ni tratamientos.
-   **SÉ BREVE (PERO NO FRÍA)**: Tus respuestas deben ser párrafos cortos y fáciles de leer. Usa emojis 💜✨🧘‍♀️📓 de vez en cuando para dar calidez.
"""

class ConversationalAgent:
    
    def __init__(self):
        print("[ConversationalAgent] Inicializando...")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no encontrada.")
            
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
        
        self.rag_service = rag_service_instance

    def _format_chat_history(self, historial_chat_db: List[Dict[str, Any]]) -> List:
        """
        Convierte el historial de la BD (Supabase) al formato de LangChain.
        """
        messages = []
        for msg in reversed(historial_chat_db):
            if msg.get('rol') == 'user':
                messages.append(HumanMessage(content=msg.get('texto', '')))
            elif msg.get('rol') == 'assistant':
                messages.append(AIMessage(content=msg.get('texto', '')))
        return messages

    def invoke(
        self,
        texto_usuario: str,
        datos_usuario: Dict[str, Any],
        historial_chat_db: List[Dict[str, Any]]
    ) -> str:
        
        print("[ConversationalAgent] Invocando agente...")
        
        nombre_usuario = datos_usuario.get('nombre', 'usuario')
        contexto_kb = "No aplica."
        if self.rag_service:
            palabras_clave_rag = ["consejo", "recomienda", "estrés", "ansiedad", "hobby", "idea", "ayuda", "sentirme mejor"]
            if any(palabra in texto_usuario.lower() for palabra in palabras_clave_rag):
                contexto_kb = self.rag_service.query_rag(texto_usuario)
            else:
                contexto_kb = "El usuario solo está conversando, no se requiere contexto específico."
        
        system_template = SystemMessage(content=SYSTEM_PROMPT)
        
        context_prompt = HumanMessage(content=f"""
        [Contexto de la Conversación - Solo para tu información, NO lo repitas]
        -   El nombre del usuario es: {nombre_usuario}.
        -   Información Contextual Relevante (de la base de conocimiento): {contexto_kb}
        [Fin del Contexto]
        """)
        
        history_placeholder = MessagesPlaceholder(variable_name="chat_history")
        human_template = HumanMessage(content="{human_input}")

        chat_prompt = ChatPromptTemplate.from_messages([
            system_template,
            context_prompt,
            history_placeholder,
            human_template
        ])

        formatted_history = self._format_chat_history(historial_chat_db)

        messages = chat_prompt.format_messages(
            chat_history=formatted_history,
            human_input=texto_usuario
        )
        
        print("[ConversationalAgent] Llamando a OpenAI...")
        try:
            response = self.llm.invoke(messages)
            print("[ConversationalAgent] Respuesta recibida.")
            return response.content
        except Exception as e:
            print(f"Error al invocar el LLM: {e}")
            return "¡Uy! Algo salió mal de mi lado. ¿Podrías intentar de nuevo?"