#!/usr/bin/env python3
"""
天气播报机器人主程序

使用彩玉天气API获取天气数据，并通过钉钉机器人推送美化后的天气信息。
支持定时任务，每小时自动推送天气播报。
"""

import sys
import argparse
from loguru import logger
from src import WeatherBot, config

def setup_logging():
    """设置日志配置"""
    logger.remove()  # 移除默认handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/weather_bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="天气播报机器人 - 定时获取天气信息并推送到钉钉群"
    )
    parser.add_argument(
        "--show-schedule",
        action="store_true",
        help="显示任务执行计划"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="发送测试消息后退出"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="指定配置文件路径"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    try:
        # 创建天气机器人实例
        bot = WeatherBot()
        
        if args.test:
            # 测试模式
            logger.info("=== 测试模式 ===")
            success = bot.send_test_message()
            if success:
                logger.info("✅ 测试消息发送成功")
                sys.exit(0)
            else:
                logger.error("❌ 测试消息发送失败")
                sys.exit(1)
        elif args.show_schedule:
            # 显示执行计划
            logger.info("=== 任务执行计划 ===")
            bot.scheduler.show_next_run_times()
            sys.exit(0)
        else:
            # 正常运行模式
            logger.info("启动多任务播报机器人（基于Cron调度）")
            bot.run()
            
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在退出...")
        sys.exit(0)
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        logger.error("请检查config.example文件，复制为.env并填入正确的配置信息")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
