# 规范检查清单

创建新 Agent 时，逐项检查：

## `__init__.py`

- [ ] 只导出 `AGENT_CONFIG`，不导出 `workflow`/`State`
- [ ] `AGENT_CONFIG` 包含：
  - [ ] `name`
  - [ ] `display_name`
  - [ ] `description`
  - [ ] `version`
  - [ ] `tags`
  - [ ] `enabled`

## `state.py`

- [ ] State 类继承 `BaseGraphState`
- [ ] 用户输入字段用 `query`（不用 `question`）
- [ ] 包含核心字段：
  - [ ] `graph_type`
  - [ ] `query`
  - [ ] `session_id`
  - [ ] `user_id`
  - [ ] `messages`
  - [ ] `history`
  - [ ] `model_id`
  - [ ] `params`
- [ ] 累加字段用 `Annotated[List[...], add]`

## `graph.py`

- [ ] 使用 `workflow.set_entry_point()` 设置入口
- [ ] 节点名使用中文：`add_node("中文名", node_func)`
- [ ] 实现 `get_graph_info()` 函数
- [ ] `get_graph_info()` 必须字段：
  - [ ] `name`
  - [ ] `display_name`
  - [ ] `description`
  - [ ] `version`
  - [ ] `nodes`（中文列表）
  - [ ] `entry_point`（中文）

## `router.py`

- [ ] 路由函数返回值与 `add_node` 中文名一致
- [ ] `add_conditional_edges` 映射字典用中文节点名
- [ ] 使用 `Literal[...]` 类型标注
- [ ] 提供合理的默认返回值

## `nodes.py`

- [ ] 有模型输出必须用 `create_stream_writer()`
- [ ] 使用 `@track_execute` 装饰业务节点
- [ ] 上下文管理节点命名 `context_manager_node`
- [ ] 节点返回结构化 dict
- [ ] model_id 从 state 获取，不硬编码

## `tools.py`

- [ ] 使用 `@tool` 装饰器
- [ ] 所有函数为 `async` 异步函数
- [ ] docstring 清晰描述功能
- [ ] 统一返回格式：
  - [ ] 成功：`{"success": True, "data": ..., "message": ...}`
  - [ ] 失败：`{"success": False, "error": ...}`
- [ ] 所有异常被捕获并返回统一格式
- [ ] 导出列表命名：`AGENT_NAME_TOOLS`
- [ ] 辅助函数以 `_` 开头（私有）
- [ ] 不在 tool 中直接 print

## `_shared/base_tools.py`（共享工具）

- [ ] 仅放可复用的通用工具
- [ ] 遵循与 `tools.py` 相同规范

## 命名规范

- [ ] 节点名（add_node）：中文（`"上下文管理"`）
- [ ] 函数名（nodes.py）：`xxx_node`
- [ ] 工具函数（tools.py）：`xxx_tool`
- [ ] 工具导出：`AGENT_NAME_TOOLS`
- [ ] 路由函数：`route_xxx` 或 `decide_xxx`
- [ ] Agent 名称：小写下划线（`my_agent`）

## 测试

- [ ] 基础流程测试通过
- [ ] HITL 流程测试通过（如适用）
- [ ] 错误处理测试通过

## 文档

- [ ] README.md 存在
- [ ] 包含架构说明
- [ ] 包含运行指引
