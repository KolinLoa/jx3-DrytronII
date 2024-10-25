"""
websocket管理器
"""
import asyncio
import inspect
from asyncio import TimeoutError
from enum import Enum
from typing import Generic, Optional, Type, TypeVar

import websockets
from nonebot import get_bots, logger, get_driver
from nonebot.message import handle_event
from websockets.exceptions import ConnectionClosed

from . import event
from .collator import Collator
from .config import MAX_RECONNECT, RECONECT_INTERVAL, WS_URI
from .event import WebsocketAction, WebsocketData, WebsocketEvent, WebsocketNoticeEvent

E = TypeVar("E", bound=WebsocketEvent)

# 获取 NoneBot 的配置对象
driver = get_driver()
config = driver.config


class ManagerStatus(Enum):
    """
    链接状态
    """

    Idle = 0
    """空闲"""
    Connecting = 1
    """正在连接"""
    Connected = 2
    """已连接"""


class WebsocketManager(Generic[E]):
    """
    剑网三websocket管理器
    """

    collator: Collator
    """事件搜索器"""
    status: ManagerStatus
    """链接状态"""

    def __init__(self) -> None:
        self.collator = Collator()
        self.init_event_model()
        self.status = ManagerStatus.Idle

    def init_event_model(self) -> None:
        """
        初始化事件模型
        """
        self.collator.clear()
        for model_name in dir(event):
            model = getattr(event, model_name)
            if not inspect.isclass(model) or not issubclass(model, WebsocketEvent):
                continue
            self.collator.add_model(model)

    def data_to_event(self, data: WebsocketData) -> Optional[Type[E]]:
        """
        data转为事件模型
        """
        try:
            action = WebsocketAction(data.action)
        except ValueError:
            return None
        return self.collator.get_model(action)

    def handle_ws_event(self, event: E) -> None:
        """
        分发ws事件
        """
        bots = get_bots()
        for bot in bots.values():
            asyncio.create_task(handle_event(bot, event))

    def handle_ws_notice(self, event: WebsocketNoticeEvent) -> None:
        """
        分发ws通知事件
        """
        bots = get_bots()
        for bot in bots.values():
            asyncio.create_task(handle_event(bot, event))

    def handle_ws_message(self, message: str) -> None:
        """
        处理ws消息
        """
        websocket_data = WebsocketData.parse_raw(message)
        event_model = self.data_to_event(websocket_data)
        if event_model is None:
            logger.warning(f"未知的ws推送事件: {websocket_data}")
            return
        event = event_model.parse_obj(websocket_data.data)
        self.handle_ws_event(event)

    async def start_websocket_connect(self) -> None:
        """
        开始websocket连接
        """
        if self.status != ManagerStatus.Idle:
            return
        connect_time = 0
        self.status = ManagerStatus.Connecting

        # 从环境变量中获取 token
        token = config.wsstoken
        ws_uri_with_token = f"{WS_URI}?token={token}" if token else WS_URI  # 将 token 添加到 URI

        while connect_time < MAX_RECONNECT:
            try:
                async with websockets.connect(
                        uri=ws_uri_with_token,  # 使用包含 token 的 URI
                        open_timeout=RECONECT_INTERVAL
                ) as websocket:
                    logger.success("websocket连接成功...")
                    self.status = ManagerStatus.Connected
                    try:
                        async for message in websocket:
                            self.handle_ws_message(message)
                    except ConnectionClosed:
                        connect_time = 0
                        logger.success("websocket连接关闭，正在重连...")
                        self.status = ManagerStatus.Connecting
            except (ConnectionRefusedError, TimeoutError):
                connect_time += 1
                logger.error(f"websocket连接超时，正在尝试重连，次数:{connect_time}...")
                self.status = ManagerStatus.Connecting
        logger.error("websocket连接失败，已达最大重连次数，链接退出...")
        self.status = ManagerStatus.Idle
        # 通知管理员
        event = WebsocketNoticeEvent(message="jx3api的websocket已断开！")
        self.handle_ws_notice(event)


manager = WebsocketManager()
"""
websocket管理器
"""
