# Graph 构建模板

> 参考实现：`src/application/agents/deepresearch/graph.py`

## 完整 Graph 示例

```python
"""
Deep Research Graph 流程定义
支持多类型流式输出的深度研究分析图
"""

from langgraph.graph import END, StateGraph
from langgraph.types import CachePolicy
from src.infrastructure.ai.agent.memory.cache import question_key
from src.application.agents.deepresearch.state import DeepResearchState
from src.application.agents.deepresearch.nodes import (
    context_manager_node,
    mode_router_node,
    react_agent_node,
    followup_suggestions_node,
    planning_node,
    plan_router_node,
    searching_node,
    analyzing_node,
    coding_node,
    writing_node,
    summarizing_node,
)
from src.application.agents.deepresearch.router import (
    route_from_mode,
    route_from_plan,
)

# 创建状态图
workflow = StateGraph(DeepResearchState)
workflow.set_entry_point("上下文管理")

# ========== 添加所有节点（使用中文名称便于前端显示）==========
workflow.add_node("上下文管理", context_manager_node)
workflow.add_node("模式路由", mode_router_node)
workflow.add_node("快速问答", react_agent_node)
workflow.add_node("任务规划", planning_node)
workflow.add_node("计划路由", plan_router_node)
workflow.add_node(
    "信息搜索",
    searching_node,
    cache_policy=CachePolicy(ttl=86400, key_func=question_key),  # 带缓存
)
workflow.add_node("数据分析", analyzing_node)
workflow.add_node("代码执行", coding_node)
workflow.add_node("报告撰写", writing_node)
workflow.add_node("结果总结", summarizing_node)
workflow.add_node("追问建议", followup_suggestions_node)

# ========== 入口边 ==========
workflow.add_edge("上下文管理", "模式路由")

# ========== 直接边 ==========
workflow.add_edge("任务规划", "信息搜索")
workflow.add_edge("信息搜索", "计划路由")
workflow.add_edge("数据分析", "计划路由")
workflow.add_edge("代码执行", "计划路由")
workflow.add_edge("报告撰写", "结果总结")
workflow.add_edge("快速问答", "追问建议")
workflow.add_edge("结果总结", "追问建议")
workflow.add_edge("追问建议", END)

# ========== 条件边：模式路由 ==========
workflow.add_conditional_edges(
    "模式路由",
    route_from_mode,
    {
        "任务规划": "任务规划",
        "快速问答": "快速问答",
    }
)

# ========== 条件边：计划路由 ==========
workflow.add_conditional_edges(
    "计划路由",
    route_from_plan,
    {
        "信息搜索": "信息搜索",
        "数据分析": "数据分析",
        "代码执行": "代码执行",
        "报告撰写": "报告撰写",
        "结果总结": "结果总结"
    }
)
```

## get_graph_info 实现

```python
def get_graph_info() -> dict:
    """获取图的基本信息"""
    return {
        # === 必须字段 ===
        "name": "deepresearch",
        "display_name": "深度研究分析",
        "description": "智能深度研究分析图，支持两种执行模式：deep(完整工作流)、react(轻量Agent)",
        "version": "1.0.0",
        "nodes": [
            "上下文管理",
            "模式路由",
            "快速问答",
            "任务规划",
            "计划路由",
            "信息搜索",
            "数据分析",
            "代码执行",
            "报告撰写",
            "结果总结",
            "追问建议",
        ],
        "entry_point": "上下文管理",
        # === 可选字段 ===
        "features": [
            "两种执行模式切换",
            "计划驱动执行",
            "智能路径选择",
            "动态阶段跳过",
        ],
        "message_types": [
            "plan", "thinking", "search", "content",
            "tool_result", "code", "markdown", "file", "summary"
        ],
        "interrupt_before": [],
    }
```

## __init__.py 配置

```python
"""Deep Research 服务配置"""

AGENT_CONFIG = {
    "name": "deepresearch",
    "display_name": "深度研究分析",
    "description": "多工具的研究报告生成",
    "version": "1.0.0",
    "tags": ["research", "search", "analysis", "file_generation", "streaming"],
    "enabled": True,
    "dependencies": []
}
```

**注意**：`__init__.py` 只导出 `AGENT_CONFIG`，不导出 `workflow`、`State`。

## 流程图

```
                    Entry
                      │
                      ▼
                 上下文管理
                      │
                      ▼
                 模式路由
                /         \
               ▼           ▼
          任务规划      快速问答
              │             │
              ▼             │
          信息搜索          │
              │             │
              ▼             │
          计划路由 ◄────┐   │
         /  |  |  \    │   │
        ▼   ▼   ▼   ▼  │   │
      搜索 分析 代码 撰写│   │
        │   │   │   │  │   │
        └───┴───┴───┘  │   │
              │        │   │
              ▼────────┘   │
          结果总结         │
              │            │
              └────┬───────┘
                   ▼
              追问建议
                   │
                   ▼
                  END
```
