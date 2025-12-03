# HITL 中断与恢复模板

> 参考实现：`src/application/agents/deepresearch/nodes.py` - `mode_router_node`

## 节点内触发中断

```python
from langgraph import types
from langgraph.prebuilt.interrupt import HumanInterrupt

async def mode_router_node(state: DeepResearchState) -> Dict[str, Any]:
    """模式路由节点：判定 deep/react 模式，deep 时触发 HITL 确认"""
    
    decided = state.get("mode")

    if decided not in {"deep", "react"}:
        q = extract_question_from_state(state)

        try:
            # LLM 判定模式
            router = get_model_router()
            llm = router.build_llm(state.get("model_id"), **(state.get("params") or {}))
            prompt = await _prompt_manager.abuild_prompt_from_name("intent_classifier")
            resp = await llm.ainvoke(prompt.format_messages(question=q))
            decision = safe_json_parse(getattr(resp, "content", ""), {"mode": "react"})
            suggested = (decision.get("mode") or "react").lower()
            
            # 建议 deep 时进行 HITL 确认
            if suggested == "deep":
                request: HumanInterrupt = {
                    "action_request": {
                        "action": "confirm_deep",
                        "args": {"question": q, "suggested_mode": "deep"}
                    },
                    "config": {
                        "allow_accept": True,
                        "allow_reject": True,
                        "allow_edit": False
                    },
                    "description": (
                        "建议进入【深度研究】模式\n"
                        "- 将执行规划/搜索/分析/写作等多阶段流程\n"
                        "- 若拒绝，将使用【快速问答】\n\n"
                        "请输入 'accept' 或 'reject'"
                    ),
                }
                response = types.interrupt(request)
                
                # 处理响应
                if isinstance(response, (list, tuple)) and response:
                    response = response[-1]
                if isinstance(response, str):
                    response = {"type": response}
                    
                decided = "deep" if response.get("type") == "accept" else "react"
            else:
                decided = "react"
        except Exception:
            decided = "react"

    return {
        "mode": decided or "deep",
        "current_node": "mode_router",
    }
```

## HumanInterrupt 结构

```python
request: HumanInterrupt = {
    "action_request": {
        "action": "confirm_deep",           # 动作类型
        "args": {"question": q}             # 动作参数
    },
    "config": {
        "allow_accept": True,               # 允许接受
        "allow_reject": True,               # 允许拒绝
        "allow_edit": False                 # 允许编辑
    },
    "description": "展示给用户的说明文字",
}
```

## 恢复执行

```python
from langgraph.types import Command

# 接受
await app.astream(Command(resume=[{"type": "accept"}]), config=config)

# 拒绝
await app.astream(Command(resume=[{"type": "reject"}]), config=config)

# 编辑后接受
await app.astream(
    Command(resume=[{"type": "edit", "new_args": {...}}]),
    config=config
)
```

## 异常处理（重要）

```python
from src.infrastructure.ai.agent.tools.wrapper import is_interrupt_exception

try:
    result = await risky_operation()
except Exception as e:
    # 重要：不捕获中断异常，让它透传以支持 HITL
    if is_interrupt_exception(e):
        raise
    writer.error(f"操作失败: {str(e)}")
    return {"errors": [...]}
```

## 编译时配置中断点

```python
# 在指定节点前中断
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["工具执行"]
)
```

## 执行模式

| 模式 | State 字段 | 说明 |
|------|-----------|------|
| `interactive` | `auto=False` | 交互模式，需用户确认 |
| `copilot` | `auto=True` | 协作模式，自动执行 |
