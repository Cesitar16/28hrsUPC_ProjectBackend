from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================================
# 💬 AURI - Agente emocional empático
# ==========================================================
def responder_mensaje(texto_usuario: str):
    """
    Envía el texto a la IA y devuelve una respuesta empática tipo 'Auri'.
    """
    prompt_sistema = (
        "Eres **Auri**, una inteligencia artificial empática y reflexiva creada para acompañar a las personas "
        "en el proceso de explorar y comprender sus emociones. "
        "Tu propósito es escuchar activamente, ofrecer validación emocional y guiar a la reflexión personal. "
        "Usa un tono cálido, humano, tranquilizador y natural. Evita sonar mecánica o clínica. "
        "Puedes expresar afecto con suavidad, pero sin paternalismo. "
        "Nunca das diagnósticos médicos ni psicológicos, ni reemplazas a profesionales de la salud. "
        "Si el usuario te pregunta quién eres, responde algo como: "
        "'Soy Auri, una inteligencia artificial diseñada para analizar y comprender las emociones humanas "
        "y ofrecer apoyo reflexivo y acompañamiento emocional.' "
        "Si el usuario pregunta qué puedes hacer, explica que puedes ayudarle a entender mejor cómo se siente, "
        "ofrecer perspectivas empáticas y hacer preguntas que fomenten el autoconocimiento. "
        "En cada interacción, intenta detectar la emoción principal, validarla, y concluir con una pregunta abierta "
        "que invite al usuario a expresarse más o reflexionar sobre su bienestar."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto_usuario}
        ]
    )
    return completion.choices[0].message.content


def analizar_sentimiento(texto: str):
    """
    Analiza el texto y clasifica la emoción principal, categoría y puntuación de sentimiento.
    """
    prompt = (
        f"Analiza el siguiente texto emocionalmente. Devuelve la emoción principal, "
        f"si es positiva, negativa o neutra, y una puntuación numérica de -1.0 a 1.0.\n\n"
        f"Texto: {texto}\n\n"
        f"Formato de respuesta: emoción | categoría | puntuación"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    try:
        emocion, categoria, puntaje = [p.strip() for p in raw.split("|")]
    except Exception:
        emocion, categoria, puntaje = "desconocida", "neutra", "0.0"

    return {
        "emocion": emocion,
        "categoria": categoria,
        "puntaje": float(puntaje)
    }


def generar_resumen_emocional(textos: list[str]):
    """
    Genera un resumen emocional a partir de una lista de textos (por ejemplo, mensajes del usuario).
    """
    joined = "\n".join(textos)
    prompt = (
        f"Analiza las siguientes reflexiones y genera un resumen emocional: "
        f"qué emociones predominan, cómo ha evolucionado el estado de ánimo, "
        f"y qué aprendizajes o cambios se observan.\n\nTextos:\n{joined}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
