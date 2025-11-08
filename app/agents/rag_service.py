import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import OPENAI_API_KEY

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
            
            loader = DirectoryLoader(
                KB_DIR,
                show_progress=True,
                use_multithreading=True,
                loader_kwargs={"json_loader_kwargs": {"jq_schema": "try .entradas[] | .titulo + \": \" + .contenido catch .", "text_content": False}}
            )
            # ---------------------------------
            
            documents = loader.load()
            
            if not documents:
                print("[RAGService] ADVERTENCIA: No se cargó ningún documento. Verifica los loaders y los archivos JSON.")
                return None

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = splitter.split_documents(documents)

            print("[RAGService] Creando embeddings e índice FAISS...")
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever = vectorstore.as_retriever()

            print("[RAGService] Inicializando modelo de lenguaje...")
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

            template = (
                "Usa la siguiente información del contexto para responder la pregunta.\n\n"
                "Contexto:\n{context}\n\n"
                "Pregunta: {question}\n\n"
                "Respuesta:"
            )
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


try:
    rag_service_instance = RAGService()
except Exception as e:
    print(f"No se pudo inicializar RAGService: {e}")
    rag_service_instance = None