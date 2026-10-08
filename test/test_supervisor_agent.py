import pytest

from src.agents.supervisor_agent import chat_endpoint

#@pytest.mark.asyncio
# async def test_supervisor_agent():
#     result = await chat_endpoint("1001", "1001", "你好")
#     print(result)

async def test_agent_memory():
    """验证短期记忆：同一 thread_id 下第二轮能记住第一轮的内容"""
    # 第一轮：自我介绍
    reply1 = await chat_endpoint("1123", "ATDAAS", "你好，我Aubin")
    print(f"\n第一轮回复：{reply1}")

    # 第二轮：考察记忆
    reply2 = await chat_endpoint("1123", "ATDAAS", "我是谁？")
    print(f"第二轮回复：{reply2}")

    # 断言：第二轮回复应包含名字
    assert "Aubin" in reply2, f"Agent 应该记住用户名字，实际回复：{reply2}"