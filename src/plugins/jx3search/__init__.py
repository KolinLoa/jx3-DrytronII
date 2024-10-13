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


##################### Free API #####################

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
    daily_info = await async_api.active_calendar(server=server_name)

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
    celebs_info = await async_api.active_celebs(name=map_name)

    # 检查 API 响应
    if celebs_info["code"] != 200:
        await celebs.finish(f"查询失败：{celebs_info['msg']}")

    # 提取行侠事件数据
    event_data = celebs_info["data"]


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
    exam_info = await async_api.exam_answer(subject=subject)

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
    flower_info = await async_api.home_flower(server=server_name, name=flower_name)

    # 检查 API 响应是否成功
    if flower_info.get("code") != 200:
        await flower.finish(f"查询失败：{flower_info.get('msg', '未知错误')}")

    # 提取数据
    data = flower_info.get("data", {})

    # 从 data 中提取具体花的信息
    flowers = data

    # 格式化输出
    text_message = f"{flowers.get()} 的花价信息：\n"
    for flower_data in flowers:  # 使用 flower_data 代替 flower，避免冲突
        text_message += (f"\n花名：{flower_data.get('name', '未知')}\n"
                         f"颜色：{flower_data.get('color', '未知')}\n"
                         f"价格：{flower_data.get('price', '未知')} 金\n"
                         f"线路：{'，'.join(flower_data.get('line', []))}\n")

    # 发送格式化后的信息
    await flower.finish(text_message)

#查询家具价格，输入家园+家具名
furniture = on_command("furniture", aliases={"家园"}, priority=5, block=True)

@furniture.handle()
async def handle_furniture(args: Message = CommandArg()):
    furniture_name = args.extract_plain_text()
    if not furniture_name:
        await furniture.finish("TMD想好了再查！")
    
    # 从 AsyncJX3API 获取家具价格数据
    furniture_info = await async_api.home_furniture(name=furniture_name)

    # 检查 API 响应是否成功
    if furniture_info.get("code") != 200:
        await furniture.finish(f"查询失败：{furniture_info.get('msg', '未知错误')}")

    # 提取数据
    data = furniture_info.get("data", {})
    image_url = data.get("image")  # 获取图片 URL

    # 构建返回信息
    text_message = f"家具名称：{data.get('name')}\n" \
                   f"来源：{data.get('source')}\n" \
                   f"描述：{data.get('tip')}\n" \
                   f"装饰度：{data.get('view')}\n" \
                   f"质量：{data.get('quality')}"

    # 发送家具信息和图片
    await furniture.send(Message(f"{text_message}\n[CQ:image,file={image_url}]"))

# 器物图谱查询，输入器物+地图
travel = on_command("travel", aliases={"器物"}, priority=5, block=True)

@travel.handle()
async def handle_travel(args: Message = CommandArg()):
    travel_name = args.extract_plain_text()
    if not travel_name:
        await travel.finish("TMD想好了再查！")

    # 从 AsyncJX3API 获取器物图谱数据
    travel_info = await async_api.home_travel(name=travel_name)
    
    # 检查 API 响应是否成功
    if travel_info.get("code") != 200:
        await travel.finish(f"查询失败：{travel_info.get('msg', '未知错误')}")

    # 提取器物数据
    data = travel_info.get("data", [{}])[0]  # 获取第一个器物数据
    image_url = data.get("image")  # 获取图片 URL

    # 构建返回信息
    text_message = f"器物名称：{data.get('name')}\n" \
                   f"来源：{data.get('source')}\n" \
                   f"数量：{data.get('limit')}\n" \
                   f"质量：{data.get('quality')}\n" \
                   f"装饰度：{data.get('view')}\n" \
                   f"实用性：{data.get('practical')}\n" \
                   f"难度：{data.get('hard')}\n" \
                   f"风水：{data.get('geomantic')}\n" \
                   f"趣味性：{data.get('interesting')}\n" \
                   f"产出：{data.get('produce')}\n" \
                   f"描述：{data.get('tip')}"

    # 发送器物信息和图片
    await travel.send(Message(f"{text_message}\n[CQ:image,file={image_url}]"))
    

#开服检查，输入开服或者开服+服务器
check = on_command("check", aliases={"开服"}, priority=5, block=True)

@check.handle()
async def handle_check(args: Message = CommandArg()):
    server_name = args.extract_plain_text()
    if not server_name:
        server_name = get_server_name(str(event.group_id))

    # 从 AsyncJX3API 获取服务器开服信息
    check_info = await async_api.server_check(server=server_name)
    
    # 检查 API 响应是否成功
    if check_info.get("code") != 200:
        await check.finish(f"查询失败：{check_info.get('msg', '未知错误')}")

    # 提取服务器开服信息
    data = check_info.get("data", {})
    server_status = data.get("status")  # 获取服务器状态

    # 根据服务器状态构建返回信息
    if server_status == 1:
        text_message = f"服务器状态：开服\n" \
                       f"区服：{data.get('zone')}"\
                       f"服务器：{data.get('server')}\n" \
                       f"赶紧上线打工吧！\n"
                       
    else:
        text_message = f"服务器状态：维护中\n"\
                       f"Have a break!别那么着急打工!\n"


    # 发送服务器状态消息
    await check_status.send(text_message)

# 官方最新公告及新闻，输入新闻
allnews = on_command("allnews", aliases={"新闻"}, priority=5, block=True)

@allnews.handle()
async def handle_allnews(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取官方最新公告及新闻
    news_info = await async_api.news_allnews(limit="1")
    
    # 检查 API 响应是否成功
    if news_info.get("code") != 200:
        await allnews.finish(f"查询失败：{news_info.get('msg', '未知错误')}")

    # 提取新闻数据
    data = news_info.get("data", [{}])[0]  # 获取第一个新闻项目

    # 构建返回消息
    text_message = f"最新公告：标题：{data.get('title')}\n"\
                f"分类：{data.get('class')}\n"\
                f"日期：{data.get('date')}\n"\
                f"链接：{data.get('url')}\n"

    # 发送消息
    await allnews.send(text_message)

# 官方最新维护公告,输入维护
announce = on_command("announce", aliases={"维护"}, priority=5, block=True)

@announce.handle()
async def handle_announce(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取官方最新维护公告
    announce_info = await async_api.news_announce(limit="1")
    
    # 检查 API 响应是否成功
    if announce_info.get("code") != 200:
        await announce.finish(f"查询失败：{announce_info.get('msg', '未知错误')}")

    # 提取公告数据
    data = announce_info.get("data", [{}])[0]

    # 构建返回消息
    text_message = f"标题：{data.get('title')}\n"\
                f"分类：{data.get('class')}\n"\
                f"日期：{data.get('date')}\n"\
                f"链接：{data.get('url')}\n"
    
    # 发送消息
    await announce.send(text_message)

# 骚话，输入骚话
random = on_command("random", aliases={"骚话"}, priority=5, block=True)

@random.handle()
async def handle_random(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取骚话
    random_info = await async_api_saohua.random
    
    # 检查 API 响应是否成功
    if random_info.get("code") != 200:
        await random.finish(f"查询失败：{random_info.get('msg', '未知错误')}")

    # 提取骚话
    data = random_info.get("data", [{}])[0]
    
    # 构建返回消息
    text_message = f"{data.get('text')}"
    
    # 发送消息
    await random.send(text_message)

# 舔狗日记，输入舔狗
content = on_command("content", aliases={"舔狗"}, priority=5, block=True)

@content.handle()
async def handle_content(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取舔狗
    content_info = await async_api_saohua.content
    
    # 检查 API 响应是否成功
    if content_info.get("code") != 200:
        await content.finish(f"查询失败：{content_info.get('msg', '未知错误')}")

    # 提取舔狗
    data = content_info.get("data", [{}])[0]
    
    # 构建返回消息
    text_message = f"{data.get('text')}"
    
    # 发送消息
    await content.send(text_message)





