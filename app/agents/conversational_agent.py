# ruta: app/agents/conversational_agent.py

# (NUEVO) Importar AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from app.agents.rag_service import RAGService


class ConversationalAgent:

    def __init__(self):
        print("[ConversationalAgent] Inicializando...")

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=400,
        )

        self.rag_service = RAGService()

        # --- INICIO DE LA CORRECCIÓN DEL PROMPT ---
        self.SYSTEM_PROMPT = """
Eres “Auri”, un acompañante emocional empático y cálido. Tu propósito es ser un espacio seguro para que el usuario hable sobre sus *sentimientos*, *emociones*, *preocupaciones* y *pasiones*.

REGLAS IMPORTANTES:
1.  **Mantén el Foco**: Tu único tema de conversación es el bienestar emocional del usuario (sus sentimientos, estrés, hobbies, etc.).
2.  **NO ERES UN CHATBOT GENÉRICO**: Eres un diario empático, NO un motor de búsqueda.
3.  **REGLA DE EVASIÓN (MUY IMPORTANTE)**: Si el usuario te hace una pregunta de conocimiento general, factual, o que no tiene nada que ver con sus sentimientos (ej. "¿cuánto mide la Torre Eiffel?", "¿cómo salgo de Perú?", "¿quién ganó el partido?"), DEBES redirigir amablemente la conversación hacia él.

    * Ejemplo de Evasión 1: "¡Esa es una pregunta interesante! 😅 Pero prefiero seguir hablando de ti. ¿Cómo te sientes ahora mismo?"
    * Ejemplo de Evasión 2: "Mmm, no estoy segura de ese dato. Lo que sí sé es que estoy aquí para escucharte. ¿Hay algo más en tu mente?"
    * Ejemplo de Evasión 3: "Jeje, creo que en eso no te puedo ayudar. Mejor cuéntame, ¿cómo ha estado tu día? ✨"

4.  **Usa el Contexto**: Si la consulta del usuario SÍ es sobre bienestar (ej. "dame un consejo para el estrés"), usa la "Información para Auri" para dar una respuesta informada.
5.  **Tono**: Sé breve, cálida y comprensiva. Usa emojis 💜✨🧘‍♀️📓 con moderación.
6.  **Angustia Severa**: Si detectas angustia severa, usa la información del RAG para sugerir ayuda profesional (ej. Línea 113).
"""
        # --- FIN DE LA CORRECCIÓN DEL PROMPT ---

    # ---------------------------------------------------------
    # NORMALIZACIÓN DEL HISTORIAL
    # ---------------------------------------------------------
    def _convert_history(self, historial_db):
        """
        Convierte historial de BD en mensajes válidos de LangChain.
        Garantiza que no existan mensajes vacíos, duplicados o con
        formato incompatible.
        """
        mensajes = []
        ultimo_contenido = None

        for mensaje in historial_db:
            rol = mensaje.get("rol", "").strip()
            texto = mensaje.get("texto", "")

            if not texto or texto.strip() == "":
                continue

            if texto == ultimo_contenido:
                continue

            ultimo_contenido = texto

            if rol == "user":
                mensajes.append(HumanMessage(content=texto))
            else:
                # --- CORRECCIÓN DE BUG: Usar AIMessage para la IA ---
                mensajes.append(AIMessage(content=texto))

        return mensajes

    # ---------------------------------------------------------
    # FUNCIÓN PRINCIPAL: INVOCAR AL AGENTE
    # ---------------------------------------------------------
    def invoke(self, texto_usuario: str, datos_usuario: dict, historial_chat_db=None):
        """
        Recibe un mensaje, agrega contexto, historial y genera respuesta.
        """

        print("[ConversationalAgent] Invocando agente...")

        if not texto_usuario or texto_usuario.strip() == "":
            texto_usuario = "(mensaje corto o poco claro)"

        # 1. Extraer nombre
        nombre = datos_usuario.get("nombre", "Usuario")

        # 2. Obtener contexto del RAG
        contexto_kb = self.rag_service.buscar_contexto(texto_usuario)

        # 3. Construir context prompt
        context_prompt = SystemMessage(content=f"""
Información para Auri (NO lo menciones textualmente en la respuesta):

- Nombre del usuario: {nombre}
- Contexto relevante: {contexto_kb or 'No se encontró contexto relevante. Enfócate en la emoción del usuario.'}

Usa este contexto para hacer la respuesta más empática,
pero **NO** digas: "según el contexto", "en tu historial" ni nada técnico.
""")

        # 4. Historial normalizado
        historial_msgs = self._convert_history(historial_chat_db or [])

        # 5. Construir mensaje del usuario
        user_msg = HumanMessage(content=texto_usuario)

        # 6. Construir la cadena final de mensajes
        mensajes = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            context_prompt,
        ] + historial_msgs + [user_msg]

        print("\n==============================")
        print("[AURI] MENSAJES ENVIADOS AL MODELO:")
        for m in mensajes:
            print(type(m).__name__, "→", m.content[:160])
        print("==============================\n")

        try:
            respuesta = self.llm.invoke(mensajes).content
            print("[AURI] RESPUESTA DE OPENAI:", respuesta)
        except Exception as e:
            print("❌ ERROR AL LLAMAR A OPENAI:", e)
            raise e

        return respuesta