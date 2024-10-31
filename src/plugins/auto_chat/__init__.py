from nonebot import get_plugin_config, on_message, on_command
from nonebot.plugin import PluginMetadata
from nonebot import on_message, on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me
from zhipuai import ZhipuAI
import requests
import json
import random



from .config import Config

__plugin_meta__ = PluginMetadata(
    name="auto_chat",
    description="见缝插针式自动聊天",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# 从配置中获取 API_KEY 和 SECRET_KEY
config = get_driver().config
API_KEY = config.api_key
CONTENT = config.content


client = ZhipuAI(api_key=API_KEY)


wenxin_chat = on_message(priority=99)
chat_query = on_message(rule=to_me(), permission=GROUP, priority=9, block=True)
set_probability_cmd = on_command("set_probability", aliases={"活跃度", "设置概率"}, permission=GROUP_ADMIN | GROUP_OWNER)

REPLY_PROBABILITY = 10  # 默认的概率值

@chat_query.handle()
async def handle_chat_query(bot: Bot, event: GroupMessageEvent):
    user_message = str(event.get_message()).strip()
    response = await get_wenxin_response(user_message, config)
    await chat_query.send(response)

@wenxin_chat.handle()
async def handle_auto_chat(bot: Bot, event: GroupMessageEvent):
    user_message = str(event.get_message()).strip()

    # 根据概率决定是否触发 auto_chat
    if random.randint(1, 200) <= REPLY_PROBABILITY:  # 概率值调整为 1-200 之间
        response = await get_wenxin_response(user_message)
        await wenxin_chat.send(response)

@set_probability_cmd.handle()
async def handle_set_probability(event: GroupMessageEvent, args: Message = CommandArg()):
    global REPLY_PROBABILITY
    command_args = args.extract_plain_text().strip().split()  # 提取命令参数
    try:
        new_probability = int(command_args[0])  # 取第一个参数并转为整数
        if 1 <= new_probability <= 200:  # 确保概率在1到200之间
            REPLY_PROBABILITY = new_probability
            await set_probability_cmd.send(f"概率已设置为 {REPLY_PROBABILITY}%。")
        else:
            await set_probability_cmd.send("请提供一个在1到200之间的整数。")
    except (ValueError, IndexError):
        await set_probability_cmd.send("请输入有效的整数。")


async def get_wenxin_response(user_message: str, config) -> str:
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": CONTENT  # 从 config 中获取内容
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        tools=[{"type": "web_search", "web_search": {"search_result": True}}],
        stream=True
    )

    result = ""
    for trunk in response:
        for choice in trunk.choices:
            result += choice.delta.content  # 收集所有内容

    return result or "我不能理解你在说什么。"