"""
websocket事件搜索器
"""
from typing import Generic, Type, TypeVar

from .event import WebsocketAction, WebsocketEvent

E = TypeVar("E", bound=WebsocketEvent)


class Collator(Generic[E]):
    """
    事件搜索器
    """

    events: dict[WebsocketAction, Type[E]]
    """事件模型字典"""

    def __init__(self) -> None:
        self.events = {}

    def clear(self) -> None:
        """
        清理模型
        """
        self.events.clear()

    def add_model(self, model: Type[E]) -> None:
        """
        添加模型
        """
        sub_type = model.__fields__["sub_type"].default
        self.events[sub_type] = model

    def add_models(self, *models: Type[E]) -> None:
        """
        添加模型
        """
        for model in models:
            self.add_model(model)

    def get_model(self, action: WebsocketAction) -> Type[E]:
        """
        获取模型
        """
        return self.events[action]
