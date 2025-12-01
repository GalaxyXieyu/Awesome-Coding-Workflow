---
name: langgraph-agent
description: 基于 LangGraph 构建生产级 Agent，涵盖 State/Node/Router/HITL 模式
---

# LangGraph Agent 开发专家

## 角色定位

作为 LangGraph Agent 开发专家，负责设计与实现基于 LangGraph 的智能 Agent。遵循以下核心原则：
- Graph 结构清晰：节点单一职责、边显式声明、路由逻辑集中
- State 设计优先：先定义完整 State，再设计节点与流转
- 流式输出必备：所有 LLM 输出必须经过 Writer 推送
- 中断可恢复：支持 HITL 的 interrupt/resume 机制

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
   - **单独测试每个 Tool**：
     ```python
     # 测试脚本（通过后删除）
     import asyncio
     from tools import my_tool
     
     async def test():
         result = await my_tool.ainvoke({"param": "test"})
         print(result)
     
     asyncio.run(test())
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

7. **单元测试**
   - Tools 单独测试（invoke/ainvoke）
   - Nodes 单独测试（mock state）
   - Router 逻辑测试

8. **集成测试**
   - 完整流程跑通
   - HITL 中断/恢复测试（如需要）
   - 边界情况和异常处理

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
    ├── tools.py            # Agent 专属工具（单文件，从 _shared 导入通用工具）
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

- **命名规范**
  - 节点名（add_node）：中文（`"上下文管理"`）
  - 函数名：`xxx_node`（小写下划线）
  - 工具函数：`xxx_tool`（小写下划线）
  - 工具导出：`AGENT_NAME_TOOLS`（大写下划线）
  - Agent名：小写下划线（`my_agent`）

- **必须遵守**
  - State 必须继承 BaseGraphState
  - 用户输入字段统一用 `query`
  - 累加字段用 `Annotated[List[...], add]`
  - 有模型输出必须用 Writer
  - 路由返回值必须与中文节点名一致

- **禁止事项**
  - 不要在 `__init__.py` 导出 workflow/State
  - 不要硬编码 model_id，必须从 state 获取
  - 不要跳过 Writer 直接 print

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
