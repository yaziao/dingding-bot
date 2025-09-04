"""配置管理模块"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
    
    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置实例"""
        return cls(
            caiyun_api_key=os.getenv("CAIYUN_API_KEY", ""),
            longitude=float(os.getenv("LONGITUDE", "116.4074")),
            latitude=float(os.getenv("LATITUDE", "39.9042")),
            dingtalk_webhook=os.getenv("DINGTALK_WEBHOOK", ""),
            dingtalk_secret=os.getenv("DINGTALK_SECRET"),
            city_name=os.getenv("CITY_NAME", "北京")
        )
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.caiyun_api_key:
            raise ValueError("彩玉天气API密钥不能为空")
        if not self.dingtalk_webhook:
            raise ValueError("钉钉机器人Webhook地址不能为空")
        return True

# 全局配置实例
config = Config.from_env()
