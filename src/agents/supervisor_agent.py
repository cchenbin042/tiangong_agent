from langchain.agents import create_agent
from langgraph.checkpoint.redis import AsyncRedisSaver
from langchain.chat_models import init_chat_model
from src.infra.redis_cache import get_checkpointer_redis


# 创建监督Agent
async def create_supervisor_agent():
    # 1、复用项目存在的checkpointer
    redis_client = get_checkpointer_redis()

    # 2. 创建 AsyncRedisSaver，并调用 asetup() 初始化 RediSearch 索引
    # asetup() 会在 Redis Stack 中创建 checkpoint / checkpoint_write 两个索引
    # 必须在首次使用前调用一次，索引已存在时自动跳过，可以重复调用
    checkpointer = AsyncRedisSaver(redis_client=redis_client)
    await checkpointer.asetup()

    # 3. 创建 SupervisorAgent
    model = init_chat_model(model="deepseek-chat")

    agent = create_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer, # 短期记忆
    )
    return agent

# 构建模块级单实例，避免每次请求都去创建agent和checkpointer
_supervisor_agent = None

async def get_supervisor_agent():
    """返回全局单例 Agent，首次调用时初始化。"""
    global _supervisor_agent
    if _supervisor_agent is None:
        _supervisor_agent = await create_supervisor_agent()
    return _supervisor_agent

# 在FastAPI中使用
async def chat_endpoint(user_id: str, session_id: str, message: str) -> str:
    agent = await get_supervisor_agent() # 获取全局单例 Agent
    # 设置线程ID，用于区分不同用户的对话
    config = {
        "configurable":{
            "thread_id":f"{user_id}_{session_id}"
        }
    }
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config
    )

    return result['messages'][-1].content