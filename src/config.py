"""配置管理模块"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TaskConfig(BaseModel):
    """任务配置类"""
    cron: str = Field(..., description="cron表达式")
    enabled: bool = Field(default=True, description="是否启用")
    source: Optional[str] = Field(None, description="数据源（热搜任务专用）")

class Config(BaseModel):
    """应用配置类"""
    # 彩玉天气API配置
    caiyun_api_key: str = Field(..., description="彩玉天气API密钥")
    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")
    
    # 钉钉机器人配置
    dingtalk_webhook: str = Field(..., description="钉钉机器人Webhook地址")
    dingtalk_secret: Optional[str] = Field(None, description="钉钉机器人密钥")
    
    # 其他配置
    city_name: str = Field(default="未知城市", description="城市名称")
    
    # 任务配置
    task_configs: Dict[str, TaskConfig] = Field(default_factory=dict, description="任务配置字典")
    
    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置实例"""
        # 基础配置
        config = cls(
            caiyun_api_key=os.getenv("CAIYUN_API_KEY", ""),
            longitude=float(os.getenv("LONGITUDE", "116.4074")),
            latitude=float(os.getenv("LATITUDE", "39.9042")),
            dingtalk_webhook=os.getenv("DINGTALK_WEBHOOK", ""),
            dingtalk_secret=os.getenv("DINGTALK_SECRET"),
            city_name=os.getenv("CITY_NAME", "北京")
        )
        
        # 加载任务配置
        config._load_task_configs()
        
        return config
    
    def _load_task_configs(self):
        """加载任务配置"""
        # 天气任务配置
        weather_cron = os.getenv("WEATHER_TASK_CRON", "0 * * * *")
        weather_enabled = os.getenv("WEATHER_TASK_ENABLED", "true").lower() == "true"
        self.task_configs["weather"] = TaskConfig(
            cron=weather_cron,
            enabled=weather_enabled
        )
        
        # 热搜任务配置
        hotsearch_cron = os.getenv("HOTSEARCH_TASK_CRON", "0 */2 * * *")
        hotsearch_enabled = os.getenv("HOTSEARCH_TASK_ENABLED", "true").lower() == "true"
        hotsearch_source = os.getenv("HOTSEARCH_TASK_SOURCE", "weibo")
        self.task_configs["hotsearch"] = TaskConfig(
            cron=hotsearch_cron,
            enabled=hotsearch_enabled,
            source=hotsearch_source
        )
        
        # 加载其他热搜源配置
        self._load_additional_hotsearch_configs()
    
    def _load_additional_hotsearch_configs(self):
        """加载额外的热搜源配置"""
        hotsearch_sources = ["zhihu", "douyin", "toutiao", "bilibili", "baidu"]
        
        for source in hotsearch_sources:
            env_prefix = f"HOTSEARCH_{source.upper()}"
            cron_key = f"{env_prefix}_CRON"
            enabled_key = f"{env_prefix}_ENABLED"
            
            if os.getenv(cron_key):  # 只有配置了cron才加载
                cron = os.getenv(cron_key)
                enabled = os.getenv(enabled_key, "true").lower() == "true"
                task_key = f"hotsearch_{source}"
                
                self.task_configs[task_key] = TaskConfig(
                    cron=cron,
                    enabled=enabled,
                    source=source
                )
    
    def get_task_config(self, task_name: str) -> Optional[TaskConfig]:
        """获取任务配置"""
        return self.task_configs.get(task_name)
    
    def get_enabled_task_configs(self) -> Dict[str, TaskConfig]:
        """获取所有启用的任务配置"""
        return {name: config for name, config in self.task_configs.items() if config.enabled}
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.caiyun_api_key:
            raise ValueError("彩玉天气API密钥不能为空")
        if not self.dingtalk_webhook:
            raise ValueError("钉钉机器人Webhook地址不能为空")
        return True

# 全局配置实例
config = Config.from_env()
