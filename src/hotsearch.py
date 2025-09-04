"""热搜榜单API模块"""
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from loguru import logger

class HotSearchItem(BaseModel):
    """热搜条目数据模型"""
    rank: int  # 排名
    title: str  # 标题
    url: Optional[str] = None  # 链接
    hot_value: Optional[str] = None  # 热度值
    category: Optional[str] = None  # 分类

class HotSearchData(BaseModel):
    """热搜数据模型"""
    source: str  # 数据源
    update_time: str  # 更新时间
    items: List[HotSearchItem]  # 热搜条目列表

class HotSearchAPI:
    """热搜榜单API客户端"""
    
    def __init__(self):
        # 参考JavaScript代码的API配置，确保包含正确的URL链接
        self.api_configs = {
            "weibo": {
                "name": "微博",
                "url": "https://weibo.com/ajax/statuses/hot_band",
                "path": "data.band_list",
                "title_key": "word",
                "hot_key": "num",
                "url_key": "url",
                "url_template": "https://s.weibo.com/weibo?q={}&rsv_pq=&rsv_t=&oq=&rsv_spt=1"
            },
            "zhihu": {
                "name": "知乎", 
                "url": "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=15&desktop=true",
                "path": "data",
                "title_key": "target.title",
                "hot_key": "detail_text",
                "url_key": "target.url",
                "url_template": "https://www.zhihu.com/hot"
            },
            "douyin": {
                "name": "抖音",
                "url": "https://aweme.snssdk.com/aweme/v1/hot/search/list/",
                "path": "data.word_list",
                "title_key": "word",
                "hot_key": "hot_value",
                "url_key": "",
                "url_template": "https://www.douyin.com/search/{}"
            },
            "toutiao": {
                "name": "今日头条",
                "url": "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
                "path": "data",
                "title_key": "Title",
                "hot_key": "HotValue",
                "url_key": "Url",
                "url_template": "https://www.toutiao.com/"
            },
            "bilibili": {
                "name": "哔哩哔哩",
                "url": "https://api.bilibili.com/x/web-interface/ranking/v2",
                "path": "data.list",
                "title_key": "title",
                "hot_key": "play",
                "url_key": "short_link_v2",
                "url_template": "https://www.bilibili.com/"
            },
            "baidu": {
                "name": "百度",
                "url": "https://tenapi.cn/v2/baiduhot",
                "path": "data",
                "title_key": "title",
                "hot_key": "index",
                "url_key": "url",
                "url_template": "https://www.baidu.com/s?wd={}"
            },
            "tieba": {
                "name": "百度贴吧",
                "url": "https://tieba.baidu.com/hottopic/browse/topicList",
                "path": "data.bang_topic.topic_list",
                "title_key": "topic_name",
                "hot_key": "discuss_num",
                "url_key": "topic_url",
                "url_template": "https://tieba.baidu.com/"
            }
        }
    
    def _get_nested_value(self, data: dict, path: str):
        """获取嵌套字典的值"""
        keys = path.split('.')
        value = data
        try:
            for key in keys:
                if isinstance(value, list) and key.isdigit():
                    value = value[int(key)]
                else:
                    value = value[key]
            return value
        except (KeyError, IndexError, TypeError):
            return None
    
    def _fetch_hotsearch(self, source_type: str, limit: int = 15) -> Optional[HotSearchData]:
        """通用热搜获取方法"""
        if source_type not in self.api_configs:
            logger.error(f"不支持的热搜源: {source_type}")
            return None
        
        config = self.api_configs[source_type]
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": config["url"]
            }
            
            # 支持GET参数
            params = config.get("params", {})
            response = requests.get(config["url"], headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"获取{config['name']}热搜数据成功")
            
            # 获取列表数据
            items_data = self._get_nested_value(data, config["path"])
            if not items_data:
                logger.warning(f"{config['name']}热搜数据为空")
                return None
            
            items = []
            for i, item_data in enumerate(items_data[:limit], 1):
                title = self._get_nested_value(item_data, config["title_key"])
                hot_value = self._get_nested_value(item_data, config["hot_key"])
                url = self._get_nested_value(item_data, config["url_key"]) if config["url_key"] else ""
                
                # 如果没有直接的URL，使用模板生成URL
                if not url and config.get("url_template"):
                    if "{}" in config["url_template"]:
                        import urllib.parse
                        encoded_title = urllib.parse.quote(str(title))
                        url = config["url_template"].format(encoded_title)
                    else:
                        url = config["url_template"]
                
                if title:  # 只有标题不为空才添加
                    hot_item = HotSearchItem(
                        rank=i,
                        title=str(title),
                        url=str(url) if url else "",
                        hot_value=str(hot_value) if hot_value else "",
                        category="热门"
                    )
                    items.append(hot_item)
            
            if not items:
                logger.warning(f"{config['name']}未获取到有效数据")
                return None
            
            from datetime import datetime
            return HotSearchData(
                source=config["name"],
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                items=items
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求{config['name']}热搜API失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析{config['name']}热搜数据失败: {e}")
            return None
    
    def get_weibo_hot(self) -> Optional[HotSearchData]:
        """获取微博热搜"""
        return self._fetch_hotsearch("weibo")
    
    def get_zhihu_hot(self) -> Optional[HotSearchData]:
        """获取知乎热榜"""
        return self._fetch_hotsearch("zhihu")
    
    def get_douyin_hot(self) -> Optional[HotSearchData]:
        """获取抖音热搜"""
        return self._fetch_hotsearch("douyin")
    
    def get_toutiao_hot(self) -> Optional[HotSearchData]:
        """获取今日头条热搜"""
        return self._fetch_hotsearch("toutiao")
    
    def get_bilibili_hot(self) -> Optional[HotSearchData]:
        """获取哔哩哔哩热榜"""
        return self._fetch_hotsearch("bilibili")
    
    def get_baidu_hot(self) -> Optional[HotSearchData]:
        """获取百度热搜"""
        return self._fetch_hotsearch("baidu")
    
    def get_tieba_hot(self) -> Optional[HotSearchData]:
        """获取百度贴吧热搜"""
        return self._fetch_hotsearch("tieba")
    
    def get_hot_by_source(self, source: str) -> Optional[HotSearchData]:
        """根据来源获取热搜数据"""
        source_methods = {
            "weibo": self.get_weibo_hot,
            "zhihu": self.get_zhihu_hot,
            "douyin": self.get_douyin_hot,
            "toutiao": self.get_toutiao_hot,
            "bilibili": self.get_bilibili_hot,
            "baidu": self.get_baidu_hot,
            "tieba": self.get_tieba_hot
        }
        
        method = source_methods.get(source.lower())
        if method:
            return method()
        else:
            logger.error(f"不支持的热搜源: {source}")
            return None
    
    def get_available_sources(self) -> List[str]:
        """获取可用的热搜源列表"""
        return list(self.api_configs.keys())
    
