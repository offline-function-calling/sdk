from abc import ABC, abstractmethod
from typing import List, Iterator, Union, Dict, Callable

from sdk.types import Message, Model


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str, **kwargs):
        self.model = model

    @abstractmethod
    def chat(
        self, messages: List[Message], tools: List[Callable] = None
    ) -> Iterator[Union[str, List[Dict]]]:
        """
        Main method for interacting with the LLM. It should provide a
        streaming response by yielding chunks of text or tool calls.
        """
        pass

    @abstractmethod
    def details(self) -> Model:
        """
        Returns a dictionary with the details and capabilities of the
        model currently in use.
        """
        pass
