from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict

POSITIVE_WORDS = {"feliz", "contento", "agradecido", "tranquilo", "alegre", "emocionado"}
NEGATIVE_WORDS = {"triste", "estresado", "ansioso", "enojado", "cansado", "deprimido", "solo"}
NEUTRAL_WORDS = {"ok", "normal", "estándar", "regular"}

EMOTION_MAP = {
    "feliz": ("alegría", "positiva"),
    "contento": ("alegría", "positiva"),
    "agradecido": ("gratitud", "positiva"),
    "tranquilo": ("calma", "positiva"),
    "alegre": ("alegría", "positiva"),
    "emocionado": ("entusiasmo", "positiva"),
    "triste": ("tristeza", "negativa"),
    "estresado": ("estrés", "negativa"),
    "ansioso": ("ansiedad", "negativa"),
    "enojado": ("ira", "negativa"),
    "cansado": ("cansancio", "negativa"),
    "deprimido": ("depresión", "negativa"),
    "solo": ("soledad", "negativa"),
}


def summarize_text(text: str, max_chars: int = 200) -> str:
    normalized = " ".join(text.strip().split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def estimate_sentiment_score(text: str) -> float:
    words = [word.strip(".,;:!¿?¡").lower() for word in text.split()]
    if not words:
        return 0.0
    positive = sum(1 for word in words if word in POSITIVE_WORDS)
    negative = sum(1 for word in words if word in NEGATIVE_WORDS)
    score = (positive - negative) / math.sqrt(len(words))
    return max(min(round(score, 2), 1.0), -1.0)


def detect_emotion(text: str) -> tuple[str | None, str | None]:
    words = [word.strip(".,;:!¿?¡").lower() for word in text.split()]
    candidates = [EMOTION_MAP[word] for word in words if word in EMOTION_MAP]
    if not candidates:
        return None, None
    counter = Counter(candidates)
    (emotion, category), _ = counter.most_common(1)[0]
    return emotion, category


def analyze_diary_entry(text: str) -> Dict[str, Any]:
    resumen = summarize_text(text)
    emocion, categoria = detect_emotion(text)
    sentimiento = estimate_sentiment_score(text)
    return {
        "resumen_ia": resumen,
        "emocion_predominante": emocion,
        "categoria_emocional": categoria,
        "promedio_sentimiento": sentimiento,
        "fuente_modelo": "heuristic-v1",
    }


def analyze_chat_message(text: str) -> Dict[str, Any]:
    emocion, categoria = detect_emotion(text)
    sentiment = estimate_sentiment_score(text)
    resumen = summarize_text(text, max_chars=160)
    return {
        "sentiment": sentiment,
        "emotions": [emocion] if emocion else [],
        "summary": resumen,
        "category": categoria,
        "safety": {"flag": False},
    }
