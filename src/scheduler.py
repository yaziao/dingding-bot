"""定时任务调度模块"""
import time
from datetime import datetime, timedelta
from typing import Callable, Optional, List
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from croniter import croniter
from .base import TaskManager
from .dingtalk import DingTalkBot
from .config import config

class CronTaskScheduler:
    """基于Cron表达式的任务调度器"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.dingtalk_bot = DingTalkBot(config.dingtalk_webhook, config.dingtalk_secret)
        
        # 配置APScheduler
        executors = {
            'default': ThreadPoolExecutor(10),  # 最多10个线程
        }
        
        job_defaults = {
            'coalesce': False,  # 不合并任务
            'max_instances': 1,  # 每个任务最多同时运行1个实例
            'misfire_grace_time': 300  # 容错时间5分钟
        }
        
        self.scheduler = BlockingScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'  # 设置时区
        )
        
        self.is_running = False
    
    def validate_cron_expression(self, cron_expr: str) -> bool:
        """验证cron表达式是否有效"""
        try:
            croniter(cron_expr)
            return True
        except Exception as e:
            logger.error(f"无效的cron表达式 '{cron_expr}': {e}")
            return False
    
    def get_next_run_time(self, cron_expr: str) -> Optional[datetime]:
        """获取cron表达式的下次执行时间"""
        try:
            cron = croniter(cron_expr, datetime.now())
            return cron.get_next(datetime)
        except Exception as e:
            logger.error(f"计算下次执行时间失败: {e}")
            return None
    
    def add_cron_job(self, task_name: str, cron_expr: str, func: Callable, **kwargs):
        """添加cron定时任务"""
        try:
            if not self.validate_cron_expression(cron_expr):
                return False
            
            # 解析cron表达式（APScheduler使用的格式）
            cron_parts = cron_expr.split()
            if len(cron_parts) != 5:
                logger.error(f"cron表达式格式错误，应为5个字段: {cron_expr}")
                return False
            
            minute, hour, day, month, day_of_week = cron_parts
            
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone='Asia/Shanghai'
            )
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_name,
                name=task_name,
                replace_existing=True,
                **kwargs
            )
            
            next_run = self.get_next_run_time(cron_expr)
            logger.info(f"任务 {task_name} 已添加，cron: {cron_expr}, 下次执行: {next_run}")
            return True
            
        except Exception as e:
            logger.error(f"添加cron任务失败: {e}")
            return False
    
    def execute_task_by_name(self, task_name: str) -> bool:
        """执行指定名称的任务"""
        try:
            logger.info(f"执行任务: {task_name}")
            result = self.task_manager.execute_task(task_name)
            
            if result:
                logger.info(f"任务 {task_name} 执行成功")
            else:
                logger.error(f"任务 {task_name} 执行失败")
            
            return result
            
        except Exception as e:
            logger.error(f"执行任务 {task_name} 异常: {e}")
            return False
    
    def register_task(self, task):
        """注册任务"""
        return self.task_manager.register_task(task)
    
    def unregister_task(self, task_name: str):
        """注销任务"""
        return self.task_manager.unregister_task(task_name)
    
    def list_tasks(self):
        """列出所有任务"""
        return self.task_manager.list_tasks()
    
    def get_task_status(self):
        """获取所有任务状态"""
        return self.task_manager.get_all_task_status()
    
    def setup_cron_jobs(self):
        """根据配置设置所有cron任务"""
        try:
            # 获取启用的任务配置
            enabled_configs = config.get_enabled_task_configs()
            
            logger.info("根据配置设置定时任务...")
            
            for task_key, task_config in enabled_configs.items():
                if task_key == "weather":
                    # 天气任务
                    self.add_cron_job(
                        task_name="天气播报",
                        cron_expr=task_config.cron,
                        func=lambda: self.execute_task_by_name("天气播报")
                    )
                elif task_key.startswith("hotsearch"):
                    # 热搜任务
                    if task_key == "hotsearch":
                        task_name = f"热搜榜单-{task_config.source}"
                    else:
                        # hotsearch_zhihu -> 热搜榜单-zhihu
                        source = task_key.split("_", 1)[1]
                        task_name = f"热搜榜单-{source}"
                    
                    self.add_cron_job(
                        task_name=task_name,
                        cron_expr=task_config.cron,
                        func=lambda name=task_name: self.execute_task_by_name(name)
                    )
                else:
                    logger.warning(f"未知的任务类型: {task_key}")
            
            logger.info(f"已设置 {len(enabled_configs)} 个定时任务")
            
        except Exception as e:
            logger.error(f"设置cron任务失败: {e}")
            raise
    
    def start_scheduler(self):
        """启动cron调度器"""
        try:
            # 验证配置
            config.validate_config()
            
            logger.info("启动Cron定时任务调度器...")
            
            # 设置任务
            self.setup_cron_jobs()
            
            # 显示下次执行时间
            self.show_next_run_times()
            
            self.is_running = True
            
            # 启动调度器（阻塞运行）
            logger.info("调度器开始运行...")
            self.scheduler.start()
                
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在停止调度器...")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"调度器运行异常: {e}")
            self.stop_scheduler()
    
    def show_next_run_times(self):
        """显示所有任务的下次执行时间"""
        logger.info("=== 任务执行计划 ===")
        
        enabled_configs = config.get_enabled_task_configs()
        for task_key, task_config in enabled_configs.items():
            next_run = self.get_next_run_time(task_config.cron)
            if next_run:
                logger.info(f"📅 {task_key}: {task_config.cron} -> {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logger.warning(f"⚠️ {task_key}: cron表达式无效 {task_config.cron}")
        
        logger.info("===================")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        logger.info("调度器已停止")
    
    def get_scheduled_jobs(self) -> list:
        """获取所有已调度的任务"""
        return self.scheduler.get_jobs()
    
    def print_jobs(self):
        """打印所有任务信息"""
        jobs = self.get_scheduled_jobs()
        if not jobs:
            logger.info("没有已调度的任务")
            return
        
        logger.info("已调度的任务:")
        for job in jobs:
            logger.info(f"  - {job.id}: {job.next_run_time}")

# 保持向后兼容的别名
MultiTaskScheduler = CronTaskScheduler

class MultiTaskBot:
    """多任务机器人主类"""
    
    def __init__(self):
        self.scheduler = CronTaskScheduler()
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """根据配置设置任务"""
        from .tasks import WeatherTask, HotSearchTask
        
        # 获取启用的任务配置
        enabled_configs = config.get_enabled_task_configs()
        
        for task_key, task_config in enabled_configs.items():
            if task_key == "weather":
                # 注册天气任务
                weather_task = WeatherTask(self.scheduler.dingtalk_bot)
                self.scheduler.register_task(weather_task)
                
            elif task_key.startswith("hotsearch"):
                # 注册热搜任务
                source = task_config.source
                hotsearch_task = HotSearchTask(self.scheduler.dingtalk_bot, source_type=source)
                self.scheduler.register_task(hotsearch_task)
    
    def add_hotsearch_task(self, source_type: str):
        """添加热搜任务"""
        from .tasks import HotSearchTask
        hotsearch_task = HotSearchTask(self.scheduler.dingtalk_bot, source_type=source_type)
        return self.scheduler.register_task(hotsearch_task)
    
    def register_task(self, task):
        """注册新任务"""
        return self.scheduler.register_task(task)
    
    def unregister_task(self, task_name: str):
        """注销任务"""
        return self.scheduler.unregister_task(task_name)
    
    def list_tasks(self):
        """列出所有任务"""
        return self.scheduler.list_tasks()
    
    def get_task_status(self):
        """获取任务状态"""
        return self.scheduler.get_task_status()
    
    def run(self):
        """运行多任务机器人"""
        logger.info("=== 多任务播报机器人启动 ===")
        logger.info(f"城市: {config.city_name}")
        logger.info(f"坐标: {config.longitude}, {config.latitude}")
        
        # 显示已注册的任务
        tasks = self.list_tasks()
        logger.info(f"已注册任务: {', '.join(tasks)}")
        
        try:
            self.scheduler.start_scheduler()
        except Exception as e:
            logger.error(f"机器人运行异常: {e}")
        finally:
            logger.info("=== 多任务播报机器人停止 ===")
    
    def send_test_message(self):
        """发送测试消息"""
        logger.info("执行测试任务...")
        # 执行所有已注册的任务
        results = self.scheduler.task_manager.execute_all_tasks()
        success_count = sum(1 for result in results.values() if result is True)
        total_count = len([r for r in results.values() if r is not None])
        
        logger.info(f"测试完成: {success_count}/{total_count} 成功")
        return success_count > 0

# 保持向后兼容
WeatherBot = MultiTaskBot
