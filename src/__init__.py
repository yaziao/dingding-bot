"""天气播报机器人包"""

from .config import config
from .weather import WeatherAPI, WeatherData
from .dingtalk import DingTalkBot
from .formatter import WeatherFormatter
from .scheduler import WeatherScheduler, WeatherBot

__version__ = "1.0.0"
__author__ = "天气播报机器人"

__all__ = [
    "config",
    "WeatherAPI",
    "WeatherData", 
    "DingTalkBot",
    "WeatherFormatter",
    "WeatherScheduler",
    "WeatherBot"
]
