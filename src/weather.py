"""彩玉天气API调用模块"""
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from loguru import logger

class HourlyWeatherData(BaseModel):
    """小时级天气数据模型"""
    datetime: datetime  # 时间
    temperature: float  # 温度
    humidity: float  # 湿度
    weather_desc: str  # 天气描述
    wind_speed: float  # 风速
    wind_direction: float  # 风向
    precipitation: float = 0.0  # 降水量

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
    hourly_forecast: List[HourlyWeatherData] = []  # 未来2小时预报

class WeatherAPI:
    """彩玉天气API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.caiyunapp.com/v2.6"
    
    def get_weather(self, longitude: float, latitude: float) -> Optional[WeatherData]:
        """获取天气数据（包含实时数据和未来2小时预报）"""
        try:
            # 获取实时天气数据
            realtime_data = self._get_realtime_weather(longitude, latitude)
            if not realtime_data:
                return None
            
            # 获取小时级预报数据
            hourly_forecast = self._get_hourly_forecast(longitude, latitude, hours=2)
            
            # 合并数据
            realtime_data.hourly_forecast = hourly_forecast
            
            return realtime_data
            
        except Exception as e:
            logger.error(f"获取天气数据失败: {e}")
            return None
    
    def _get_realtime_weather(self, longitude: float, latitude: float) -> Optional[WeatherData]:
        """获取实时天气数据"""
        try:
            url = f"{self.base_url}/{self.api_key}/{longitude},{latitude}/realtime"
            
            headers = {
                "User-Agent": "WeatherBot/1.0",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"获取实时天气数据成功: {data.get('status')}")
            
            if data.get("status") != "ok":
                logger.error(f"实时天气API返回错误状态: {data.get('status')}")
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
            logger.error(f"请求实时天气API失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析实时天气数据失败: {e}")
            return None
    
    def _get_hourly_forecast(self, longitude: float, latitude: float, hours: int = 2) -> List[HourlyWeatherData]:
        """获取小时级预报数据"""
        try:
            url = f"{self.base_url}/{self.api_key}/{longitude},{latitude}/hourly"
            
            headers = {
                "User-Agent": "WeatherBot/1.0",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"获取小时级预报数据成功: {data.get('status')}")
            
            if data.get("status") != "ok":
                logger.error(f"小时级预报API返回错误状态: {data.get('status')}")
                return []
            
            result = data.get("result", {})
            hourly = result.get("hourly", {})
            
            # 获取各项数据的时间序列
            temperature = hourly.get("temperature", [])
            humidity = hourly.get("humidity", [])
            skycon = hourly.get("skycon", [])
            wind = hourly.get("wind", [])
            precipitation = hourly.get("precipitation", [])
            
            hourly_data = []
            current_time = datetime.now()
            
            # 只取未来指定小时数的数据
            for i in range(min(hours, len(temperature))):
                try:
                    forecast_time = current_time + timedelta(hours=i+1)
                    
                    # 安全获取数据，处理数组长度不一致的情况
                    temp = temperature[i].get("value", 0) if i < len(temperature) else 0
                    humid = humidity[i].get("value", 0) * 100 if i < len(humidity) else 0  # 转换为百分比
                    sky = skycon[i].get("value", "") if i < len(skycon) else ""
                    wind_data = wind[i] if i < len(wind) else {}
                    precip = precipitation[i].get("value", 0) if i < len(precipitation) else 0
                    
                    wind_speed = wind_data.get("speed", 0) if wind_data else 0
                    wind_direction = wind_data.get("direction", 0) if wind_data else 0
                    
                    hourly_weather = HourlyWeatherData(
                        datetime=forecast_time,
                        temperature=temp,
                        humidity=humid,
                        weather_desc=self._get_weather_description(sky),
                        wind_speed=wind_speed,
                        wind_direction=wind_direction,
                        precipitation=precip
                    )
                    
                    hourly_data.append(hourly_weather)
                    
                except Exception as e:
                    logger.warning(f"解析第{i+1}小时预报数据失败: {e}")
                    continue
            
            logger.info(f"成功获取{len(hourly_data)}小时的预报数据")
            return hourly_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求小时级预报API失败: {e}")
            return []
        except Exception as e:
            logger.error(f"解析小时级预报数据失败: {e}")
            return []
    
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
