"""天气播报任务"""
from typing import Optional, Dict, Any
from loguru import logger
from ..base import TaskBase
from ..weather import WeatherAPI
from ..formatter import WeatherFormatter
from ..config import config

class WeatherTask(TaskBase):
    """天气播报任务"""
    
    def __init__(self, dingtalk_bot):
        super().__init__("天气播报", dingtalk_bot)
        self.weather_api = WeatherAPI(config.caiyun_api_key)
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """获取天气数据"""
        try:
            weather_data = self.weather_api.get_weather(config.longitude, config.latitude)
            if weather_data:
                return {
                    "weather": weather_data,
                    "city_name": config.city_name
                }
            return None
        except Exception as e:
            logger.error(f"获取天气数据失败: {e}")
            return None
    
    def format_message(self, data: Dict[str, Any]) -> tuple[str, str]:
        """格式化天气消息"""
        weather_data = data["weather"]
        city_name = data["city_name"]
        
        return WeatherFormatter.format_markdown_message(weather_data, city_name)
