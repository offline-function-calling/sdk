from pathlib import Path
from typing import List, Optional, AsyncIterator, Union, Dict, Any

from .types import Message, ToolCall, Part
from .providers.base import BaseProvider
from .tools import ToolManager


class Agent:
    """
    An agent for interacting with an offline, function-calling enabled
    large language model. Handles the setup of tools, system prompts,
    and the underlying provider.
    """

    def __init__(
        self,
        provider: BaseProvider,
        prompt: Optional[str] = None,
        tools: Optional[Union[str, List[str]]] = None,
    ):
        self.model_provider = provider
        self.system_prompt = prompt
        self.history: List[Message] = []

        self.file_manager: FileManager()
        self.tool_dirs = [tools] if isinstance(tools, str) else tools or []
        self.tool_manager = ToolManager(self.tool_dirs)

        self._is_initialized = False

    def clear_history(self):
        """Resets the conversation history, preserving the system prompt."""
        self.history.clear()
        if self.system_prompt:
            self.history.append(Message(role="system", content=self.system_prompt))

    async def describe_model(self) -> Dict[str, Any]:
        """Gets model details from the provider."""
        return await self.model_provider.details()

    async def stream_response(
        self, prompt: Optional[str], files: Optional[List[str]] = None
    ) -> AsyncIterator[Part]:
        """
        Generates and streams a response from the model. If a prompt is
        provided, it starts a new user turn. If prompt is `None`, it
        continues the conversation, assuming that tool results have been
        added to history.
        """
        parts = []

        if prompt is not None:
            parts += [Part(kind="text", data=prompt)]

        if files is not None and len(files) > 0:
            files = self.file_manager.process_files(files)
            parts += [Part(kind="file", data=file) for file in files]

        if len(parts) > 0:
            self.history.append(Message(role="user", parts=parts))

        tools = self.tool_manager.get_tools()
        stream = self.model_provider.chat(self.history, tools)

        full_response = ""
        tool_calls = []

        async for part in stream:
            if part.kind == "text":
                full_response += part.data
                yield part
            elif part.kind == "tool_call":
                tool_calls.append(part.data)
                # yield the tool calls at the end

        parts = [Part(kind="text", data=full_response), *tool_calls]
        self.history.append(Message(role="assistant", parts=parts))

        if tool_calls:
            for call in tool_calls:
                yield call
