"""定时任务调度模块"""
import schedule
import time
from datetime import datetime, timedelta
from typing import Callable, Optional, List
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
    
    def _get_next_hour_times(self, interval_hours: int) -> List[str]:
        """计算符合间隔的整点时间列表"""
        times = []
        
        # 从0点开始，按间隔生成所有整点时间
        for hour in range(0, 24, interval_hours):
            time_str = f"{hour:02d}:00"
            times.append(time_str)
        
        return times
    
    def _wait_for_next_hour(self, interval_hours: int):
        """等待到下个符合间隔的整点"""
        current_time = datetime.now()
        
        # 计算下一个整点
        next_hour = current_time.replace(minute=0, second=0, microsecond=0)
        if current_time.minute > 0 or current_time.second > 0:
            next_hour += timedelta(hours=1)
        
        # 如果间隔大于1小时，找到下一个符合间隔的整点
        if interval_hours > 1:
            current_hour = next_hour.hour
            # 找到下一个符合间隔的小时
            next_valid_hour = ((current_hour // interval_hours) + 1) * interval_hours
            if next_valid_hour >= 24:
                # 跨天处理
                next_valid_hour = 0
                next_hour = next_hour.replace(hour=0) + timedelta(days=1)
            else:
                next_hour = next_hour.replace(hour=next_valid_hour)
        
        wait_seconds = (next_hour - current_time).total_seconds()
        
        if wait_seconds > 0:
            logger.info(f"等待 {wait_seconds:.0f} 秒到下个整点 {next_hour.strftime('%H:%M')}")
            time.sleep(wait_seconds)
    
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
        """启动定时任务调度器（整点执行）"""
        try:
            # 验证配置
            config.validate_config()
            
            logger.info(f"启动天气播报定时任务，每{interval_hours}小时在整点执行")
            
            # 设置整点定时任务
            if interval_hours == 1:
                # 每小时整点执行
                schedule.every().hour.at(":00").do(self.send_weather_report)
                logger.info("已设置每小时整点执行任务")
            else:
                # 多小时间隔，设置特定整点时间
                hour_times = self._get_next_hour_times(interval_hours)
                for time_str in hour_times:
                    schedule.every().day.at(time_str).do(self.send_weather_report)
                    logger.info(f"已设置每天{time_str}执行任务")
            
            # 首次执行选择：如果不在整点，先等待到整点
            current_time = datetime.now()
            if current_time.minute == 0 and current_time.second < 30:
                # 如果刚好在整点附近，立即执行
                logger.info("当前为整点，立即执行首次天气播报...")
                self.send_weather_report()
            else:
                # 等待到下个整点
                logger.info("等待下个整点执行首次天气播报...")
                self._wait_for_next_hour(interval_hours)
                if self.is_running:  # 确保没有被停止
                    self.send_weather_report()
            
            self.is_running = True
            
            # 运行调度器
            while self.is_running:
                schedule.run_pending()
                time.sleep(30)  # 每30秒检查一次，提高精度
                
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
        logger.info(f"播报间隔: 每{interval_hours}小时（整点执行）")
        
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
