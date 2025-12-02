# Node 实现模板

> 参考实现：`src/application/agents/deepresearch/nodes.py`

## 常用导入

```python
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph import types
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.interrupt import HumanInterrupt

from src.infrastructure.ai.models.router import get_model_router
from src.infrastructure.ai.prompt_management.prompt_manager import PromptManager
from src.application.agents.deepresearch.state import DeepResearchState, track_execute
from src.infrastructure.ai.agent.tools.wrapper import (
    is_interrupt_exception,
    safe_tool_call,
    wrap_tool_by_state,
)
from src.infrastructure.ai.agent.utils.context_compression import (
    CompressionMode, TriggerType, approx_tokens, compress_messages,
)
from src.infrastructure.ai.agent.utils.json_utils import safe_json_parse, serialize_for_llm
from src.infrastructure.ai.agent.utils.message_collector import (
    collect_messages_from_llm_stream,
    extract_question_from_state,
)
from src.infrastructure.ai.agent.writer import create_stream_writer
```

## 上下文管理节点

```python
async def context_manager_node(
    state: DeepResearchState, 
    hard_limit: int = 8000, 
    summarize: bool = True
) -> Dict[str, Any]:
    """
    上下文管理节点 - 使用统一的压缩工具管理对话历史
    
    Args:
        state: 当前状态
        hard_limit: token 硬限制，超过后触发压缩
        summarize: 是否使用 LLM 总结（True）或简单截取（False）
    """
    writer = create_stream_writer(node_name="context_manager", agent_name="deepresearch")
    
    try:
        history = state.get("history", []) or []
        messages = state.get("messages", []) or []
        
        if not history and not messages:
            writer.thinking("上下文管理：无历史记录，跳过压缩")
            return {}
        
        base = history if history else messages
        before_count = len(base)
        before_tokens = approx_tokens(base)
        
        writer.thinking(f"上下文管理：当前 {before_count} 条消息，约 {before_tokens} tokens")
        
        # 获取 LLM 实例
        llm = None
        if summarize:
            try:
                router = get_model_router()
                params = state.get("params") or {}
                llm = router.build_llm(state.get("model_id"), **params)
            except Exception as e:
                logger.warning(f"获取 LLM 失败，降级为截取模式: {e}")
        
        # 使用统一的压缩函数
        window = await compress_messages(
            messages=base,
            mode=CompressionMode.LLM_SUMMARY if summarize else CompressionMode.TRUNCATE,
            trigger_type=TriggerType.TOKEN,
            threshold=hard_limit,
            target_size=int(hard_limit * 0.7),
            llm=llm,
            summary_prompt="你是一个对话摘要助手。请用简洁的语言总结以下对话的关键信息。",
            keep_recent=15
        )
        
        return {
            "messages": window,
            "context_stats": {
                "before": {"count": before_count, "approx_tokens": before_tokens},
                "after": {"count": len(window), "approx_tokens": approx_tokens(window)},
                "compressed": len(window) < len(base),
            }
        }
        
    except Exception as e:
        writer.error(f"上下文压缩失败: {str(e)}")
        return {}
```

## 模式路由节点（带 HITL）

```python
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
            messages = prompt.format_messages(question=q)
            resp = await llm.ainvoke(messages, temperature=0.0, max_tokens=200)
            decision = safe_json_parse(getattr(resp, "content", ""), {"mode": "react"})
            suggested = (decision.get("mode") or "react").lower()
            
            # 建议 deep 时进行 HITL 确认
            if suggested == "deep":
                request: HumanInterrupt = {
                    "action_request": {
                        "action": "confirm_deep",
                        "args": {"question": q, "suggested_mode": "deep"}
                    },
                    "config": {"allow_accept": True, "allow_reject": True, "allow_edit": False},
                    "description": "建议进入【深度研究】模式，是否确认？",
                }
                response = types.interrupt(request)
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

## 业务节点（带 @track_execute）

```python
@track_execute
async def searching_node(state: DeepResearchState) -> Dict[str, Any]:
    """信息搜索节点"""
    writer = create_stream_writer(node_name="searching", agent_name="deepresearch")
    
    query = extract_question_from_state(state)
    writer.thinking(f"正在搜索: {query}")
    
    # 执行搜索
    async with safe_tool_call(writer, "searching"):
        tool = wrap_tool_by_state(web_search_tool, state)
        results = await tool.ainvoke({"query": query})
    
    writer.search(
        answer=f"找到 {len(results)} 条结果",
        search_result=results,
        query=query,
        results_count=len(results)
    )
    
    return {
        "search_results": results,
        "current_node": "searching",
    }
```

## Writer API

```python
writer = create_stream_writer(node_name="节点名", agent_name="agent名")

# ========== 原子层 ==========
writer.content("内容", format_type="markdown")
writer.thinking("思考要点...")
writer.plan(tasks, current_task_id=1, overall_progress=30, description="描述")
writer.search(answer, search_result=results, query=q, results_count=len(results))
writer.tool_call("tool_name", {"param": "value"})
writer.tool_result("tool_name", result)
writer.error("错误信息", error_type="ValueError")
writer.summary("总结内容...")

# ========== 编排层 ==========
async for chunk in llm.astream(prompt):
    writer.graph(chunk)
```

## @track_execute 装饰器

装饰器自动完成：
1. 任务开始时：更新为 running，推送任务列表
2. 任务完成时：更新为 completed，推送任务列表
3. 任务失败时：根据重试次数决定状态，推送任务列表

```python
@track_execute
async def my_node(state: DeepResearchState) -> Dict[str, Any]:
    # 节点逻辑
    return {"result": ...}  # 装饰器自动合并 tasks/progress 等字段
```

## 异常处理

```python
try:
    result = await risky_operation()
except Exception as e:
    # 重要：不捕获中断异常
    if is_interrupt_exception(e):
        raise
    writer.error(f"操作失败: {str(e)}")
    return {"errors": [{"node": "my_node", "error": str(e)}]}
```

## 返回值规范

```python
return {
    "current_node": "节点名",
    "router_decision": {"next_action": "writing"},  # 供路由使用
    "search_results": [...],                        # 业务数据
    # tasks/overall_progress 由 @track_execute 自动管理
}
```
