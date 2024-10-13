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
BINDINGS_FILE = os.path.join(os.path.dirname(__file__),
                             "../bind/bindings.json")


def get_server_name(group_id: str) -> str:
    """根据群组 ID 获取绑定的服务器名称，如果没有则返回默认服务器"""
    if not os.path.exists(BINDINGS_FILE):
        return DEFAULT_SERVER

    with open(BINDINGS_FILE, "r", encoding="utf-8") as f:
        bindings = json.load(f)

    return bindings.get(group_id, DEFAULT_SERVER)


#日常查询，输入日常（+服务器名）
daily = on_command("daily", aliases={"日常"}, priority=5, block=True)


@daily.handle()
async def handle_daily(event: GroupMessageEvent, args: Message = CommandArg()):
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
    text_message = (f"📅 日期：{data.get('date')} (星期{data.get('week')})\n\n"
                    f"⚔️ 战场活动：{data.get('war')}\n"
                    f"🏞️ 大战：{data.get('battle')}\n"
                    f"⛏️ 矿车：{data.get('orecar')}\n"
                    f"📚 门派：{data.get('school')}\n"
                    f"🛡️ 救援：{data.get('rescue')}\n\n"
                    f"🍀 今日宠物奇缘：\n- " + "\n- ".join(data.get('luck', [])) +
                    "\n\n"
                    f"🃏 副本：\n" +
                    "\n".join(f"{i+1}. {card}"
                              for i, card in enumerate(data.get('card', []))) +
                    "\n\n"
                    f"🎮 团本：\n" +
                    "\n".join(f"{i+1}. {team}"
                              for i, team in enumerate(data.get('team', []))))

    # 返回格式化的文本信息
    await daily.finish(f"服务器：{server_name} 的日常信息：\n{text_message}")


#行侠事件查询，输入行侠+地图名
celebs = on_command("celebs", aliases={"行侠"}, priority=5, block=True)


@celebs.handle()
async def handle_celebs(args: Message = CommandArg()):
    map_name = args.extract_plain_text()
    if not map_name:
        await celebs.finish("TMD想好了再查！")

    # 从 AsyncJX3API 获取行侠数据
    celebs_info = await async_api.active_celebs(map_name)

    # 检查 API 响应
    if celebs_info["code"] != 200:
        await celebs.finish(f"查询失败：{celebs_info['msg']}")

    # 提取行侠事件数据
    event_data = celebs_info["data"]

    # 如果没有事件数据，发送空数据提醒
    if not event_data:
        await celebs.finish(f"在 {map_name} 没有找到行侠数据。")

    # 格式化事件信息
    text_message = f"行侠信息\n"
    for event in event_data:
        text_message += (f"\n地图名称：{event['map_name']}\n"
                         f"事件：{event['event']}\n"
                         f"地点：{event['site']}\n"
                         f"{event['desc']}\n"
                         f"时间：{event['time']}\n")

    # 发送格式化后的信息
    await celebs.finish(text_message)


#科举试题查询，输入科举+题目
exam = on_command("exam", aliases={"科举"}, priority=5, block=True)


@exam.handle()
async def handle_exam(args: Message = CommandArg()):
    subject = args.extract_plain_text()
    if not subject:
        await exam.finish("TMD想好了再查！")

    # 从 AsyncJX3API 获取科举试题数据
    exam_info = await async_api.exam_answer(subject)

    # 处理 JSON 数据
    if exam_info["code"] == 200:
        # 输出请求成功的信息
        text_message = f"请求成功：{exam_info['msg']}\n"
        for item in exam_info["data"]:
            text_message += (f"问题 ID: {item['id']}\n"
                             f"问题: {item['question']}\n"
                             f"答案: {item['answer']}\n"
                             f"拼音: {item['pinyin']}\n")
        await exam.finish(text_message)  # 发送响应消息
    else:
        await exam.finish(f"请求失败：{exam_info['msg']}")


#查询花价，输入花价（+服务器）
flower = on_command("flower", aliases={"花价"}, priority=5, block=True)


@flower.handle()
async def handle_flower(event: GroupMessageEvent,
                        args: Message = CommandArg()):
    # 提取用户输入
    text = args.extract_plain_text()

    # 检查用户输入是否为空
    if not text:
        await flower.finish("请TM提供服务器和花名，例如：'服务器名称 花名'")

    # 分割用户输入，提取服务器名称和花名
    parts = text.split(maxsplit=1)
    if len(parts) < 1:
        await flower.finish("能不能认真输入，请给老子输入：服务器名称 花名")

    server_name, flower_name = parts[0], parts[1]

    # 如果 server_name 是空的，使用绑定的服务器名称或默认服务器
    if not server_name:
        group_id = str(event.group_id)
        server_name = get_server_name(
            group_id)  # 确保 get_server_name 返回绑定或默认服务器名称

    # 从 AsyncJX3API 获取特定花名的花价数据
    flower_info = await async_api.home_flower(server_name, flower_name)

    # 检查 API 响应是否成功
    if flower_info.get("code") != 200:
        await flower.finish(f"查询失败：{flower_info.get('msg', '未知错误')}")

    # 提取数据
    data = flower_info.get("data", {})
    if not data or server_name not in data:
        await flower.finish(f"{server_name} 没有找到关于 {flower_name} 的花价信息。")

    # 从 data 中提取具体花的信息
    flowers = data[server_name]

    # 格式化输出
    text_message = f"{server_name} 的花价信息：\n"
    for flower_data in flowers:  # 使用 flower_data 代替 flower，避免冲突
        text_message += (f"\n花名：{flower_data.get('name', '未知')}\n"
                         f"颜色：{flower_data.get('color', '未知')}\n"
                         f"价格：{flower_data.get('price', '未知')} 金\n"
                         f"线路：{'，'.join(flower_data.get('line', []))}\n")

    # 发送格式化后的信息
    await flower.finish(text_message)
