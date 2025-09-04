"""彩玉天气API调用模块"""
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

class WeatherData(BaseModel):
    """天气数据模型"""
    temperature: float  # 温度
    humidity: float  # 湿度
    pressure: float  # 气压
    wind_speed: float  # 风速
    wind_direction: float  # 风向
    visibility: float  # 能见度
    weather_desc: str  # 天气描述
    aqi: Optional[int] = None  # 空气质量指数
    pm25: Optional[float] = None  # PM2.5
    pm10: Optional[float] = None  # PM10

class WeatherAPI:
    """彩玉天气API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.caiyunapp.com/v2.6"
    
    def get_weather(self, longitude: float, latitude: float) -> Optional[WeatherData]:
        """获取天气数据"""
        try:
            url = f"{self.base_url}/{self.api_key}/{longitude},{latitude}/realtime"
            
            headers = {
                "User-Agent": "WeatherBot/1.0",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"获取天气数据成功: {data.get('status')}")
            
            if data.get("status") != "ok":
                logger.error(f"天气API返回错误状态: {data.get('status')}")
                return None
            
            result = data.get("result", {})
            realtime = result.get("realtime", {})
            
            # 解析天气数据
            weather_data = WeatherData(
                temperature=realtime.get("temperature", 0),
                humidity=realtime.get("humidity", 0) * 100,  # 转换为百分比
                pressure=realtime.get("pressure", 0),
                wind_speed=realtime.get("wind", {}).get("speed", 0),
                wind_direction=realtime.get("wind", {}).get("direction", 0),
                visibility=realtime.get("visibility", 0),
                weather_desc=self._get_weather_description(realtime.get("skycon", "")),
                aqi=realtime.get("air_quality", {}).get("aqi", {}).get("chn", None),
                pm25=realtime.get("air_quality", {}).get("pm25", None),
                pm10=realtime.get("air_quality", {}).get("pm10", None)
            )
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求天气API失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析天气数据失败: {e}")
            return None
    
    def _get_weather_description(self, skycon: str) -> str:
        """将skycon代码转换为中文描述"""
        weather_map = {
            "CLEAR_DAY": "晴天",
            "CLEAR_NIGHT": "晴夜",
            "PARTLY_CLOUDY_DAY": "多云",
            "PARTLY_CLOUDY_NIGHT": "多云",
            "CLOUDY": "阴天",
            "LIGHT_HAZE": "轻雾",
            "MODERATE_HAZE": "中雾",
            "HEAVY_HAZE": "重雾",
            "LIGHT_RAIN": "小雨",
            "MODERATE_RAIN": "中雨",
            "HEAVY_RAIN": "大雨",
            "STORM_RAIN": "暴雨",
            "LIGHT_SNOW": "小雪",
            "MODERATE_SNOW": "中雪",
            "HEAVY_SNOW": "大雪",
            "STORM_SNOW": "暴雪",
            "DUST": "浮尘",
            "SAND": "沙尘",
            "WIND": "大风"
        }
        return weather_map.get(skycon, "未知天气")
    
    def _get_wind_direction_desc(self, direction: float) -> str:
        """将风向角度转换为方向描述"""
        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = int((direction + 22.5) // 45) % 8
        return directions[index]
