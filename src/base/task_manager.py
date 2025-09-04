"""任务管理器"""
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from .task_base import TaskBase

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskBase] = {}
    
    def register_task(self, task: TaskBase) -> bool:
        """注册任务"""
        try:
            if task.name in self.tasks:
                logger.warning(f"任务 {task.name} 已存在，将被覆盖")
            
            self.tasks[task.name] = task
            logger.info(f"任务 {task.name} 注册成功")
            return True
            
        except Exception as e:
            logger.error(f"注册任务 {task.name} 失败: {e}")
            return False
    
    def unregister_task(self, task_name: str) -> bool:
        """注销任务"""
        try:
            if task_name in self.tasks:
                del self.tasks[task_name]
                logger.info(f"任务 {task_name} 注销成功")
                return True
            else:
                logger.warning(f"任务 {task_name} 不存在")
                return False
                
        except Exception as e:
            logger.error(f"注销任务 {task_name} 失败: {e}")
            return False
    
    def get_task(self, task_name: str) -> Optional[TaskBase]:
        """获取任务"""
        return self.tasks.get(task_name)
    
    def list_tasks(self) -> List[str]:
        """列出所有任务名称"""
        return list(self.tasks.keys())
    
    def execute_task(self, task_name: str) -> bool:
        """执行指定任务"""
        task = self.get_task(task_name)
        if not task:
            logger.error(f"任务 {task_name} 不存在")
            return False
        
        if not task.enabled:
            logger.warning(f"任务 {task_name} 已禁用，跳过执行")
            return False
        
        try:
            task.last_run_time = datetime.now()
            return task.execute()
        except Exception as e:
            logger.error(f"执行任务 {task_name} 异常: {e}")
            return False
    
    def execute_all_tasks(self) -> Dict[str, bool]:
        """执行所有启用的任务"""
        results = {}
        for task_name, task in self.tasks.items():
            if task.enabled:
                results[task_name] = self.execute_task(task_name)
            else:
                logger.info(f"任务 {task_name} 已禁用，跳过执行")
                results[task_name] = None
        
        return results
    
    def enable_task(self, task_name: str) -> bool:
        """启用任务"""
        task = self.get_task(task_name)
        if task:
            task.enable()
            return True
        else:
            logger.error(f"任务 {task_name} 不存在")
            return False
    
    def disable_task(self, task_name: str) -> bool:
        """禁用任务"""
        task = self.get_task(task_name)
        if task:
            task.disable()
            return True
        else:
            logger.error(f"任务 {task_name} 不存在")
            return False
    
    def get_task_status(self, task_name: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.get_task(task_name)
        if task:
            return task.get_status()
        return None
    
    def get_all_task_status(self) -> Dict[str, Dict]:
        """获取所有任务状态"""
        status = {}
        for task_name, task in self.tasks.items():
            status[task_name] = task.get_status()
        return status
