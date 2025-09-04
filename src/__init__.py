"""多任务播报机器人包"""

from .config import config
from .weather import WeatherAPI, WeatherData
from .dingtalk import DingTalkBot
from .formatter import WeatherFormatter
from .hotsearch import HotSearchAPI, HotSearchData
from .hotsearch_formatter import HotSearchFormatter
from .scheduler import MultiTaskScheduler, MultiTaskBot, WeatherBot
from .base import TaskBase, TaskManager

__version__ = "2.0.0"
__author__ = "多任务播报机器人"

__all__ = [
    "config",
    "WeatherAPI",
    "WeatherData", 
    "DingTalkBot",
    "WeatherFormatter",
    "HotSearchAPI",
    "HotSearchData",
    "HotSearchFormatter",
    "MultiTaskScheduler",
    "MultiTaskBot",
    "WeatherBot",  # 向后兼容
    "TaskBase",
    "TaskManager"
]
