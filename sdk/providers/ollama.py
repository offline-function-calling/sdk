from typing import List, AsyncIterator, Dict, Callable, Any
from ollama import AsyncClient, ResponseError

from sdk.types import Message, Part, ToolCall, Model
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """Async provider for Ollama models."""

    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.client = AsyncClient(host)

    def _format_message(self, message: Message) -> Dict[str, Any]:
        formatted = {
            "role": message.role,
            "content": "",
            "images": [],
            "tool_calls": []
        }

        for part in message.parts:
            if part.kind == "text":
                formatted["content"] += part.data
            elif part.kind == "file":
                if part.data.mime.startswith("image/"):
                    formatted["images"].append(part.data.contents)
                else:
                    header = "=" * 13
                    formatted["content"] += f"\n\n{header}\nFile: {part.data.name}\n{header}\n"
            elif part.kind == "tool_call":
                formatted["tool_calls"].append({
                    "id": part.data.id,
                    "function": {
                        "name": part.data.tool,
                        "arguments": part.data.parameters,
                    }
                })

        return formatted

    async def chat(
        self, messages: List[Message], tools: List[Callable] = None
    ) -> AsyncIterator[Part]:
        stream = await self.client.chat(
            model=self.model,
            messages=[self._format_message(m) for m in messages],
            tools=tools,
            stream=True,
            options={"num_ctx": 32000},
        )

        async for chunk in stream:
            if tool_calls := chunk["message"].get("tool_calls"):
                for tool_call in tool_calls:
                    yield Part(kind="tool_call", data=ToolCall(
                        id=None,
                        tool=tool_call.function.name,
                        parameters=tool_call.function.arguments or {},
                    ))
            elif content := chunk["message"].get("content"):
                yield Part(kind="text", data=content)

    async def details(self) -> Model:
        try:
            info = await self.client.show(self.model)
            return Model(
                name=self.model,
                details=info.get("details", {}),
                capabilities=info.get("capabilities", []),
            )
        except ResponseError as e:
            raise ConnectionError(
                f"Could not connect to Ollama or model '{self.model}' not found."
            ) from e
