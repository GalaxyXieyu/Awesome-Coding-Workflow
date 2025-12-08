---
name: langgraph-agent
description: 基于 LangGraph 构建生产级 Agent，涵盖 State/Node/Router/HITL 模式
tags:
  - langgraph
  - agent
  - state-machine
  - workflow
  - hitl
---

# LangGraph Agent 开发专家

## 角色定位

作为 LangGraph Agent 开发专家，负责设计与实现基于 LangGraph 的智能 Agent。遵循以下核心原则：
- **Graph 结构清晰**：节点单一职责、边显式声明、路由逻辑集中
- **State 设计优先**：先定义完整 State，再设计节点与流转
- **流式输出必备**：所有 LLM 输出必须经过 Writer 推送
- **中断可恢复**：支持 HITL 的 interrupt/resume 机制
- **业务语义优先**：命名使用业务术语而非技术术语（如 `记忆助手` 而非 `context_manager`）
- **端到端一致性**：Graph/Router/Writer/Config 中的节点名必须完全一致

## 触发场景

- 用户请求"创建 Agent"、"设计 LangGraph 流程"
- 需要实现多节点协作的智能体
- 需要 HITL（人机交互）审批流程
- 需要流式输出与状态持久化

## 开发步骤

### Phase 1: 设计（先想清楚再动手）

1. **梳理 Graph 逻辑**
   - 画出节点流转图（可用 Mermaid/手绘）
   - 明确每个节点的职责和输入输出
   - 确定路由条件和分支逻辑
   - 标记 HITL 中断点位置（如需要）

2. **设计 State**
   - 参考 `references/state-template.md`
   - 根据 Graph 流转确定需要哪些字段
   - 定义字段类型和默认值

### Phase 2: 实现（自底向上）

3. **实现 Tools**
   - 参考 `references/tools-template.md`
   - 特有工具写在 `tools.py`
   - 通用工具放 `_shared/` 按功能分文件
   - **在 test.ipynb 中单独测试每个 Tool**，使用 `wprint` 工具查看结果：
     ```python
     # test.ipynb 中的 Tool 测试 Cell
     import asyncio
     from src.application.agents.my_agent.tools import my_tool
     from src.infrastructure.logging.wprint import wprint

     async def test_tool():
         result = await my_tool.ainvoke({"param": "test"})
         wprint("Tool Result", result)  # 格式化打印，便于阅读

     await test_tool()
     ```

4. **实现 Nodes**
   - 参考 `references/node-template.md`
   - 每个节点单一职责
   - 先实现核心逻辑，再加 Writer 输出

5. **实现 Router**
   - 参考 `references/router-template.md`
   - 路由返回值必须是中文节点名
   - 路由逻辑集中管理

6. **构建 Graph**
   - 参考 `references/graph-template.md`
   - 按设计图连接节点和边
   - 实现 `get_graph_info()`

### Phase 3: 验证

7. **单元测试（在 test.ipynb 中执行）**
   - Tools 单独测试（invoke/ainvoke）
   - Nodes 单独测试（mock state）
   - Router 逻辑测试
   - 使用 `wprint` 工具查看结果，格式清晰易读

8. **集成测试（在 test.ipynb 中执行）**
   - 完整流程跑通
   - HITL 中断/恢复测试（如需要）
   - 边界情况和异常处理
   - 使用 `wprint` 工具追踪每个阶段的输出

### 开发顺序总结

```
Graph 设计 -> State 定义 -> Tools 实现 -> Tools 测试
                                              |
                                              v
集成测试 <- Graph 构建 <- Router <- Nodes 实现
```

## 输出规范

### 目录结构
```
src/application/agents/
├── _shared/                # 共享工具（按功能分文件）
│   ├── __init__.py
│   ├── web_search.py       # 网络搜索
│   ├── knowledge.py        # 知识库检索
│   ├── data_query.py       # 数据查询
│   ├── graph_search.py     # 图谱检索
│   └── file_generator.py   # 文件生成
└── <agent_name>/
    ├── __init__.py         # 仅导出 AGENT_CONFIG
    ├── state.py            # State 定义
    ├── graph.py            # Graph 构建 + get_graph_info
    ├── router.py           # 路由逻辑
    ├── nodes.py            # 节点实现
    ├── tools.py            # Agent 专属工具
    ├── test.ipynb          # Jupyter 测试notebook（使用 wprint 工具）
    └── README.md           # Agent 文档
```

### AGENT_CONFIG 格式
```json
{
  "name": "agent_name",
  "display_name": "中文显示名",
  "description": "功能描述",
  "version": "1.0.0",
  "tags": [],
  "enabled": true
}
```

## 约束条件

- **LLM 调用规范**
  - 必须使用项目内置的 `get_model_router().build_llm()`，禁止自己封装
  - `model_id` 从 state 获取，不要硬编码
  ```python
  from src.infrastructure.ai.models.router import get_model_router
  
  router = get_model_router()
  llm = router.build_llm(model_id=state.get("model_id"), temperature=0.1)
  response = await llm.ainvoke(messages)
  ```

- **命名规范**
  - 节点名（add_node）：中文业务术语（`"记忆助手"` 而非 `"context_manager"`）
  - 函数名：`xxx_node`（小写下划线）
  - 工具函数：`xxx_tool`（小写下划线）
  - 工具导出：`AGENT_NAME_TOOLS`（大写下划线）
  - Agent名：小写下划线（`my_agent`）
  - **关键：Graph/Router/Writer 中的节点名必须完全一致**

- **必须遵守**
  - State 必须继承 BaseGraphState
  - 用户输入字段统一用 `query`
  - 累加字段用 `Annotated[List[...], add]`
  - 有模型输出必须用 Writer
  - 路由返回值必须与中文节点名一致（关键！）
  - 所有节点在 Graph/Router/Writer/Config 中保持命名一致

- **禁止事项**
  - 不要在 `__init__.py` 导出 workflow/State
  - 不要硬编码 model_id，必须从 state 获取
  - 不要跳过 Writer 直接 print，所有输出都用 Writer
  - 不要自己封装 LLM 调用，使用 `get_model_router().build_llm()`
  - **最重要**：不要混用英文和中文节点名（不一致会导致 interrupt_before 等配置失效）

## 测试最佳实践

### test.ipynb 结构

每个 Agent 都应该有 `test.ipynb`，用于快速验证和调试。使用 `wprint` 工具格式化输出：

```python
# 导入必要模块
from langgraph.checkpoint.memory import InMemorySaver
from src.application.agents.my_agent.graph import workflow
from src.infrastructure.ai.agent.memory.store import initialize_store
from src.infrastructure.ai.agent.writer.debug import wprint
import time

# 配置
config = {"configurable": {"thread_id": f"my_agent_{int(time.time())}"}}

# 编译图
checkpointer = InMemorySaver()
store = await initialize_store()
app = workflow.compile(
    checkpointer=checkpointer,
    store=store,
    interrupt_before=["人工审核"]  # 如需要在中断点停止
)

# 测试查询
state = {
    "query": "用户查询",
    "model_id": "gpt-4o",
    "auto": True,  # 自动执行或需要人工审核
}

# 运行工作流，使用 wprint 查看结果
async for chunk in app.astream(
    state,
    config=config,
    stream_mode=["custom"],
):
    wprint(chunk)  # 格式化输出，便于阅读
```

### wprint 工具的优势

- ✅ **美观的格式化输出**：自动缩进和着色
- ✅ **结构化显示**：清晰展示 Dict、List 等复杂数据结构
- ✅ **易于调试**：快速定位数据和流程问题
- ✅ **高效阅读**：相比 `print()` 节省时间

## 参考资料

详细代码模板见 `references/` 目录（基于 `deepresearch` Agent 真实代码）：
- `state-template.md` - State 定义模板
- `tools-template.md` - Tools 实现模板
- `node-template.md` - 节点实现模板
- `graph-template.md` - Graph 构建模板
- `router-template.md` - 路由设计模板
- `hitl-template.md` - HITL 模式模板
- `test-template.md` - 测试代码模板
- `checklist.md` - 规范检查清单

真实参考实现：
- `src/application/agents/deepresearch/` - 完整 Agent 示例
