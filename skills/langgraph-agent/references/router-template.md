# Router 设计模板

> 参考实现：`src/application/agents/deepresearch/router.py`

## 完整 Router 示例

```python
"""
Deep Research Graph 路由逻辑
处理条件边的路由决策
"""

from langgraph.graph import END
from src.application.agents.deepresearch.state import DeepResearchState


# 英文节点名 → 中文节点名映射（集中管理）
NODE_NAME_MAP = {
    "searching": "信息搜索",
    "analyzing": "数据分析",
    "coding": "代码执行",
    "writing": "报告撰写",
    "summarizing": "结果总结",
}


def route_from_mode(state: DeepResearchState) -> str:
    """
    根据模式路由的结果选择路径
    
    Args:
        state: DeepResearchState 状态对象
        
    Returns:
        str: 下一个节点名称 ("快速问答" 或 "任务规划")
    """
    mode = (state.get("mode") or "deep").lower()
    return "快速问答" if mode == "react" else "任务规划"


def route_from_plan(state: DeepResearchState) -> str:
    """
    智能路由决策 - 基于 plan_router 的决策结果
    
    支持以下路由：
    - 信息搜索: 进入搜索阶段
    - 数据分析: 直接进入分析阶段
    - 代码执行: 直接进入代码执行阶段
    - 报告撰写: 直接进入写作阶段
    - 结果总结: 直接进入总结阶段
    - end: 结束流程
    
    Args:
        state: DeepResearchState 状态对象
        
    Returns:
        str: 下一个节点名称或 END
    """
    router_decision = state.get("router_decision", {})
    next_action = router_decision.get("next_action", "writing")

    # 支持重试逻辑
    if next_action.startswith("retry_"):
        action = next_action.replace("retry_", "")
        return NODE_NAME_MAP.get(action, "报告撰写")

    # 支持结束流程
    if next_action == "end":
        return END

    # 正常路由：英文 → 中文
    return NODE_NAME_MAP.get(next_action, "报告撰写")


# 路由配置映射（便于统一管理和查阅）
ROUTE_MAPPING = {
    "模式路由": {
        "router_func": route_from_mode,
        "edges": {
            "任务规划": "任务规划",
            "快速问答": "快速问答",
        }
    },
    "计划路由": {
        "router_func": route_from_plan,
        "edges": {
            "信息搜索": "信息搜索",
            "数据分析": "数据分析",
            "代码执行": "代码执行",
            "报告撰写": "报告撰写",
            "结果总结": "结果总结",
        }
    }
}
```

## 在 Graph 中使用

```python
# 条件边：模式路由
workflow.add_conditional_edges(
    "模式路由",
    route_from_mode,
    {
        "任务规划": "任务规划",
        "快速问答": "快速问答",
    }
)

# 条件边：计划路由
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

## 关键规则

| 规则 | 说明 |
|------|------|
| **返回值** | 必须与 `add_node` 中的中文节点名一致 |
| **映射表集中** | `NODE_NAME_MAP` 集中管理英文→中文映射 |
| **默认值** | 始终提供合理的默认返回值 |
| **支持 END** | 可返回 `END` 常量结束流程 |
| **支持重试** | 通过 `retry_` 前缀支持重试逻辑 |
