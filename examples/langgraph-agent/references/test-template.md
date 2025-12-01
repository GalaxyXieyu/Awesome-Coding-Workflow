# 测试代码模板

## 最小测试

```python
import asyncio
import time
from langgraph.checkpoint.memory import InMemorySaver
from .graph import workflow

async def test_basic_flow():
    """基础流程测试"""
    config = {
        "configurable": {
            "thread_id": f"test_{int(time.time())}",
            "user_id": "test_user"
        }
    }
    
    state = {
        "query": "测试输入",
        "model_id": "gpt-4o",
        "tool_execution_mode": "copilot"
    }
    
    app = workflow.compile(checkpointer=InMemorySaver())
    
    outputs = []
    async for event in app.astream(state, config=config, stream_mode=["custom"]):
        outputs.append(event)
    
    assert len(outputs) > 0
    print("基础流程测试通过")

if __name__ == "__main__":
    asyncio.run(test_basic_flow())
```

## HITL 测试

```python
from langgraph.types import Command

async def test_hitl_flow():
    """HITL 中断恢复测试"""
    config = {
        "configurable": {
            "thread_id": f"hitl_test_{int(time.time())}",
            "user_id": "test_user"
        }
    }
    
    state = {
        "query": "需要确认的操作",
        "model_id": "gpt-4o",
        "tool_execution_mode": "interactive"
    }
    
    app = workflow.compile(
        checkpointer=InMemorySaver(),
        interrupt_before=["工具执行"]
    )
    
    # 第一轮：触发中断
    events_1 = []
    async for event in app.astream(state, config=config, stream_mode=["custom"]):
        events_1.append(event)
    
    # 验证到达中断点
    current = await app.aget_state(config)
    assert current.next == ("工具执行",)
    
    # 恢复执行
    events_2 = []
    async for event in app.astream(
        Command(resume=[{"type": "accept"}]),
        config=config,
        stream_mode=["custom"]
    ):
        events_2.append(event)
    
    print("HITL 测试通过")
```

## 错误处理测试

```python
async def test_error_handling():
    """错误处理测试"""
    config = {
        "configurable": {
            "thread_id": f"error_test_{int(time.time())}",
            "user_id": "test_user"
        }
    }
    
    # 故意缺少 model_id
    state = {
        "query": "测试输入",
        # "model_id": None  # 缺失
    }
    
    app = workflow.compile(checkpointer=InMemorySaver())
    
    async for event in app.astream(state, config=config, stream_mode=["custom"]):
        pass
    
    final = await app.aget_state(config)
    errors = final.values.get("errors", [])
    
    assert len(errors) > 0
    assert "model_id" in str(errors)
    print("错误处理测试通过")
```

## 状态持久化测试

```python
async def test_state_persistence():
    """状态持久化测试"""
    thread_id = f"persist_test_{int(time.time())}"
    config = {"configurable": {"thread_id": thread_id, "user_id": "test_user"}}
    
    checkpointer = InMemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    # 第一次运行
    state = {"query": "第一次输入", "model_id": "gpt-4o"}
    async for _ in app.astream(state, config=config):
        pass
    
    # 获取状态
    saved = await app.aget_state(config)
    assert saved.values.get("query") == "第一次输入"
    
    # 继续运行（新输入）
    state_2 = {"query": "第二次输入"}
    async for _ in app.astream(state_2, config=config):
        pass
    
    # 验证历史累加
    final = await app.aget_state(config)
    history = final.values.get("history", [])
    assert len(history) >= 2
    
    print("状态持久化测试通过")
```

## 运行所有测试

```python
async def run_all_tests():
    """运行所有测试"""
    await test_basic_flow()
    await test_hitl_flow()
    await test_error_handling()
    await test_state_persistence()
    print("===== 所有测试通过 =====")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
```
