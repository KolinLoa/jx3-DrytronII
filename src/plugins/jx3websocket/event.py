"""
event定义
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from nonebot.adapters.onebot.v11 import Event as OnebotEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.typing import overrides
from pydantic import BaseModel, Field, validator


class WebsocketData(BaseModel):
    """
    websocket推送数据
    """

    action: int
    """推送类型"""
    data: dict
    """推送数据"""


class WebsocketAction(Enum):
    """
    websocket推送类型枚举
    新的
    * 1001 奇遇报时
    * 1002 抓马刷新
    * 1003 抓马捕获
    * 1004 扶摇开启
    * 1005 扶摇结束
    * 1006 烟花报时（已关闭）
    * 1007 玄晶报时
    * 1008 追魂点名
    * 1009 诛恶事件
    * 1010 的卢刷新
    * 1011 的卢捕获
    * 1012 的卢竞拍
    * 1101 粮仓被劫
    * 1102 大将重置
    * 1103 大旗被夺
    * 1104 据点占领(有帮会)
    * 1105 据点占据(无帮会
    * 1106 结算贡献
    * 2001 开服监控
    * 2002 新闻资讯
    * 2003 游戏更新
    * 2004 八卦速报
    * 2005 关隘预告
    * 2006 云从预告
    """

    奇遇报时 = 1001
    抓马刷新 = 1002
    抓马捕获 = 1003
    扶摇开启 = 1004
    扶摇点名 = 1005
    玄晶报时 = 1007
    攻防粮仓 = 1008
    攻防大将 = 1009
    攻防大旗 = 1010
    攻防占领 = 1011
    追魂点名 = 1012
    诛恶事件 = 1013
    开服监控 = 2001
    新闻资讯 = 2002
    游戏更新 = 2003
    八卦速报 = 2004

    def __str__(self) -> str:
        return self.name


class WebsocketNoticeEvent(OnebotEvent):
    """
    ws通知事件
    """

    post_type: Literal["websocket_notice"] = "websocket_notice"
    """事件类型"""
    self_id: int = 0
    time: int = 0
    message: str
    """通知内容"""


class WebsocketEvent(OnebotEvent):
    """
    Websocket事件
    """

    post_type: Literal["jx3_websocket"] = "jx3_websocket"
    """事件类型"""
    sub_type: WebsocketAction = Field(..., alias="action")
    """事件子类型，也是推送类型"""
    self_id: int = 0
    """self_id，固定为0"""
    time: int
    """时间戳"""

    @overrides(OnebotEvent)
    def get_event_name(self) -> str:
        return f"jx3ws事件·{self.sub_type}"

    @overrides(OnebotEvent)
    def get_message(self) -> Message:
        return Message(self.get_event_description())

    @validator("sub_type")
    def get_sub_type(cls, v) -> WebsocketAction:
        return WebsocketAction(v)


class QiyuLevel(Enum):
    """
    奇遇类型
    """

    普通奇遇 = 1
    绝世奇遇 = 2

    def __str__(self) -> str:
        return self.name


class QiyuNoticeEvent(WebsocketEvent):
    """
    奇遇报时事件
    """

    sub_type: str = WebsocketAction.奇遇报时
    server: str
    """服务器名"""
    name: str
    """角色名"""
    event: str
    """奇遇名"""
    level: QiyuLevel
    """奇遇类型"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        event_time = datetime.fromtimestamp(self.time).strftime("%H:%M:%S")
        return (
            f"【{event_time}】{self.server} 的 {self.name} 获取了[{self.level}]: {self.event}"
        )


class ZhuamaNewEvent(WebsocketEvent):
    """
    抓马刷新事件
    """

    sub_type: str = WebsocketAction.抓马刷新
    server: str
    """服务器名"""
    map_name: str
    """地图名"""
    min_time: int
    """最小出没时间"""
    max_time: int
    """最大出没时间"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {self.map_name} 抓马时间刷新了"


class ZhuamaCatchEvent(WebsocketEvent):
    """
    抓马捕获事件
    """

    sub_type: str = WebsocketAction.抓马捕获
    server: str
    """服务器名"""
    name: str
    """角色名"""
    map_name: str
    """地图名"""
    horse: str
    """马匹名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {self.name} 在 {self.map_name} 捕获了 {self.horse}"


class FuyaoOpenEvent(WebsocketEvent):
    """
    扶摇开启事件
    """

    sub_type: str = WebsocketAction.扶摇开启
    server: str
    """服务器名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 扶摇 开启了"


class FuyaoCallEvent(WebsocketEvent):
    """
    扶摇点名事件
    """

    sub_type: str = WebsocketAction.扶摇点名
    server: str
    """服务器名"""
    name: list[str]
    """角色名列表"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {', '.join(self.name)} 点名了"


class XuanjingEvent(WebsocketEvent):
    """
    玄晶报时事件
    """

    sub_type: str = WebsocketAction.玄晶报时
    server: str
    """服务器名"""
    role_name: str
    """角色名"""
    map_name: str
    """地图名"""
    name: str
    """玄晶名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {self.role_name} 在 {self.map_name} 获取了 {self.name}"


class GongfangLiangcangEvent(WebsocketEvent):
    """
    攻防粮仓事件
    """

    sub_type: str = WebsocketAction.攻防粮仓
    server: str
    """服务器名"""
    castle: str
    """城池名"""
    camp_name: str
    """阵营名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {self.castle} 粮仓被 {self.camp_name} 占领了"


class GongfangDajiangEvent(WebsocketEvent):
    """
    攻防大将事件
    """

    sub_type: str = WebsocketAction.攻防大将
    server: str
    """服务器名"""
    name: str
    """大将名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 的 {self.name} 被攻陷了"


class GongfangDaqiEvent(WebsocketEvent):
    """
    攻防大旗事件
    """

    sub_type: str = WebsocketAction.攻防大旗
    server: str
    """服务器名"""
    camp_name: str
    """阵营名"""
    map_name: str
    """地图名"""
    castle: str
    """城池名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return (
            f"{self.server} 的 {self.camp_name} 在 {self.map_name} 的 {self.castle} 大旗被夺"
        )


class GongfangZhanlingEvent(WebsocketEvent):
    """
    攻防占领事件
    """

    sub_type: str = WebsocketAction.攻防占领
    server: str
    camp_name: str
    """阵营名"""
    tong_name: str
    """帮会名"""
    castle: str
    """城池名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return (
            f"{self.server} 的 {self.camp_name} 在 {self.castle} 被 {self.tong_name} 占领了"
        )


class ZhuihunEvent(WebsocketEvent):
    """
    追魂点名事件
    """

    sub_type: str = WebsocketAction.追魂点名
    zone: str
    """服务器名"""
    server: str
    """大区名"""
    subserver: str
    """分区名"""
    name: str
    """角色名"""
    realm: str
    """境界名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"先锋队执事：请[{self.subserver}·{self.name}]侠士速来[{self.realm}]·跨服烂柯山！"


class ZhueEvent(WebsocketEvent):
    """
    诛恶事件
    """

    sub_type: str = WebsocketAction.诛恶事件
    zone: str
    """服务器名"""
    server: str
    """大区名"""
    map_name: str
    """地图名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server}: 诛恶事件触发！众侠士可前往【{self.map_name}】一探究竟。"


class ServerOpenEvent(WebsocketEvent):
    """
    开服事件
    """

    sub_type: str = WebsocketAction.开服监控
    time: int = 0
    server: str
    """服务器名"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"{self.server} 开服了"


class NewsEvent(WebsocketEvent):
    """
    新闻资讯事件
    """

    sub_type: str = WebsocketAction.新闻资讯
    time: int = 0
    type: str
    """新闻类型"""
    title: str
    """新闻标题"""
    url: str
    """新闻链接"""
    date: str
    """新闻日期"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"[{self.type}]: {self.title} {self.url} {self.date}"


class UpdateEvent(WebsocketEvent):
    """
    游戏更新事件
    """

    sub_type: str = WebsocketAction.游戏更新
    time: int = 0
    old_version: str
    """旧版本号"""
    new_version: str
    """新版本号"""
    package_num: int
    """更新包数量"""
    package_size: str
    """更新包大小"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return (
            f"游戏更新啦！版本号：{self.old_version} -> {self.new_version}，"
            f"更新包数量：{self.package_num}，更新包大小：{self.package_size}"
        )


class BaguaEvent(WebsocketEvent):
    """
    八卦事件
    """

    sub_type: str = WebsocketAction.八卦速报
    time: int = 0
    source: str = Field(..., alias="class")
    """八卦来源"""
    server: str
    """服务器名"""
    name: str
    """大区名"""
    title: str
    """标题"""
    url: str
    """链接"""
    date: str
    """日期"""

    @overrides(WebsocketEvent)
    def get_event_description(self) -> str:
        return f"[{self.source}]: {self.title} {self.url} {self.date}"
