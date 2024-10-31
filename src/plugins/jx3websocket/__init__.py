from nonebot import get_plugin_config, get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.plugin import PluginMetadata
from .config import Config
import websockets
import datetime
import asyncio
import certifi
import json
import ssl



driver = get_driver()
config = driver.config

TOKEN = config.wsstoken


# SSL 配置
context = ssl.create_default_context()
context.load_verify_locations(certifi.where())

__plugin_meta__ = PluginMetadata(
    name="jx3websocket",
    description="剑网三websocket消息推送",
    usage="接收jx3api.com的消息",
    config=Config,
)

config = get_plugin_config(Config)

class Handler:
    @classmethod
    async def action_1001(cls, data: dict):
        zone = data['zone']
        server = data['server']
        name = data['name']
        event = data['event']
        str_time = await gettime(data["time"])
        return f"收到奇遇事件：{server} 的 {name} 在 {str_time} 触发了 {event}"

    @classmethod
    async def action_1002(cls, data: dict):
        server_name = data["server"]
        min_time = data["min_time"]
        max_time = data["max_time"]
        map_name = data["map_name"]
        time = await gettime(data["time"])
        return f"{server_name},{min_time}-{max_time}分钟后，将有宝马良驹出现在{map_name}\n消息时间{time}"

    @classmethod
    async def action_1003(cls, data: dict):
        server_name = data["server"]
        player_name = data["name"]
        map_name = data["map_name"]
        horse_name = data["horse"]
        return f"恭喜这个老六{server_name},{player_name}在{map_name}抓获{horse_name}宝驹。"

    @classmethod
    async def action_1004(cls, data: dict):
        server_name = data["server"]
        time = await gettime(data["time"])
        return f"{server_name},[{time}]，扶摇九天已开启"

    @classmethod
    async def action_1005(cls, data: dict):
        server_name = data["server"]
        player_names = data["name"]
        player_names_str = ""
        for i in player_names:
            player_names_str = player_names_str + "【" + i + "】"
        return f"{server_name},以下老六获得扶摇点名:\n{player_names_str}"

    @classmethod
    async def action_1007(cls, data: dict):
        server_name = data["server"]
        player_name = data["role_name"]
        map_name = data["map_name"]
        xuanjing_name = data["name"]
        return f"{server_name},恭喜这个老六{player_name}在{map_name}获得{xuanjing_name}。"

    @classmethod
    async def action_1008(cls, data: dict):
        return f"追魂点名消息处理: {data}"

    @classmethod
    async def action_1009(cls, data: dict):
        server_name = data["server"]
        map_name = data["map_name"]
        time = await gettime(data["time"])
        return f"{server_name},诛恶事件于{time}触发！众侠士可前往【{map_name}】一探究竟。"

    @classmethod
    async def action_1010(cls, data: dict):
        return f"的卢刷新消息处理: {data}"

    @classmethod
    async def action_1011(cls, data: dict):
        return f"的卢捕获消息处理: {data}"

    @classmethod
    async def action_1012(cls, data: dict):
        return f"的卢竞拍消息处理: {data}"

    @classmethod
    async def action_1101(cls, data: dict):
        server_name = data["server"]
        castle = data["castle"]
        camp = data["camp_name"]
        time = await gettime(data["time"])
        return f"{server_name},在 {time} {castle} 据点粮仓被一群 {camp} 人士洗劫"

    @classmethod
    async def action_1102(cls, data: dict):
        server_name = data["server"]
        name = data["name"]
        time = await gettime(data["time"])
        return f"{server_name},在 {time} {name} 据点大旗被据点大将重置回初始位置！"

    @classmethod
    async def action_1103(cls, data: dict):
        server_name = data["server"]
        castle = data["castle"]
        map = data["map_name"]
        camp = data["camp_name"]
        time = await gettime(data["time"])
        return f"{server_name},在 {time} {camp} 位于 {map} 的 {castle} 据点大旗被夺，十分钟后未能夺回大旗，则会丢失此据点！"

    @classmethod
    async def action_1104(cls, data: dict):
        server_name = data["server"]
        castle = data["castle"]
        tong = data["tong_name"]
        camp = data["camp_name"]
        time = await gettime(data["time"])
        return f"{server_name},在 {time} {camp} 的 {tong} 帮会成功占领 {castle} 据点！"

    @classmethod
    async def action_1105(cls, data: dict):
        return f"据点占据消息处理(无帮会): {data}"

    @classmethod
    async def action_1106(cls, data: dict):
        return f"结算贡献消息处理: {data}"

    @classmethod
    async def action_2001(cls, data: dict):
        server_name = data["server"]
        status = data["status"]
        if status == 1:
            status = "开张啦！"
        else:
            status = "倒闭啦！"
        if server_name == "青梅煮酒":
            return f"剑网三{status}"



    @classmethod
    async def action_2002(cls, data: dict):
        type = data["type"]
        title = data["title"]
        url = data["url"]
        date = data["date"]
        return f"{type}来了\n{title}\n{url}\n日期：{date}"

    @classmethod
    async def action_2003(cls, data: dict):
        old_version = data["old_version"]
        new_version = data["new_version"]
        package_num = data["package_num"]
        package_size = data["package_size"]
        return f"游戏更新包已发布，\n{old_version} → {new_version}\n {package_num}个更新包，共{package_size}"

    @classmethod
    async def action_2004(cls, data: dict):
        tieba_name = data["name"]
        server_name = data["server"]
        title = data["title"]
        url = data["url"]
        return f"{title}\n吃瓜地址：{url}\n来源：{tieba_name}\n服务器：{server_name}"

    @classmethod
    async def action_2005(cls, data: dict):
        server_name = data["server"]
        castle = data["castle"]
        start = await gettime(data["start"])
        #return f"关隘预告: {server_name},{castle},{start}"
        #默认关闭，太吵了，需要的取消前面的注释符号即可打开

    @classmethod
    async def action_2006(cls, data: dict):
        name = data["name"]
        site = data["site"]
        desc = data["desc"]
        time = await gettime(data["time"])
        return f"云从预告: {site},{name},{desc},{time}"

    # ...


class WebSocket:
    def __init__(self, bot: Bot):
        self.client = None
        self.handler = Handler()
        self.bot = bot

    async def connect(self):
        while True:
            try:
                logger.info("尝试连接 WebSocket 服务器...")
                self.client = await websockets.connect(
                    uri="wss://socket.jx3api.com",
                    extra_headers={'token': TOKEN},
                    ssl=context
                )
                logger.info("建立连接成功...")
                asyncio.create_task(self.receive())
                return
            except Exception as e:
                logger.error(f"连接失败({e})，10秒后重新尝试...")
                await asyncio.sleep(10)

    async def receive(self):
        logger.info("开始接收消息")
        try:
            while self.client.open:
                data = await self.client.recv()
                data = json.loads(data)
                name = f"action_{data['action']}"
                if handler := getattr(self.handler, name, None):
                    message = await handler(data['data'])
                    await self.send_to_all_groups(message)
                logger.info("收到消息: %s", data)
        except Exception as e:
            logger.error(f"连接已断开({e})")
            asyncio.create_task(self.connect())  # 创建重连任务

    async def send_to_all_groups(self, message: str):
        groups = await self.bot.get_group_list()
        for group in groups:
            group_id = group['group_id']
            await self.bot.send_group_msg(group_id=group_id, message=message)
            logger.info(f"已发送消息到群 {group_id}: {message}")



async def gettime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)

    # 将 datetime 对象格式化为小时:分钟字符串
    formatted_time = dt.strftime("%H:%M")

    return formatted_time
async def start_websocket(bot: Bot):
    ws = WebSocket(bot)
    await ws.connect()


@driver.on_startup
async def on_startup():
    logger.info("正在启动 jx3_websocket...")


def register_bot_connect_handler():
    @driver.on_bot_connect
    async def on_bot_connect(bot: Bot):
        logger.info("Bot 已连接，启动 WebSocket 连接...")
        await start_websocket(bot)


register_bot_connect_handler()


@driver.on_shutdown
async def on_shutdown():
    logger.info("正在关闭 jx3_websocket...")
    # 关闭 WebSocket 连接的逻辑可以添加在这里
