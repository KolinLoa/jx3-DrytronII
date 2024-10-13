import os
import json
from dotenv import load_dotenv  # 导入 dotenv
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from jx3api import AsyncJX3API
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

__plugin_meta__ = PluginMetadata(
    name="jx3search",
    description="剑三基础查询工具",
    usage="具体使用方法请看帮助",
)

# 加载 .env 文件
load_dotenv()  # 这里将加载 .env 文件中的环境变量

# 从环境变量获取默认服务器、TOKEN 和 TICKET
DEFAULT_SERVER = os.getenv("DEFAULT_SERVER")
TOKEN = os.getenv("TOKEN")
TICKET = os.getenv("TICKET")


# 使用 TOKEN 和 TICKET 初始化 AsyncJX3API
async_api = AsyncJX3API(token=TOKEN, ticket=TICKET)

# 定义绑定文件路径
BINDINGS_FILE = os.path.join(os.path.dirname(__file__), "../bind/bindings.json")

def get_server_name(group_id: str) -> str:
    """根据群组 ID 获取绑定的服务器名称，如果没有则返回默认服务器"""
    if not os.path.exists(BINDINGS_FILE):
        return DEFAULT_SERVER

    with open(BINDINGS_FILE, "r", encoding="utf-8") as f:
        bindings = json.load(f)

    return bindings.get(group_id, DEFAULT_SERVER)


daily = on_command("daily", aliases={"日常"}, priority=5, block=True)

#日常查询，输入日常（+服务器名）
@daily.handle()
async def handle_function(args: Message = CommandArg()):
    server_name = args.extract_plain_text().strip()

    # 如果 server_name 是空的，获取绑定的服务器名称；若无绑定，使用默认服务器
    if not server_name:
        group_id = str(event.group_id)
        server_name = get_server_name(group_id)

    # 从 AsyncJX3API 获取日常数据
    daily_info = await async_api.active_calendar(server_name)

    # 从 daily_info 中提取数据
    data = daily_info.get("data", {})
    
    # 格式化文本消息
    text_message = (
        f"📅 日期：{data.get('date')} (星期{data.get('week')})\n\n"
        f"⚔️ 战场活动：{data.get('war')}\n"
        f"🏞️ 大战：{data.get('battle')}\n"
        f"⛏️ 矿车：{data.get('orecar')}\n"
        f"📚 门派：{data.get('school')}\n"
        f"🛡️ 救援：{data.get('rescue')}\n\n"
        f"🍀 今日宠物奇缘：\n- " + "\n- ".join(data.get('luck', [])) + "\n\n"
        f"🃏 副本：\n" + "\n".join(f"{i+1}. {card}" for i, card in enumerate(data.get('card', []))) + "\n\n"
        f"🎮 团本：\n" + "\n".join(f"{i+1}. {team}" for i, team in enumerate(data.get('team', [])))
    )
    
    # 返回格式化的文本信息
    await daily.finish(f"服务器：{server_name} 的日常信息：\n{text_message}")
    

