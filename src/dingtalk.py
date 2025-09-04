"""钉钉机器人消息推送模块"""
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from typing import Dict, Any, Optional
from loguru import logger

class DingTalkBot:
    """钉钉机器人客户端"""
    
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _generate_sign(self, timestamp: str) -> str:
        """生成签名"""
        if not self.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign
    
    def _get_signed_url(self) -> str:
        """获取带签名的URL"""
        if not self.secret:
            return self.webhook_url
        
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)
        return f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
    
    def send_text_message(self, content: str, at_all: bool = False) -> bool:
        """发送文本消息"""
        try:
            url = self._get_signed_url()
            
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "isAtAll": at_all
                }
            }
            
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("钉钉消息发送成功")
                return True
            else:
                logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"发送钉钉消息异常: {e}")
            return False
    
    def send_markdown_message(self, title: str, text: str, at_all: bool = False) -> bool:
        """发送Markdown消息"""
        try:
            url = self._get_signed_url()
            
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {
                    "isAtAll": at_all
                }
            }
            
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("钉钉Markdown消息发送成功")
                return True
            else:
                logger.error(f"钉钉Markdown消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"发送钉钉Markdown消息异常: {e}")
            return False
    
    def send_action_card(self, title: str, text: str, single_title: str = "", single_url: str = "") -> bool:
        """发送ActionCard消息"""
        try:
            url = self._get_signed_url()
            
            data = {
                "msgtype": "actionCard",
                "actionCard": {
                    "title": title,
                    "text": text,
                    "hideAvatar": "0",
                    "btnOrientation": "0"
                }
            }
            
            if single_title and single_url:
                data["actionCard"]["singleTitle"] = single_title
                data["actionCard"]["singleURL"] = single_url
            
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("钉钉ActionCard消息发送成功")
                return True
            else:
                logger.error(f"钉钉ActionCard消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"发送钉钉ActionCard消息异常: {e}")
            return False
