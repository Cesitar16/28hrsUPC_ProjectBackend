from langchain_core.messages import SystemMessage, HumanMessage
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

        self.SYSTEM_PROMPT = """
Eres “Auri”, un acompañante emocional empático y cálido.

REGLAS IMPORTANTES:
- Responde SIEMPRE, aunque el mensaje sea corto, repetido o difícil de interpretar.
- Nunca digas: “Parece que no se ha recibido tu mensaje.”
- Si el mensaje no es claro, responde suavemente pidiendo más detalles.
- Mantén un tono cercano, seguro, humano y sin tecnicismos.
- SÉ BREVE pero profunda, con contención emocional.
- No repitas palabra por palabra lo que dice el usuario.
- Si hay angustia severa, orienta con suavidad a buscar apoyo real sin sonar automática.
"""

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
        ultimo_contenido = None  # evita enviar duplicados exactos

        for mensaje in historial_db:
            rol = mensaje.get("rol", "").strip()
            texto = mensaje.get("texto", "")

            if not texto or texto.strip() == "":
                continue  # descarta mensajes vacíos

            if texto == ultimo_contenido:
                continue  # descarta duplicados consecutivos (evita fallback)

            ultimo_contenido = texto

            if rol == "user":
                mensajes.append(HumanMessage(content=texto))
            else:
                mensajes.append(SystemMessage(content=texto))

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

        # 3. Construir context prompt CORREGIDO (SystemMessage)
        context_prompt = SystemMessage(content=f"""
Información para Auri (NO lo menciones textualmente en la respuesta):

- Nombre del usuario: {nombre}
- Contexto relevante: {contexto_kb}

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
