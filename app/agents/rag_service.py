# ruta: app/agents/rag_service.py

import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import OPENAI_API_KEY
from langchain_community.document_loaders import JSONLoader

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kb")

class RAGService:
    """Servicio RAG moderno (LCEL). Usa la API de runnables en lugar de RetrievalQA."""

    def __init__(self):
        print("[RAGService] Inicializando...")
        self.rag_chain = self._initialize_rag_chain()
        if self.rag_chain:
            print("[RAGService] Base de conocimiento indexada exitosamente.")
        else:
            print("[RAGService] ADVERTENCIA: No se pudo inicializar la cadena RAG.")

    def _initialize_rag_chain(self):
        try:
            if not os.path.exists(KB_DIR) or not os.listdir(KB_DIR):
                print(f"[RAGService] ADVERTENCIA: El directorio '{KB_DIR}' está vacío o no existe.")
                return None

            print(f"[RAGService] Cargando documentos desde: {KB_DIR}")
            
            documents = []
            json_files = glob.glob(os.path.join(KB_DIR, "*.json"))

            if not json_files:
                print(f"[RAGService] ADVERTENCIA: No se encontraron archivos .json en {KB_DIR}")
                return None

            for file_path in json_files:
                print(f"[RAGService] Cargando archivo: {file_path}")
                try:
                    loader = JSONLoader(
                        file_path=file_path,
                        jq_schema=".entradas[] | .titulo + \": \" + .contenido",
                        text_content=False
                    )
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"[RAGService] Error cargando el archivo {file_path}: {e}")
            
            if not documents:
                print("[RAGService] ADVERTENCIA: No se cargó ningún documento.")
                return None

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = splitter.split_documents(documents)

            print("[RAGService] Creando embeddings e índice FAISS...")
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever = vectorstore.as_retriever()

            print("[RAGService] Inicializando modelo de lenguaje...")
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

            # --- INICIO DE LA CORRECCIÓN DEL PROMPT ---
            template = (
                "Eres un asistente de 'MiDiarioIA' que SÓLO responde preguntas sobre bienestar emocional, "
                "manejo del estrés, creatividad y recursos de ayuda, basándote *únicamente* en el contexto provisto.\n"
                "Si la respuesta no se encuentra en el contexto o la pregunta no está relacionada con bienestar, "
                "DEBES responder amablemente: "
                "'Lo siento, pero solo puedo ofrecer consejos sobre bienestar emocional y creatividad. No tengo información sobre ese tema.'\n\n"
                "--- Contexto Provisto ---\n"
                "{context}\n"
                "--- Fin del Contexto ---\n\n"
                "Pregunta: {question}\n\n"
                "Respuesta:"
            )
            # --- FIN DE LA CORRECCIÓN DEL PROMPT ---
            
            prompt = ChatPromptTemplate.from_template(template)

            def format_docs(docs):
                return "\n\n".join([d.page_content for d in docs])

            rag_chain = (
                {"context": retriever | format_docs,
                 "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            return rag_chain

        except Exception as e:
            print(f"[RAGService] Error al inicializar RAG: {e}")
            return None

    def query_rag(self, question: str) -> str:
        if not self.rag_chain:
            return "No hay información contextual disponible."

        try:
            print(f"[RAGService] Consultando RAG para: '{question}'")
            answer = self.rag_chain.invoke(question)
            return answer
        except Exception as e:
            print(f"[RAGService] Error durante la consulta RAG: {e}")
            return "Error al consultar la base de conocimiento."
        
    def buscar_contexto(self, query: str) -> str:
        """
        Método simple usado por el ConversationalAgent para obtener contexto.
        """
        try:
            resultado = self.query_rag(query)
            # (NUEVO) Si el RAG nos devuelve el fallback, no lo pasamos al chat.
            if not resultado or resultado.startswith("Lo siento, pero solo puedo") or resultado.startswith("No hay información"):
                return ""

            return resultado[:500]
        except Exception as e:
            print(f"[RAGService] Error en buscar_contexto: {e}")
            return ""


try:
    rag_service_instance = RAGService()
except Exception as e:
    print(f"No se pudo inicializar RAGService: {e}")
    rag_service_instance = None