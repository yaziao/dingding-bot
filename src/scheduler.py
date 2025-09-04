"""定时任务调度模块"""
import schedule
import time
from datetime import datetime
from typing import Callable, Optional
from loguru import logger
from .weather import WeatherAPI, WeatherData
from .dingtalk import DingTalkBot
from .formatter import WeatherFormatter
from .config import config

class WeatherScheduler:
    """天气播报定时任务调度器"""
    
    def __init__(self):
        self.weather_api = WeatherAPI(config.caiyun_api_key)
        self.dingtalk_bot = DingTalkBot(config.dingtalk_webhook, config.dingtalk_secret)
        self.is_running = False
    
    def send_weather_report(self) -> bool:
        """发送天气播报"""
        try:
            logger.info("开始获取天气数据...")
            
            # 获取天气数据
            weather_data = self.weather_api.get_weather(config.longitude, config.latitude)
            if not weather_data:
                logger.error("获取天气数据失败")
                return False
            
            logger.info(f"成功获取天气数据: {weather_data.weather_desc}, {weather_data.temperature}°C")
            
            # 格式化消息
            title, content = WeatherFormatter.format_markdown_message(weather_data, config.city_name)
            
            # 发送到钉钉
            success = self.dingtalk_bot.send_markdown_message(title, content)
            
            if success:
                logger.info("天气播报发送成功")
            else:
                logger.error("天气播报发送失败")
            
            return success
            
        except Exception as e:
            logger.error(f"发送天气播报异常: {e}")
            return False
    
    def start_scheduler(self, interval_hours: int = 1):
        """启动定时任务调度器"""
        try:
            # 验证配置
            config.validate_config()
            
            logger.info(f"启动天气播报定时任务，每{interval_hours}小时执行一次")
            
            # 设置定时任务
            schedule.every(interval_hours).hours.do(self.send_weather_report)
            
            # 首次立即执行
            logger.info("立即执行首次天气播报...")
            self.send_weather_report()
            
            self.is_running = True
            
            # 运行调度器
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在停止调度器...")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"调度器运行异常: {e}")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        logger.info("调度器已停止")
    
    def add_custom_schedule(self, time_str: str, func: Callable):
        """添加自定义定时任务"""
        try:
            schedule.every().day.at(time_str).do(func)
            logger.info(f"添加自定义定时任务: 每天{time_str}执行")
        except Exception as e:
            logger.error(f"添加自定义定时任务失败: {e}")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次运行时间"""
        jobs = schedule.jobs
        if not jobs:
            return None
        
        next_run = min(job.next_run for job in jobs)
        return next_run
    
    def list_jobs(self) -> list:
        """列出所有定时任务"""
        return [str(job) for job in schedule.jobs]

class WeatherBot:
    """天气机器人主类"""
    
    def __init__(self):
        self.scheduler = WeatherScheduler()
    
    def run(self, interval_hours: int = 1):
        """运行天气机器人"""
        logger.info("=== 天气播报机器人启动 ===")
        logger.info(f"城市: {config.city_name}")
        logger.info(f"坐标: {config.longitude}, {config.latitude}")
        logger.info(f"播报间隔: 每{interval_hours}小时")
        
        try:
            self.scheduler.start_scheduler(interval_hours)
        except Exception as e:
            logger.error(f"机器人运行异常: {e}")
        finally:
            logger.info("=== 天气播报机器人停止 ===")
    
    def send_test_message(self):
        """发送测试消息"""
        logger.info("发送测试天气播报...")
        success = self.scheduler.send_weather_report()
        return success
