#!/usr/bin/env python3
"""
Cron表达式帮助工具
"""

import argparse
import sys
from datetime import datetime, timedelta
from croniter import croniter
from loguru import logger

def setup_logging():
    """设置日志配置"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

def validate_cron(cron_expr: str):
    """验证cron表达式"""
    try:
        cron = croniter(cron_expr)
        print(f"✅ Cron表达式有效: {cron_expr}")
        return True
    except Exception as e:
        print(f"❌ Cron表达式无效: {cron_expr}")
        print(f"   错误: {e}")
        return False

def get_next_runs(cron_expr: str, count: int = 5):
    """获取接下来的执行时间"""
    try:
        cron = croniter(cron_expr, datetime.now())
        print(f"📅 接下来 {count} 次执行时间:")
        
        for i in range(count):
            next_time = cron.get_next(datetime)
            print(f"  {i+1}. {next_time.strftime('%Y-%m-%d %H:%M:%S %A')}")
        
        return True
    except Exception as e:
        print(f"❌ 计算执行时间失败: {e}")
        return False

def explain_cron(cron_expr: str):
    """解释cron表达式"""
    parts = cron_expr.split()
    if len(parts) != 5:
        print("❌ Cron表达式应包含5个字段: 分 时 日 月 周")
        return
    
    minute, hour, day, month, day_of_week = parts
    
    print(f"🔍 Cron表达式解析: {cron_expr}")
    print(f"  分钟: {minute}")
    print(f"  小时: {hour}")
    print(f"  日期: {day}")
    print(f"  月份: {month}")
    print(f"  星期: {day_of_week}")
    print()
    
    # 常见模式解释
    explanations = []
    
    if cron_expr == "0 * * * *":
        explanations.append("每小时的整点执行")
    elif cron_expr == "0 */2 * * *":
        explanations.append("每2小时执行一次")
    elif cron_expr == "0 8,12,18 * * *":
        explanations.append("每天8点、12点、18点执行")
    elif cron_expr == "0 9 * * 1-5":
        explanations.append("周一到周五的9点执行")
    elif cron_expr == "30 6 * * *":
        explanations.append("每天早上6点30分执行")
    
    if explanations:
        print("💡 说明:")
        for exp in explanations:
            print(f"  {exp}")

def show_common_examples():
    """显示常见的cron表达式示例"""
    examples = [
        ("0 * * * *", "每小时执行"),
        ("0 */2 * * *", "每2小时执行"),
        ("0 */6 * * *", "每6小时执行"),
        ("0 8,12,18 * * *", "每天8点、12点、18点执行"),
        ("30 6 * * *", "每天早上6:30执行"),
        ("0 9 * * 1-5", "工作日9点执行"),
        ("0 0 * * 0", "每周日午夜执行"),
        ("0 2 1 * *", "每月1日凌晨2点执行"),
        ("*/15 * * * *", "每15分钟执行"),
        ("0 */4 * * *", "每4小时执行"),
    ]
    
    print("📋 常见Cron表达式示例:")
    print()
    for cron, desc in examples:
        print(f"  {cron:<12} - {desc}")
    
    print()
    print("📝 Cron表达式格式: 分 时 日 月 周")
    print("  分: 0-59")
    print("  时: 0-23") 
    print("  日: 1-31")
    print("  月: 1-12")
    print("  周: 0-6 (0=周日)")
    print()
    print("🔧 特殊符号:")
    print("  *    - 匹配任何值")
    print("  */n  - 每n个单位执行")
    print("  a,b  - 在a和b时执行")
    print("  a-b  - 从a到b范围内执行")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Cron表达式帮助工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python cron_helper.py examples                    # 显示常见示例
  python cron_helper.py validate "0 * * * *"        # 验证表达式
  python cron_helper.py next "0 */2 * * *"          # 显示下次执行时间
  python cron_helper.py explain "0 8,12,18 * * *"   # 解释表达式含义
        """
    )
    
    parser.add_argument(
        "action",
        choices=["examples", "validate", "next", "explain"],
        help="要执行的操作"
    )
    
    parser.add_argument(
        "cron_expr",
        nargs="?",
        help="Cron表达式（examples操作不需要）"
    )
    
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=5,
        help="显示的执行时间数量（默认5次）"
    )
    
    args = parser.parse_args()
    
    setup_logging()
    
    try:
        if args.action == "examples":
            show_common_examples()
        elif args.action in ["validate", "next", "explain"]:
            if not args.cron_expr:
                print("❌ 该操作需要提供cron表达式")
                sys.exit(1)
            
            if args.action == "validate":
                validate_cron(args.cron_expr)
            elif args.action == "next":
                if validate_cron(args.cron_expr):
                    print()
                    get_next_runs(args.cron_expr, args.count)
            elif args.action == "explain":
                explain_cron(args.cron_expr)
                print()
                if validate_cron(args.cron_expr):
                    print()
                    get_next_runs(args.cron_expr, 3)
        
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
