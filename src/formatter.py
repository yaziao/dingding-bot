"""天气数据美化格式化模块"""
from datetime import datetime
from typing import Optional, List, Tuple
from loguru import logger
from .weather import WeatherData, HourlyWeatherData
from .rain_visualizer import RainVisualizer

class WeatherFormatter:
    """天气数据格式化器"""
    
    def __init__(self):
        self.rain_visualizer = RainVisualizer()
    
    @staticmethod
    def get_weather_emoji(weather_desc: str) -> str:
        """根据天气描述获取对应的emoji"""
        emoji_map = {
            "晴天": "☀️",
            "晴夜": "🌙",
            "多云": "⛅",
            "阴天": "☁️",
            "轻雾": "🌫️",
            "中雾": "🌫️",
            "重雾": "🌫️",
            "小雨": "🌦️",
            "中雨": "🌧️",
            "大雨": "⛈️",
            "暴雨": "⛈️",
            "小雪": "🌨️",
            "中雪": "❄️",
            "大雪": "❄️",
            "暴雪": "❄️",
            "浮尘": "🌪️",
            "沙尘": "🌪️",
            "大风": "💨"
        }
        return emoji_map.get(weather_desc, "🌈")
    
    @staticmethod
    def get_wind_direction_desc(direction: float) -> str:
        """将风向角度转换为方向描述"""
        directions = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风"]
        index = int((direction + 22.5) // 45) % 8
        return directions[index]
    
    @staticmethod
    def get_aqi_level(aqi: Optional[int]) -> tuple[str, str]:
        """获取空气质量等级和颜色"""
        if aqi is None:
            return "未知", "🔘"
        
        if aqi <= 50:
            return "优", "🟢"
        elif aqi <= 100:
            return "良", "🟡"
        elif aqi <= 150:
            return "轻度污染", "🟠"
        elif aqi <= 200:
            return "中度污染", "🔴"
        elif aqi <= 300:
            return "重度污染", "🟣"
        else:
            return "严重污染", "🔵"
    
    @staticmethod
    def get_temperature_desc(temp: float) -> str:
        """获取温度描述"""
        if temp <= 0:
            return "❄️ 寒冷"
        elif temp <= 10:
            return "🧊 较冷"
        elif temp <= 20:
            return "😊 凉爽"
        elif temp <= 30:
            return "🌡️ 温暖"
        else:
            return "🔥 炎热"
    
    @staticmethod
    def format_hourly_forecast(hourly_data: List[HourlyWeatherData]) -> str:
        """格式化小时级预报数据（分行显示）"""
        if not hourly_data:
            return ""
        
        forecast_text = ""
        for i, hour_data in enumerate(hourly_data):
            time_str = hour_data.datetime.strftime("%H:%M")
            emoji = WeatherFormatter.get_weather_emoji(hour_data.weather_desc)
            wind_desc = WeatherFormatter.get_wind_direction_desc(hour_data.wind_direction)
            
            # 降水信息
            precip_info = ""
            if hour_data.precipitation > 0:
                if hour_data.precipitation < 0.5:
                    precip_info = " (微雨)"
                elif hour_data.precipitation < 2.0:
                    precip_info = " (小雨)"
                elif hour_data.precipitation < 10.0:
                    precip_info = " (中雨)"
                else:
                    precip_info = " (大雨)"
            
            forecast_text += f"\n\n**📅 {i+1}小时后 ({time_str})**\n"
            forecast_text += f"- **温度：** {hour_data.temperature:.1f}°C\n"
            forecast_text += f"- **天气：** {emoji} {hour_data.weather_desc}{precip_info}\n"
            forecast_text += f"- **湿度：** 💧 {hour_data.humidity:.1f}%\n"
            forecast_text += f"- **风向风速：** 💨 {wind_desc} {hour_data.wind_speed:.1f}m/s"
        
        return forecast_text
    
    @staticmethod
    def format_text_message(weather_data: WeatherData, city_name: str) -> str:
        """格式化为文本消息"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        weather_emoji = WeatherFormatter.get_weather_emoji(weather_data.weather_desc)
        wind_desc = WeatherFormatter.get_wind_direction_desc(weather_data.wind_direction)
        temp_desc = WeatherFormatter.get_temperature_desc(weather_data.temperature)
        
        message = f"""🌤️ {city_name}天气播报 🌤️

📅 更新时间：{current_time}

🌡️ 温度：{weather_data.temperature:.1f}°C {temp_desc}
{weather_emoji} 天气：{weather_data.weather_desc}
💧 湿度：{weather_data.humidity:.1f}%
💨 风向风速：{wind_desc} {weather_data.wind_speed:.1f}m/s
👁️ 能见度：{weather_data.visibility:.1f}km
🏔️ 气压：{weather_data.pressure:.1f}hPa"""
        
        # 添加空气质量信息
        if weather_data.aqi is not None:
            aqi_level, aqi_emoji = WeatherFormatter.get_aqi_level(weather_data.aqi)
            message += f"\n\n🫁 空气质量"
            message += f"\n{aqi_emoji} AQI：{weather_data.aqi} ({aqi_level})"
            
            if weather_data.pm25 is not None:
                message += f"\n🔹 PM2.5：{weather_data.pm25:.1f}μg/m³"
            if weather_data.pm10 is not None:
                message += f"\n🔸 PM10：{weather_data.pm10:.1f}μg/m³"
        
        # 添加未来2小时预报
        if weather_data.hourly_forecast:
            message += "\n\n🔮 未来2小时预报："
            for i, hour_data in enumerate(weather_data.hourly_forecast):
                time_str = hour_data.datetime.strftime("%H:%M")
                emoji = WeatherFormatter.get_weather_emoji(hour_data.weather_desc)
                wind_desc = WeatherFormatter.get_wind_direction_desc(hour_data.wind_direction)
                
                # 降水信息
                precip_info = ""
                if hour_data.precipitation > 0:
                    if hour_data.precipitation < 0.5:
                        precip_info = " (微雨)"
                    elif hour_data.precipitation < 2.0:
                        precip_info = " (小雨)"
                    elif hour_data.precipitation < 10.0:
                        precip_info = " (中雨)"
                    else:
                        precip_info = " (大雨)"
                
                message += f"\n\n📅 {i+1}小时后 ({time_str})"
                message += f"\n🌡️ 温度：{hour_data.temperature:.1f}°C"
                message += f"\n{emoji} 天气：{hour_data.weather_desc}{precip_info}"
                message += f"\n💧 湿度：{hour_data.humidity:.1f}%"
                message += f"\n💨 风向：{wind_desc} {hour_data.wind_speed:.1f}m/s"
        
        # 添加贴心提醒
        message += f"\n\n💡 温馨提示："
        if weather_data.temperature <= 5:
            message += "\n❄️ 天气寒冷，注意保暖！"
        elif weather_data.temperature >= 35:
            message += "\n🔥 天气炎热，注意防暑！"
        
        if weather_data.aqi and weather_data.aqi > 100:
            message += "\n😷 空气质量较差，建议减少外出，戴好口罩！"
        
        if "雨" in weather_data.weather_desc:
            message += "\n☂️ 有降雨，记得带伞！"
        
        if weather_data.wind_speed > 10:
            message += "\n💨 风力较大，注意安全！"
        
        # 检查未来2小时是否有降雨
        if weather_data.hourly_forecast:
            has_rain = any(h.precipitation > 0 for h in weather_data.hourly_forecast)
            if has_rain and "雨" not in weather_data.weather_desc:
                message += "\n☂️ 未来2小时可能有降雨，记得带伞！"
        
        return message
    
    @staticmethod
    def format_markdown_message(weather_data: WeatherData, city_name: str) -> tuple[str, str]:
        """格式化为Markdown消息，返回(title, content)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        weather_emoji = WeatherFormatter.get_weather_emoji(weather_data.weather_desc)
        wind_desc = WeatherFormatter.get_wind_direction_desc(weather_data.wind_direction)
        temp_desc = WeatherFormatter.get_temperature_desc(weather_data.temperature)
        
        title = f"🌤️ {city_name}天气播报"
        
        content = f"""## {weather_emoji} {city_name}天气实况

> 📅 **更新时间：** {current_time}

---

### 🌡️ 基本信息
- **温度：** {weather_data.temperature:.1f}°C {temp_desc}
- **天气：** {weather_emoji} {weather_data.weather_desc}
- **湿度：** 💧 {weather_data.humidity:.1f}%
- **风向风速：** 💨 {wind_desc} {weather_data.wind_speed:.1f}m/s
- **能见度：** 👁️ {weather_data.visibility:.1f}km
- **气压：** 🏔️ {weather_data.pressure:.1f}hPa

"""
        
        # 添加空气质量信息
        if weather_data.aqi is not None:
            aqi_level, aqi_emoji = WeatherFormatter.get_aqi_level(weather_data.aqi)
            content += f"""### 🫁 空气质量
- **AQI：** {aqi_emoji} {weather_data.aqi} ({aqi_level})
"""
            if weather_data.pm25 is not None:
                content += f"- **PM2.5：** 🔹 {weather_data.pm25:.1f}μg/m³\n"
            if weather_data.pm10 is not None:
                content += f"- **PM10：** 🔸 {weather_data.pm10:.1f}μg/m³\n"
            content += "\n"
        
        # 添加未来2小时预报
        if weather_data.hourly_forecast:
            content += "\n### 🔮 未来2小时预报\n"
            hourly_forecast = WeatherFormatter.format_hourly_forecast(weather_data.hourly_forecast)
            content += hourly_forecast + "\n\n"
        
        # 添加贴心提醒
        content += "### 💡 温馨提示\n"
        tips = []
        
        if weather_data.temperature <= 5:
            tips.append("❄️ 天气寒冷，注意保暖！")
        elif weather_data.temperature >= 35:
            tips.append("🔥 天气炎热，注意防暑！")
        
        if weather_data.aqi and weather_data.aqi > 100:
            tips.append("😷 空气质量较差，建议减少外出，戴好口罩！")
        
        if "雨" in weather_data.weather_desc:
            tips.append("☂️ 有降雨，记得带伞！")
        
        if weather_data.wind_speed > 10:
            tips.append("💨 风力较大，注意安全！")
        
        # 检查未来2小时是否有降雨
        if weather_data.hourly_forecast:
            has_rain = any(h.precipitation > 0 for h in weather_data.hourly_forecast)
            if has_rain and "雨" not in weather_data.weather_desc:
                tips.append("☂️ 未来2小时可能有降雨，记得带伞！")
        
        if not tips:
            tips.append("🌈 天气不错，适合外出活动！")
        
        for tip in tips:
            content += f"- {tip}\n"
        
        return title, content
    
    def format_message_with_rain_chart(self, weather_data: WeatherData, city_name: str, 
                                     include_image: bool = True) -> tuple[str, str]:
        """格式化天气消息并包含雨图，返回(title, content)"""
        title, content = self.format_markdown_message(weather_data, city_name)
        
        # 添加雨图相关信息
        rain_info = self._get_rain_summary(weather_data)
        if rain_info:
            content += f"\n\n### 🌧️ 降水信息\n{rain_info}\n"
        
        # 生成ASCII雨图（钉钉更兼容）
        try:
            ascii_chart = self.rain_visualizer.generate_simple_rain_chart(weather_data, city_name)
            if ascii_chart:
                content += f"\n### 📊 降水预报图\n```\n{ascii_chart}\n```\n"
            else:
                content += "\n### 📊 降水预报图\n`暂无降水数据`\n"
        except Exception as e:
            logger.warning(f"生成雨图失败: {e}")
            content += "\n### 📊 降水预报图\n`雨图生成失败，请查看降水信息`\n"
        
        return title, content
    
    def _get_rain_summary(self, weather_data: WeatherData) -> str:
        """获取降水摘要信息"""
        summary_lines = []
        
        # 当前降水
        if weather_data.precipitation > 0:
            level = self._get_precipitation_level(weather_data.precipitation)
            summary_lines.append(f"- **当前降水：** {weather_data.precipitation:.1f}mm/h ({level})")
        else:
            summary_lines.append("- **当前降水：** 无降水")
        
        # 未来降水预报
        if weather_data.hourly_forecast:
            has_rain = False
            max_precip = 0
            total_precip = 0
            
            for hour_data in weather_data.hourly_forecast:
                if hour_data.precipitation > 0:
                    has_rain = True
                    max_precip = max(max_precip, hour_data.precipitation)
                    total_precip += hour_data.precipitation
            
            if has_rain:
                avg_precip = total_precip / len(weather_data.hourly_forecast)
                max_level = self._get_precipitation_level(max_precip)
                summary_lines.append(f"- **未来{len(weather_data.hourly_forecast)}小时：** 有降水，最大{max_precip:.1f}mm/h ({max_level})")
                summary_lines.append(f"- **平均降水强度：** {avg_precip:.1f}mm/h")
            else:
                summary_lines.append(f"- **未来{len(weather_data.hourly_forecast)}小时：** 无明显降水")
        
        # 降水建议
        if weather_data.precipitation > 0 or any(h.precipitation > 0 for h in weather_data.hourly_forecast):
            if max(weather_data.precipitation, 
                   max((h.precipitation for h in weather_data.hourly_forecast), default=0)) > 8:
                summary_lines.append("- **出行建议：** ⚠️ 降水较强，建议减少外出，注意安全")
            elif max(weather_data.precipitation,
                    max((h.precipitation for h in weather_data.hourly_forecast), default=0)) > 2:
                summary_lines.append("- **出行建议：** ☂️ 建议携带雨具，注意路面湿滑")
            else:
                summary_lines.append("- **出行建议：** 🌂 可能有小雨，建议备好雨具")
        
        return "\n".join(summary_lines)
    
    def _get_precipitation_level(self, precipitation: float) -> str:
        """获取降水等级描述"""
        if precipitation == 0:
            return "无降水"
        elif precipitation < 0.5:
            return "微雨"
        elif precipitation < 2.0:
            return "小雨"
        elif precipitation < 8.0:
            return "中雨" 
        elif precipitation < 20.0:
            return "大雨"
        else:
            return "暴雨"
