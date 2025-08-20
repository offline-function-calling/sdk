import os
import inspect
import importlib.util

from pathlib import Path
from typing import Callable, Dict, List, Any


class ToolManager:
    """Manages loading and executing Python functions as tools."""

    def __init__(self, tool_dirs: List[str] = None):
        self.tools: Dict[str, Callable] = {}
        self.tool_dirs = tool_dirs
        self.reload_tools()

    def _load_tools_from_directory(self, directory: str):
        path = Path(directory)
        if not path.is_dir():
            return

        for file_path in path.glob("*.py"):
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, func in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_") and func.__doc__:
                    self.add_tool(func)

    def reload_tools(self):
        if self.tool_dirs:
            for tool_dir in self.tool_dirs:
                self._load_tools_from_directory(tool_dir)
        return len(self.tools)

    def add_tool(self, func: Callable):
        self.tools[func.__name__] = func

    def get_tools(self) -> List[Callable]:
        return list(self.tools.values())

    def execute_tool(self, name: str, kwargs: Dict) -> Any:
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        try:
            return self.tools[name](**kwargs)
        except Exception as e:
            return f"Error executing tool '{name}': {e}"
