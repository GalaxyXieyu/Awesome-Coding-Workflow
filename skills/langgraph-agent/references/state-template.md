# State 定义模板

> 参考实现：`src/application/agents/deepresearch/state.py`

## 完整 State 示例

```python
"""
Deep Research Graph 状态定义.
支持多类型流式输出的深度研究分析状态管理
"""

from typing import Annotated, Optional, List, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from src.infrastructure.ai.agent.state.base_state import BaseGraphState


class DeepResearchState(BaseGraphState):
    """深度研究Graph的状态定义
    
    核心设计：
    - 统一输出管理：outputs 字段自动累加所有节点输出
    - 任务跟踪系统：tasks 列表管理任务状态和进度
    - 自动化装饰器：@track_execute 自动管理任务状态
    """

    # ========== 基本信息 ==========
    graph_type: str                              # 固定为 agent 名称
    query: Optional[str]                         # 用户输入（统一用 query）
    session_id: Optional[str]
    user_id: Optional[str]
    messages: Optional[List[BaseMessage]]        # 会话窗口（本轮压缩后）
    history: Annotated[List[BaseMessage], add]   # 跨轮完整抄本（追加聚合）

    # ========== 模型切换支持 ==========
    model_id: Optional[str]                      # 指定使用的模型
    params: Optional[Dict[str, Any]]             # 模型推理参数

    # ========== 统一输出管理 ==========
    outputs: Annotated[List[Dict[str, Any]], add]  # 节点输出自动累加

    # ========== 任务管理系统 ==========
    tasks: Optional[List[Dict[str, Any]]]        # 任务列表
    current_task_id: Optional[int]               # 当前执行任务ID
    overall_progress: Optional[int]              # 整体进度 0-100

    # ========== 流程控制 ==========
    mode: Optional[str]                          # 执行模式 "deep" | "react"
    auto: Optional[bool]                         # 工具自动运行（True=copilot，False=interactive）
    current_node: Optional[str]
    errors: Annotated[List[Dict[str, Any]], add] # 错误信息自动累加

    # ========== 执行次数控制 ==========
    execution_counts: Optional[Dict[str, int]]   # 各节点执行次数
    max_executions: Optional[Dict[str, int]]     # 最大执行次数限制

    # ========== 路由决策 ==========
    router_decision: Optional[Dict[str, Any]]    # 路由器决策详情

    # ========== 用户配置 ==========
    user_preferences: Optional[Dict[str, Any]]   # 用户偏好
    output_format: Optional[str]                 # 输出格式 ("markdown", "pdf", "html")
    research_depth: Optional[str]                # 研究深度 ("shallow", "medium", "deep")

    # ========== 扩展字段 ==========
    custom_data: Optional[Dict[str, Any]]        # 自定义数据
    stats: Optional[Dict[str, Any]]              # 统计信息（窗口/压缩等）
```

## 辅助函数

### 节点输出获取

```python
def get_node_output(state: Dict[str, Any], node_name: str, default: Any = None) -> Any:
    """从 outputs 列表中获取指定节点的最新输出"""
    outputs = state.get("outputs", [])
    for output in reversed(outputs):
        if output.get("node") == node_name:
            return output
    return default
```

### 执行次数控制

```python
def increment_execution_count(state: Dict[str, Any], node: str) -> Dict[str, Any]:
    """增加节点执行次数"""
    if "execution_counts" not in state:
        state["execution_counts"] = {}
    state["execution_counts"][node] = state["execution_counts"].get(node, 0) + 1
    state["current_node"] = node
    return state

def can_execute_node(state: Dict[str, Any], node: str) -> bool:
    """检查节点是否可以执行（未达到次数限制）"""
    current_count = state.get("execution_counts", {}).get(node, 0)
    max_count = state.get("max_executions", {}).get(node, 3)
    return current_count < max_count
```

### 任务进度计算

```python
def _calculate_progress(tasks: List[Dict]) -> int:
    """计算整体进度百分比"""
    if not tasks:
        return 0
    completed = len([t for t in tasks if t["status"] == "completed"])
    return int((completed / len(tasks)) * 100)

def _update_task(tasks: List[Dict], task_id: int, **updates) -> List[Dict]:
    """不可变方式更新任务状态"""
    return [
        {**task, **updates} if task["id"] == task_id else task
        for task in tasks
    ]
```

## 设计原则

| 原则 | 说明 |
|------|------|
| **字段命名统一** | 用户输入用 `query`，不用 `question` |
| **累加字段标注** | 需追加的字段用 `Annotated[List[...], add]` |
| **必须继承基类** | `BaseGraphState` 提供通用字段 |
| **类型完整标注** | 所有字段必须有类型声明 |
| **分组注释** | 用 `# ==========` 分隔不同功能的字段组 |
