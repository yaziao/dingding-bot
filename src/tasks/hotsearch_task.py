"""热搜榜单任务"""
from typing import Optional, Dict, Any
from loguru import logger
from ..base import TaskBase
from ..hotsearch import HotSearchAPI
from ..hotsearch_formatter import HotSearchFormatter

class HotSearchTask(TaskBase):
    """热搜榜单任务"""
    
    def __init__(self, dingtalk_bot, source_type: str = "weibo"):
        super().__init__(f"热搜榜单-{source_type}", dingtalk_bot)
        self.hotsearch_api = HotSearchAPI()
        self.source_type = source_type.lower()
        
        # 验证数据源是否支持
        available_sources = self.hotsearch_api.get_available_sources()
        if self.source_type not in available_sources:
            logger.warning(f"数据源 {source_type} 不在支持列表中: {available_sources}，将使用微博作为默认源")
            self.source_type = "weibo"
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """获取热搜数据"""
        try:
            hotsearch_data = self.hotsearch_api.get_hot_by_source(self.source_type)
            
            if hotsearch_data:
                return {"hotsearch": hotsearch_data}
            return None
            
        except Exception as e:
            logger.error(f"获取热搜数据失败: {e}")
            return None
    
    def format_message(self, data: Dict[str, Any]) -> tuple[str, str]:
        """格式化热搜消息"""
        hotsearch_data = data["hotsearch"]
        return HotSearchFormatter.format_markdown_message(hotsearch_data)
