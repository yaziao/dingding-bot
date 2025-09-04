"""天气播报任务"""
from typing import Optional, Dict, Any
from loguru import logger
from ..base import TaskBase
from ..weather import WeatherAPI
from ..formatter import WeatherFormatter
from ..config import config

class WeatherTask(TaskBase):
    """天气播报任务"""
    
    def __init__(self, dingtalk_bot, include_rain_chart: bool = True):
        super().__init__("天气播报", dingtalk_bot)
        self.weather_api = WeatherAPI(config.caiyun_api_key)
        self.weather_formatter = WeatherFormatter()
        self.include_rain_chart = include_rain_chart
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """获取天气数据"""
        try:
            # 如果包含雨图，需要获取更多小时的预报数据
            weather_data = self.weather_api.get_weather(
                config.longitude, 
                config.latitude, 
                include_rain_forecast=self.include_rain_chart
            )
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
        
        if self.include_rain_chart:
            return self.weather_formatter.format_message_with_rain_chart(
                weather_data, city_name, include_image=True
            )
        else:
            return self.weather_formatter.format_markdown_message(weather_data, city_name)
