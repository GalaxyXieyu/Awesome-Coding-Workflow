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

## 执行步骤

1. **需求分析**
   - 明确 Agent 目标与使用场景
   - 确定需要哪些节点与工具
   - 确定是否需要 HITL 中断点

2. **State 设计**
   - 参考 `references/state-template.md`
   - 继承 BaseGraphState
   - 定义所有必要字段与类型

3. **Node 实现**
   - 参考 `references/node-template.md`
   - 每个节点单一职责
   - 使用 Writer 输出、@track_execute 装饰

4. **Router 设计**
   - 参考 `references/router-template.md`
   - 路由返回值必须是中文节点名

5. **Graph 构建**
   - 参考 `references/graph-template.md`
   - 节点名使用中文
   - 实现 get_graph_info()

6. **HITL 配置**（如需要）
   - 参考 `references/hitl-template.md`
   - 配置中断点与恢复逻辑

7. **测试验证**
   - 参考 `references/test-template.md`
   - 基础流程测试 + HITL 测试

## 输出规范

### 目录结构
```
src/application/agents/<agent_name>/
├── __init__.py     # 仅导出 AGENT_CONFIG
├── state.py        # State 定义
├── graph.py        # Graph 构建 + get_graph_info
├── router.py       # 路由逻辑
├── nodes.py        # 节点实现
└── README.md       # Agent 文档
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
- `node-template.md` - 节点实现模板
- `graph-template.md` - Graph 构建模板
- `router-template.md` - 路由设计模板
- `hitl-template.md` - HITL 模式模板
- `test-template.md` - 测试代码模板
- `checklist.md` - 规范检查清单

真实参考实现：
- `src/application/agents/deepresearch/` - 完整 Agent 示例
