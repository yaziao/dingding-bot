#!/usr/bin/env python3
"""
任务管理命令行工具
"""

import argparse
import sys
from loguru import logger
from src import MultiTaskBot, config

def setup_logging(level="INFO"):
    """设置日志配置"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level
    )

def list_tasks(bot):
    """列出所有任务"""
    print("📋 已注册的任务:")
    tasks = bot.list_tasks()
    if not tasks:
        print("  无任务")
        return
    
    status = bot.get_task_status()
    for task_name in tasks:
        task_status = status.get(task_name, {})
        enabled = "✅" if task_status.get("enabled", False) else "❌"
        last_error = task_status.get("last_error")
        error_info = f" (错误: {last_error})" if last_error else ""
        print(f"  {enabled} {task_name}{error_info}")

def test_task(bot, task_name=None):
    """测试任务"""
    if task_name:
        # 测试特定任务
        print(f"🧪 测试任务: {task_name}")
        # 这里可以添加单个任务测试的逻辑
        success = bot.scheduler.task_manager.execute_task(task_name)
        if success:
            print(f"✅ 任务 {task_name} 测试成功")
        else:
            print(f"❌ 任务 {task_name} 测试失败")
    else:
        # 测试所有任务
        print("🧪 测试所有任务...")
        success = bot.send_test_message()
        if success:
            print("✅ 测试成功")
        else:
            print("❌ 测试失败")

def enable_task(bot, task_name):
    """启用任务"""
    if bot.scheduler.task_manager.enable_task(task_name):
        print(f"✅ 任务 {task_name} 已启用")
    else:
        print(f"❌ 任务 {task_name} 启用失败")

def disable_task(bot, task_name):
    """禁用任务"""
    if bot.scheduler.task_manager.disable_task(task_name):
        print(f"✅ 任务 {task_name} 已禁用")
    else:
        print(f"❌ 任务 {task_name} 禁用失败")

def show_status(bot):
    """显示任务状态"""
    print("📊 任务状态详情:")
    status = bot.get_task_status()
    
    if not status:
        print("  无任务")
        return
    
    for task_name, task_info in status.items():
        print(f"\n🔹 任务: {task_name}")
        print(f"   状态: {'启用' if task_info.get('enabled') else '禁用'}")
        
        last_run = task_info.get('last_run_time')
        if last_run:
            print(f"   上次运行: {last_run}")
        else:
            print(f"   上次运行: 从未运行")
        
        last_error = task_info.get('last_error')
        if last_error:
            print(f"   最后错误: {last_error}")

def add_hotsearch_task(bot, source_type):
    """添加热搜任务"""
    available_sources = ["weibo", "zhihu", "douyin", "toutiao", "bilibili", "baidu"]
    if source_type not in available_sources:
        print(f"❌ 不支持的热搜源: {source_type}")
        print(f"支持的热搜源: {', '.join(available_sources)}")
        return False
    
    if bot.add_hotsearch_task(source_type):
        print(f"✅ 热搜任务 {source_type} 添加成功")
        return True
    else:
        print(f"❌ 热搜任务 {source_type} 添加失败")
        return False

def list_available_sources():
    """列出可用的热搜源"""
    print("📋 可用的热搜数据源:")
    sources = [
        ("weibo", "微博热搜"),
        ("zhihu", "知乎热榜"),
        ("douyin", "抖音热搜"),
        ("toutiao", "今日头条热搜"),
        ("bilibili", "哔哩哔哩热榜"),
        ("baidu", "百度热搜")
    ]
    
    for code, name in sources:
        print(f"  📊 {code} - {name}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="多任务播报机器人管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python task_manager.py list                     # 列出所有任务
  python task_manager.py test                     # 测试所有任务
  python task_manager.py test --task 天气播报      # 测试特定任务
  python task_manager.py enable --task 热搜榜单-weibo   # 启用任务
  python task_manager.py disable --task 热搜榜单-weibo  # 禁用任务
  python task_manager.py status                   # 显示详细状态
  python task_manager.py sources                  # 显示可用热搜源
  python task_manager.py add-hot --source zhihu   # 添加知乎热搜任务
        """
    )
    
    parser.add_argument(
        "action",
        choices=["list", "test", "enable", "disable", "status", "sources", "add-hot"],
        help="要执行的操作"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="任务名称（用于enable/disable/test操作）"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        help="热搜数据源（用于add-hot操作）"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging("DEBUG" if args.verbose else "INFO")
    
    try:
        # 验证配置
        config.validate_config()
        
        # 创建机器人实例
        bot = MultiTaskBot()
        
        # 执行操作
        if args.action == "list":
            list_tasks(bot)
        elif args.action == "test":
            test_task(bot, args.task)
        elif args.action == "enable":
            if not args.task:
                print("❌ 启用任务需要指定 --task 参数")
                sys.exit(1)
            enable_task(bot, args.task)
        elif args.action == "disable":
            if not args.task:
                print("❌ 禁用任务需要指定 --task 参数")
                sys.exit(1)
            disable_task(bot, args.task)
        elif args.action == "status":
            show_status(bot)
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请检查config.example文件，复制为.env并填入正确的配置信息")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
