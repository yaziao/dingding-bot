"""天气数据美化格式化模块"""
from datetime import datetime
from typing import Optional
from .weather import WeatherData

class WeatherFormatter:
    """天气数据格式化器"""
    
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
        
        if not tips:
            tips.append("🌈 天气不错，适合外出活动！")
        
        for tip in tips:
            content += f"- {tip}\n"
        
        return title, content
