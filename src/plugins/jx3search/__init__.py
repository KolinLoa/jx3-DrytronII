import os
import json
from nonebot import on_command, get_driver
from nonebot.plugin import PluginMetadata
from jx3api import AsyncJX3API
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

__plugin_meta__ = PluginMetadata(
    name="jx3search",
    description="剑三基础查询工具",
    usage="具体使用方法请看帮助",
)

# 获取 NoneBot 的配置对象
driver = get_driver()
config = driver.config

# 从配置中获取环境变量的值
DEFAULT_SERVER = config.default_server
TOKEN = config.token
TICKET = config.ticket

# 使用 TOKEN 和 TICKET 初始化 AsyncJX3API
async_api = AsyncJX3API(token=TOKEN, ticket=TICKET)

# 定义绑定文件路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
BINDINGS_FILE = os.path.join(ROOT_DIR, "bindings.json")


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

    # 检查 API 响应是否成功
    if "date" not in daily_info:
        print("查询失败或未找到有效的日常数据")
    else:
            
            # 直接使用 daily_info 中的数据
        text_message = (f"📅 日期：{daily_info.get('date')} (星期{daily_info.get('week')})\n\n"
                    f"🏞️ 大战：{daily_info.get('war')}\n"
                    f"⚔️ 战场活动：{daily_info.get('battle')}\n"
                    f"⛏️ 矿车：{daily_info.get('orecar')}\n"
                    f"📚 门派：{daily_info.get('school')}\n"
                    f"🛡️ 救援：{daily_info.get('rescue')}\n\n"
                    f"🍀 今日宠物奇缘：\n- " + "\n- ".join(daily_info.get('luck', [])) +
                    "\n\n"
                    f"🃏 副本：\n" +
                    "\n".join(f"{i+1}. {card}" for i, card in enumerate(daily_info.get('card', []))) +
                    "\n\n"
                    f"🎨 美人图：{daily_info.get('draw')}\n\n"
                    f"🎮 团本：\n" +
                    "\n".join(f"{i+1}. {team}" for i, team in enumerate(daily_info.get('team', []))))
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

        # 检查 API 响应并确保 celebs_info 是一个列表
    if not isinstance(celebs_info, list) or not celebs_info:
        await celebs.finish("未找到相关行侠信息。")

    # 筛选指定地图的事件
    filtered_events = [event for event in celebs_info if event.get("map_name") == map_name]
    
    if not filtered_events:
        await celebs.finish(f"未找到地图 {map_name} 的行侠信息。")

    # 格式化事件信息
    text_message = f"{map_name} ：\n"
    for event in filtered_events:
        text_message += (f"\n事件：{event.get('event', '未知')}\n"
                         f"地点：{event.get('site', '未知')}\n"
                         f"{event.get('desc', '无描述')}\n"
                         f"时间：{event.get('time', '未知时间')}\n")

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

    # 检查是否有数据
    if exam_info:
        for item in exam_info:
            text_message = (f"问题 ID: {item['id']}\n"
                             f"问题: {item['question']}\n"
                             f"答案: {item['answer']}\n"
                             f"拼音: {item['pinyin']}\n")
        await exam.finish(text_message)  # 发送响应消息
    else:
        await exam.finish("请求失败：没有获取到试题数据。")


#查询花价，输入花价（+服务器）
flower_price = on_command("flower", aliases={"花价"}, priority=5, block=True)

@flower_price.handle()
async def handle_flower_price(event: GroupMessageEvent, args: Message = CommandArg()):
    # 提取用户输入
    text = args.extract_plain_text()

    # 检查用户输入是否为空
    if not text:
        await flower_price.finish("请提供服务器和花名，例如：'服务器名称 花名'")

    # 分割用户输入，提取服务器名称和花名
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await flower_price.finish("请认真输入：服务器名称 花名")

    server_name, flower_name = parts[0], parts[1]

    # 如果 server_name 是空的，使用绑定的服务器名称或默认服务器
    if not server_name:
        group_id = str(event.group_id)
        server_name = get_server_name(group_id)  # 假设你有这个函数

    # 从 AsyncJX3API 获取特定花名的花价数据
    flower_info = await async_api.home_flower(server=server_name, name=flower_name)

    # 检查数据是否存在
    if not flower_info:
        await flower_price.finish("未能获取到花价信息。")

    # 直接使用 flower_info，因为它已经是我们需要的数据结构
    formatted_data = {}

    # 将数据按照地点格式化存储
    for location, flowers in flower_info.items():
        formatted_data[location] = []  # 为每个地点初始化一个列表
        for flower_data in flowers:
            # 将花的信息以字典形式添加到列表中
            formatted_data[location].append({
                "name": flower_data.get("name", "未知"),
                "color": flower_data.get("color", "未知"),
                "price": flower_data.get("price", "未知"),
                "line": flower_data.get("line", [])
            })

    # 构建返回信息
    text_message = f"{flower_name} 的花价信息：\n"
    for location, flowers in formatted_data.items():
        text_message += f"\n地点：{location}\n"
        for flower in flowers:
            text_message += (
                f"花名：{flower['name']}\n"
                f"颜色：{flower['color']}\n"
                f"价格：{flower['price']} 金\n"
                f"线路：{'，'.join(flower['line'])}\n"
                f"----------------------\n"
            )

    # 发送格式化后的信息
    await flower_price.finish(text_message)




#查询家具价格，输入家园+家具名
furniture = on_command("furniture", aliases={"家园"}, priority=5, block=True)

@furniture.handle()
async def handle_furniture(args: Message = CommandArg()):
    furniture_name = args.extract_plain_text()
    if not furniture_name:
        await furniture.finish("TMD想好了再查！")
    
    # 从 AsyncJX3API 获取家具价格数据
    furniture_info = await async_api.home_furniture(name=furniture_name)

    # 提取数据
    # 因为没有 code 和 data 字段，直接从 furniture_info 获取信息
    if not furniture_info:
        await furniture.finish("查询失败：未获取到任何信息")

    # 提取具体字段
    image_url = furniture_info.get("image")  # 获取图片 URL
    name = furniture_info.get("name")
    source = furniture_info.get("source")
    tip = furniture_info.get("tip")
    view = furniture_info.get("view")
    quality = furniture_info.get("quality")

    # 检查是否有必需的数据
    if not all([name, source, tip, view, quality, image_url]):
        await furniture.finish("查询失败：数据不完整")

    # 构建返回信息
    text_message = (
        f"家具名称：{name}\n"
        f"来源：{source}\n"
        f"描述：{tip}\n"
        f"装饰度：{view}\n"
        f"质量：{quality}"
    )

    # 发送家具信息和图片
    await furniture.finish(Message(f"{text_message}\n[CQ:image,file={image_url}]"))


# 器物图谱查询，输入器物+地图
travel = on_command("travel", aliases={"器物"}, priority=5, block=True)

@travel.handle()
async def handle_travel(args: Message = CommandArg()):
    travel_name = args.extract_plain_text()
    if not travel_name:
        await travel.finish("TMD想好了再查！")

    # 从 AsyncJX3API 获取器物图谱数据
    travel_info = await async_api.home_travel(name=travel_name)

    # 检查是否获取到数据
    if not travel_info or not isinstance(travel_info, list):
        await travel.finish("查询失败：未获取到任何信息")

    # 提取器物数据
    data = travel_info[0]  # 获取列表中的第一个元素
    image_url = data.get("image")  # 获取图片 URL
    name = data.get("name")
    source = data.get("source")
    limit = data.get("limit")
    quality = data.get("quality")
    view = data.get("view")
    practical = data.get("practical")
    hard = data.get("hard")
    geomantic = data.get("geomantic")
    interesting = data.get("interesting")
    produce = data.get("produce")
    tip = data.get("tip")


    # 构建返回信息
    text_message = (
        f"器物名称：{name}\n"
        f"来源：{source}\n"
        f"数量：{limit}\n"
        f"质量：{quality}\n"
        f"装饰度：{view}\n"
        f"实用性：{practical}\n"
        f"难度：{hard}\n"
        f"风水：{geomantic}\n"
        f"趣味性：{interesting}\n"
        f"产出：{produce}\n"
        f"描述：{tip}"
    )

    # 发送器物信息和图片
    await travel.finish(Message(f"{text_message}\n[CQ:image,file={image_url}]"))

    

#开服检查，输入开服或者开服+服务器
check = on_command("check", aliases={"开服"}, priority=5, block=True)

@check.handle()
async def handle_check(event: GroupMessageEvent, args: Message = CommandArg()):
    server_name = args.extract_plain_text()
    if not server_name:
        server_name = get_server_name(str(event.group_id))

    # 从 AsyncJX3API 获取服务器开服信息
    check_info = await async_api.server_check(server=server_name)

    # 检查是否获取到数据
    if not check_info:
        await check.finish("查询失败：未获取到任何信息")

    # 提取服务器开服信息
    server_status = check_info.get("status")  # 获取服务器状态
    zone = check_info.get("zone")
    server = check_info.get("server")

    # 检查是否有必需的数据
    if server_status is None or not zone or not server:
        await check.finish("查询失败：数据不完整")

    # 根据服务器状态构建返回信息
    if server_status == 1:
        text_message = (
            f"服务器状态：开服\n"
            f"区服：{zone}\n"
            f"服务器：{server}\n"
            f"赶紧上线打工吧！"
        )
    else:
        text_message = (
            f"服务器状态：维护中\n"
            f"Have a break!别那么着急打工!"
        )

    # 发送服务器状态消息
    await check.finish(text_message)

# 官方最新公告及新闻，输入新闻
allnews = on_command("allnews", aliases={"新闻"}, priority=5, block=True)

@allnews.handle()
async def handle_allnews(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取官方最新公告及新闻
    news_info = await async_api.news_allnews(limit="1")

    # 检查是否获取到数据
    if not news_info or not isinstance(news_info, list):
        await allnews.finish("查询失败：未获取到任何新闻信息")

    # 提取第一个新闻项目的数据
    data = news_info[0]
    title = data.get("title")
    category = data.get("class")
    date = data.get("date")
    url = data.get("url")

    # 检查是否有必需的数据
    if not all([title, category, date, url]):
        await allnews.finish("查询失败：数据不完整")

    # 构建返回消息
    text_message = (
        f"最新公告：\n"
        f"标题：{title}\n"
        f"分类：{category}\n"
        f"日期：{date}\n"
        f"链接：{url}\n"
    )

    # 发送消息
    await allnews.finish(text_message)


# 官方最新维护公告,输入维护
announce = on_command("announce", aliases={"维护"}, priority=5, block=True)

@announce.handle()
async def handle_announce(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取官方最新维护公告
    announce_info = await async_api.news_announce(limit="1")

    # 检查是否获取到数据
    if not announce_info:
        await announce.finish("查询失败：未获取到任何信息")

    # 提取公告数据
    if isinstance(announce_info, list) and announce_info:
        data = announce_info[0]
    else:
        await announce.finish("查询失败：未获取到公告信息")

    # 构建返回消息
    text_message = (
        f"标题：{data.get('title')}\n"
        f"分类：{data.get('class')}\n"
        f"日期：{data.get('date')}\n"
        f"链接：{data.get('url')}\n"
    )

    # 发送消息
    await announce.finish(text_message)

# 骚话，输入骚话
random = on_command("random", aliases={"骚话"}, priority=5, block=True)

@random.handle()
async def handle_random(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取骚话
    random_info = await async_api.saohua_random()

    # 检查是否获取到数据
    if not random_info:
        await random.finish("查询失败：未获取到任何信息")

    # 提取骚话内容
    saohua_text = random_info.get("text")
    
    # 检查内容是否存在
    if not saohua_text:
        await random.finish("查询失败：数据不完整")

    # 发送消息
    await random.finish(saohua_text)

# 舔狗日记，输入舔狗
content = on_command("content", aliases={"舔狗"}, priority=5, block=True)

@content.handle()
async def handle_content(args: Message = CommandArg()):
    # 从 AsyncJX3API 获取舔狗内容
    content_info = await async_api.saohua_content()

    # 检查是否获取到数据
    if not content_info:
        await content.finish("查询失败：未获取到任何信息")

    # 提取舔狗语录
    content_text = content_info.get("text")
    
    # 检查内容是否存在
    if not content_text:
        await content.finish("查询失败：数据不完整")

    # 发送消息
    await content.finish(content_text)





