from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
