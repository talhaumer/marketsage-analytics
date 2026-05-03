"""Shared prompt construction for all analysis agents."""
from typing import List


_INJECTION_CHARS = str.maketrans({
    "{": "(",
    "}": ")",
    "<": "&lt;",
    ">": "&gt;",
})


def sanitize(text: str, max_len: int = 1000) -> str:
    if not text:
        return ""
    return text[:max_len].translate(_INJECTION_CHARS)


def build_prompt(
    role: str,
    question: str,
    symbols: List[str],
    timeframe: str,
    data_summary: str,
    analysis_points: List[str],
    max_question_len: int = 500,
    max_data_len: int = 3000,
) -> str:
    safe_question = sanitize(question, max_question_len)
    safe_symbols = [sanitize(s, 20) for s in (symbols or [])]
    safe_data = sanitize(data_summary, max_data_len)
    points_text = "\n".join(
        f"{i + 1}. {point}" for i, point in enumerate(analysis_points)
    )
    symbols_str = ", ".join(safe_symbols) if safe_symbols else "general market"

    return (
        f"You are a {role}. Analyze the following information.\n\n"
        f"**Question:** {safe_question}\n"
        f"**Symbols:** {symbols_str}\n"
        f"**Timeframe:** {timeframe or '1mo'}\n\n"
        f"**Data:**\n{safe_data}\n\n"
        f"**Provide a professional markdown analysis covering:**\n{points_text}\n\n"
        "Be specific, data-driven, and actionable. Cite numbers where available."
    )
