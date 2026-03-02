from __future__ import annotations

from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from langchain_core.tools import BaseTool, StructuredTool


def make_jsonable(x: Any) -> Any:
    if x is None or isinstance(x, (str, int, float, bool)):
        return x
    if isinstance(x, BaseModel):
        return make_jsonable(x.model_dump())
    if isinstance(x, dict):
        return {str(k): make_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [make_jsonable(v) for v in x]
    return repr(x)


def wrap_mcp_tool(tool: BaseTool) -> BaseTool:
    """
    Returns a NEW StructuredTool with the SAME name/description/schema,
    but whose implementation delegates to the underlying MCP tool.

    This avoids BaseTool subclass schema recursion entirely.
    """
    args_schema: Optional[Type[BaseModel]] = getattr(tool, "args_schema", None)

    def _run(**kwargs: Any) -> Any:
        return tool.invoke(make_jsonable(kwargs))

    async def _arun(**kwargs: Any) -> Any:
        return await tool.ainvoke(make_jsonable(kwargs))

    return StructuredTool.from_function(
        name=tool.name,
        description=getattr(tool, "description", "") or "",
        func=_run,
        coroutine=_arun,
        args_schema=args_schema,
    )