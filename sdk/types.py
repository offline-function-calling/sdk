from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field


@dataclass
class File:
    name: str
    uri: str
    mime: str
    contents: str


@dataclass
class ToolError:
    name: str
    description: str


@dataclass
class ToolUseExample:
    prompt: str
    parameters: Dict[str, Any]


@dataclass
class ToolSpecification:
    name: str
    description: str
    parameters: Dict[str, Any]
    responses: Optional[List[Any]]
    errors: Optional[List[ToolError]]
    examples: Optional[List[ToolUseExample]]


@dataclass
class ToolCall:
    id: str
    tool: str
    parameters: Dict[str, Any]


@dataclass
class Part:
    kind: str  # text, media, tool_call
    data: Union[str, File, ToolCall]


@dataclass
class Message:
    role: str
    parts: List[Part]


@dataclass
class Model:
    name: str
    details: Dict[str, Any]
    capabilities: List[str]
