from __future__ import annotations

from .brain import ask_jarvis
from .rag import format_context, retrieve_context
from .tools import try_local_tool


def handle_user_text(user_text: str) -> str:
    tool_result = try_local_tool(user_text)
    if tool_result.handled:
        return tool_result.message

    chunks = retrieve_context(user_text)
    context_text = format_context(chunks)
    return ask_jarvis(user_text, context_text=context_text)
