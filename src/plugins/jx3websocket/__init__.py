import asyncio

from nonebot import get_driver, logger, on_command
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent
from nonebot.plugin import PluginMetadata, on

from .event import WebsocketEvent, WebsocketNoticeEvent
from .websocket import ManagerStatus, manager

__plugin_meta__ = PluginMetadata(
    name="jx3_websocket",
    description="剑网三websocket消息推送",
    usage="接收jx3api.com的消息",
    extra={},
)


driver = get_driver()

event_handler = on("jx3_websocket", priority=1, block=True)
notice_handler = on("websocket_notice", priority=1, block=True)
command_handler = on_command("重连", priority=1, block=True)


@driver.on_startup
async def _() -> None:
    logger.info("正在启动jx3_websocket...")
    asyncio.create_task(manager.start_websocket_connect())


@event_handler.handle()
async def handle_ws_event(bot: Bot, event: WebsocketEvent) -> None:
    """
    处理websocket事件
    """
    groups = await bot.get_group_list()
    for group in groups:
        await bot.send_group_msg(
            group_id=group["group_id"], message=event.get_message()
        )
    await event_handler.finish()


@notice_handler.handle()
async def handle_ws_notice(bot: Bot, event: WebsocketNoticeEvent) -> None:
    """
    处理ws通知事件
    """
    suerusers = driver.config.superusers
    for user in suerusers:
        await bot.send_private_msg(user_id=user, message=event.message)
    await notice_handler.finish()


@command_handler.handle()
async def handle_command(bot: Bot, event: PrivateMessageEvent) -> None:
    """
    处理重连命令
    """
    if manager.status != ManagerStatus.Idle:
        await bot.send_private_msg(user_id=event.user_id, message="ws状态错误...")
        return
    asyncio.create_task(manager.start_websocket_connect())
    await command_handler.finish("正在重连...")
