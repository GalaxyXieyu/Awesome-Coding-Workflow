# Tools 实现模板

## 文件结构

```
agents/
├── _shared/                    # 共享工具（按功能分文件）
│   ├── __init__.py
│   ├── web_search.py           # 网络搜索
│   ├── graph_search.py         # 图谱检索
│   ├── knowledge.py            # 知识库检索
│   ├── data_query.py           # 数据查询
│   └── file_generator.py       # 文件生成
└── <agent_name>/
    ├── __init__.py
    ├── state.py
    ├── graph.py
    ├── nodes.py
    ├── router.py
    └── tools.py                # Agent 专属工具（单文件，从 _shared 导入通用工具）
```

**原则**：
- `_shared/` 按功能域分文件，命名直接用功能名（不要 `base_tools.py`、`xxx_tool.py`）
- 单个 Agent 用一个 `tools.py` 保持扁平，不要 `tools/` 目录
- 特有工具定义在 `tools.py`，通用工具从 `_shared` 导入并 re-export

## Agent 专属 Tools (`tools.py`)

```python
"""<Agent Name> Tools

面向 <Agent> 的专属工具集，封装特定领域的业务逻辑。
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from src.infrastructure.logging import get_logger
# 导入需要的 domain services
from src.domain.services.xxx import (
    some_service_function,
)

logger = get_logger(__name__)


# ============================================================================
# Agent Tools
# ============================================================================


@tool
async def query_something_tool(
    param1: str,
    param2: int = 10,
    param3: Optional[List[str]] = None,
) -> str:
    """工具功能描述（会作为 LLM 的 tool description）
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        param3: 参数3说明
    
    Returns:
        查询结果
    """
    try:
        result = await some_service_function(
            param1=param1,
            param2=param2,
        )
        
        if not result:
            return {
                "success": False,
                "error": f"未找到数据: {param1}",
            }
        
        return {
            "success": True,
            "data": result,
            "message": f"成功查询: {param1}",
        }
    except Exception as e:
        logger.error(f"查询失败: {e}")
        return {
            "success": False,
            "error": f"查询失败: {str(e)}",
        }


@tool
async def complex_analysis_tool(
    company_name: str,
    window_days: int = 90,
    include_extra: bool = True,
) -> str:
    """复杂分析工具示例（多个异步任务并发）"""
    try:
        # 构建并发任务
        task_map = {
            "basic": query_basic_info(company_name),
            "detail": query_detail_info(company_name, window_days),
        }
        if include_extra:
            task_map["extra"] = query_extra_info(company_name)
        
        # 并发执行
        results = await asyncio.gather(*task_map.values(), return_exceptions=True)
        
        # 处理结果
        resolved: Dict[str, Any] = {}
        for key, value in zip(task_map.keys(), results):
            if isinstance(value, Exception):
                logger.error(f"{key} 查询失败: {value}")
                resolved[key] = {}
            else:
                resolved[key] = value or {}
        
        # 聚合数据
        summary = _build_summary(resolved)
        
        return {
            "success": True,
            "data": {
                "company": company_name,
                "basic": resolved.get("basic", {}),
                "detail": resolved.get("detail", {}),
                "extra": resolved.get("extra", {}),
                "summary": summary,
            },
            "message": f"分析完成: {company_name}",
        }
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return {
            "success": False,
            "error": f"分析失败: {str(e)}",
        }


# ============================================================================
# 辅助函数（不加 @tool 装饰器）
# ============================================================================


def _build_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """构建汇总信息"""
    return {
        "basic_count": len(data.get("basic", [])),
        "detail_count": len(data.get("detail", [])),
    }


def _filter_items(items: List[Dict], filter_types: List[str]) -> List[Dict]:
    """过滤数据项"""
    if not filter_types:
        return items
    return [item for item in items if item.get("type") in filter_types]


# ============================================================================
# Tools 导出
# ============================================================================

AGENT_NAME_TOOLS = [
    query_something_tool,
    complex_analysis_tool,
]
```

## 共享 Tools (`_shared/`)

按功能分文件，每个文件负责一个领域：

```
_shared/
├── __init__.py         # 统一导出
├── graph_search.py     # 图谱检索（公司、行业、主题等）
├── knowledge.py        # 知识库向量检索
├── data_query.py       # 数据查询（SQL + 经济数据）
├── web_search.py       # 网络搜索
└── file_generator.py   # 文件生成
```

**`_shared/__init__.py` 示例**：
```python
"""共享工具模块

按功能分文件：
- graph_search.py    图谱检索
- knowledge.py       知识库检索
- data_query.py      数据查询
- web_search.py      网络搜索
- file_generator.py  文件生成
"""

from .graph_search import (
    search_company_tool,
    search_industry_tool,
    GRAPH_SEARCH_TOOLS,
)
from .knowledge import (
    knowledge_search,
    KNOWLEDGE_TOOLS,
)
from .data_query import (
    data_query,
    DATA_QUERY_TOOLS,
)
from .web_search import web_search_tool
from .file_generator import file_tool

__all__ = [
    # 图谱检索
    "search_company_tool",
    "search_industry_tool",
    "GRAPH_SEARCH_TOOLS",
    # 知识库
    "knowledge_search",
    "KNOWLEDGE_TOOLS",
    # 数据查询
    "data_query",
    "DATA_QUERY_TOOLS",
    # 网络搜索
    "web_search_tool",
    # 文件生成
    "file_tool",
]
```

## Agent Tools 完整示例 (`tools.py`)

```python
# <agent_name>/tools.py
"""Agent 特有工具 + 通用工具导入"""

import json
from typing import Optional
from langchain_core.tools import tool

from src.infrastructure.logging import get_logger

# 通用工具（从 _shared 导入）
from src.application.agents._shared import (
    web_search_tool,
    knowledge_search,
    data_query,
    file_tool,
    KNOWLEDGE_TOOLS,
    DATA_QUERY_TOOLS,
)

logger = get_logger(__name__)


# ============================================================================
# 特有工具
# ============================================================================

@tool
async def my_special_tool(param: str) -> str:
    """Agent 特有的工具"""
    try:
        # 业务逻辑
        return {"success": True, "data": param}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# 导出
# ============================================================================

AGENT_TOOLS = [
    # 特有工具
    my_special_tool,
    # 通用工具
    web_search_tool,
    knowledge_search,
    data_query,
    file_tool,
]

__all__ = [
    "my_special_tool",
    "web_search_tool",
    "knowledge_search",
    "data_query",
    "file_tool",
    "AGENT_TOOLS",
]
```

## 在 Node 中使用 Tools

```python
# nodes.py
from langgraph.prebuilt import ToolNode
from .tools import AGENT_TOOLS  # 或直接导入需要的工具

tool_node = ToolNode(AGENT_TOOLS)

async def tool_executor_node(state: AgentState) -> Dict[str, Any]:
    """工具执行节点"""
    return await tool_node.ainvoke(state)
```

## 在 Graph 中绑定 Tools

```python
# graph.py
from .tools import AGENT_TOOLS

def build_graph():
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    # ... 构建 graph
```

## 规范要点

### 命名规范
- 工具函数名：`xxx_tool` 或 `xxx_xxx_tool`（小写下划线）
- 导出列表：`AGENT_NAME_TOOLS`（大写下划线）
- 辅助函数：`_xxx`（下划线开头，表示私有）

### 返回格式
统一使用以下格式：
```python
# 成功
{"success": True, "data": {...}, "message": "描述"}

# 失败
{"success": False, "error": "错误描述"}
```

### 必须遵守
- 使用 `@tool` 装饰器
- 必须是 `async` 函数
- docstring 清晰描述功能（LLM 会看到）
- 所有异常必须捕获并返回统一格式
- 不要在 tool 中直接 print，使用 logger

### 禁止事项
- 不要在 tool 中硬编码配置
- 不要在 tool 中直接操作数据库（通过 domain services）
- 不要返回过大的数据（考虑 token 限制）
