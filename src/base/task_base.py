"""任务基类"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from loguru import logger
from ..dingtalk import DingTalkBot

class TaskBase(ABC):
    """抽象任务基类"""
    
    def __init__(self, name: str, dingtalk_bot: DingTalkBot):
        self.name = name
        self.dingtalk_bot = dingtalk_bot
        self.enabled = True
        self.last_run_time = None
        self.last_error = None
    
    @abstractmethod
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """获取数据，子类必须实现"""
        pass
    
    @abstractmethod
    def format_message(self, data: Dict[str, Any]) -> tuple[str, str]:
        """格式化消息，返回(title, content)，子类必须实现"""
        pass
    
    def send_message(self, title: str, content: str) -> bool:
        """发送消息到钉钉"""
        try:
            success = self.dingtalk_bot.send_markdown_message(title, content)
            if success:
                logger.info(f"任务 {self.name} 消息发送成功")
            else:
                logger.error(f"任务 {self.name} 消息发送失败")
            return success
        except Exception as e:
            logger.error(f"任务 {self.name} 发送消息异常: {e}")
            return False
    
    def execute(self) -> bool:
        """执行任务"""
        try:
            logger.info(f"开始执行任务: {self.name}")
            
            # 获取数据
            data = self.fetch_data()
            if not data:
                logger.warning(f"任务 {self.name} 未获取到数据")
                return False
            
            # 格式化消息
            title, content = self.format_message(data)
            
            # 发送消息
            success = self.send_message(title, content)
            
            if success:
                self.last_error = None
                logger.info(f"任务 {self.name} 执行成功")
            else:
                self.last_error = "消息发送失败"
                logger.error(f"任务 {self.name} 执行失败: 消息发送失败")
            
            return success
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"任务 {self.name} 执行异常: {e}")
            return False
    
    def enable(self):
        """启用任务"""
        self.enabled = True
        logger.info(f"任务 {self.name} 已启用")
    
    def disable(self):
        """禁用任务"""
        self.enabled = False
        logger.info(f"任务 {self.name} 已禁用")
    
    def get_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "last_run_time": self.last_run_time,
            "last_error": self.last_error
        }
