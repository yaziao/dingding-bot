"""热搜榜单格式化模块"""
from datetime import datetime
from typing import Optional
from .hotsearch import HotSearchData, HotSearchItem

class HotSearchFormatter:
    """热搜榜单格式化器"""
    
    @staticmethod
    def get_rank_emoji(rank: int) -> str:
        """根据排名获取对应的emoji"""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        elif rank <= 5:
            return "🔥"
        elif rank <= 10:
            return "📈"
        else:
            return "📊"
    
    @staticmethod
    def get_category_emoji(category: Optional[str]) -> str:
        """根据分类获取对应的emoji"""
        if not category:
            return "📰"
        
        category_map = {
            "娱乐": "🎭",
            "体育": "⚽",
            "科技": "💻",
            "财经": "💰",
            "社会": "🏛️",
            "国际": "🌍",
            "军事": "⚔️",
            "教育": "📚",
            "健康": "🏥",
            "美食": "🍽️",
            "旅游": "✈️",
            "时尚": "👗",
            "汽车": "🚗",
            "房产": "🏠",
            "游戏": "🎮"
        }
        
        for key, emoji in category_map.items():
            if key in category:
                return emoji
        
        return "📰"
    
    @staticmethod
    def format_text_message(hotsearch_data: HotSearchData) -> str:
        """格式化为文本消息"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = f"🔥 {hotsearch_data.source}热搜榜 🔥\n"
        message += f"📅 更新时间：{current_time}\n\n"
        
        for item in hotsearch_data.items:
            rank_emoji = HotSearchFormatter.get_rank_emoji(item.rank)
            category_emoji = HotSearchFormatter.get_category_emoji(item.category)
            
            # 基本格式：排名 + 标题
            line = f"{rank_emoji} {item.rank}. {item.title}"
            
            # 添加热度值
            if item.hot_value:
                line += f" ({item.hot_value})"
            
            # 添加分类图标
            if item.category:
                line += f" {category_emoji}"
            
            # 如果有URL，提示可以点击查看详情
            if item.url:
                line += " 🔗"
            
            message += line + "\n"
        
        message += f"\n📊 共{len(hotsearch_data.items)}条热搜"
        message += f"\n⏰ 数据更新：{hotsearch_data.update_time}"
        
        return message
    
    @staticmethod
    def format_markdown_message(hotsearch_data: HotSearchData) -> tuple[str, str]:
        """格式化为Markdown消息，返回(title, content)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        title = f"🔥 {hotsearch_data.source}热搜榜"
        
        content = f"## 🔥 {hotsearch_data.source}热搜榜\n\n"
        content += f"> 📅 **更新时间：** {current_time}\n\n"
        content += "---\n\n"
        
        # 直接显示前10条热搜，不分组
        display_items = hotsearch_data.items[:10]  # 只取前10条
        
        for item in display_items:
            rank_emoji = HotSearchFormatter.get_rank_emoji(item.rank)
            
            # 如果有URL，创建可点击的链接
            if item.url:
                content += f"**{rank_emoji} {item.rank}.** [{item.title}]({item.url})"
            else:
                content += f"**{rank_emoji} {item.rank}.** {item.title}"
            
            if item.hot_value:
                content += f" `{item.hot_value}`"
            
            content += "\n\n"
        
        # 统计信息
        content += "---\n\n"
        content += f"📊 **数据源：** {hotsearch_data.source} | **更新时间：** {hotsearch_data.update_time}\n"
        
        return title, content
    
    @staticmethod
    def format_simple_list(hotsearch_data: HotSearchData, limit: int = 10) -> str:
        """格式化为简单列表"""
        items = hotsearch_data.items[:limit]
        
        message = f"📈 {hotsearch_data.source} Top{len(items)}:\n\n"
        
        for item in items:
            if item.url:
                message += f"{item.rank}. [{item.title}]({item.url})\n"
            else:
                message += f"{item.rank}. {item.title}\n"
        
        return message
