from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="Jx3Websocket",
    description="接收websocket信息",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

