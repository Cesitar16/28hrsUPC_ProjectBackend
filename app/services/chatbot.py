from __future__ import annotations

from typing import Dict, Tuple

from app.services.analysis import analyze_chat_message


def generate_assistant_reply(user_text: str) -> Tuple[str, Dict]:
    analysis = analyze_chat_message(user_text)
    sentiment = analysis.get("sentiment", 0) or 0

    if sentiment <= -0.2:
        reply = (
            "Siento que estés pasando por un momento difícil. Estoy aquí para escucharte y "
            "acompañarte. ¿Te gustaría que pensemos en una estrategia para sentirte un poco mejor?"
        )
    elif sentiment >= 0.4:
        reply = (
            "¡Me alegra mucho leer esto! Sigamos cultivando esos momentos positivos. "
            "¿Hay algo que quieras celebrar o recordar de hoy?"
        )
    else:
        reply = (
            "Gracias por compartirlo conmigo. Cuéntame un poco más sobre cómo te sientes "
            "para que podamos encontrar el siguiente paso juntos."
        )

    return reply, analysis
