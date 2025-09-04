#!/usr/bin/env python3
"""
便捷启动脚本
提供简单的交互式配置和启动功能
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """创建.env配置文件"""
    env_file = Path(".env")
    example_file = Path("config.example")
    
    if env_file.exists():
        print("✅ .env文件已存在")
        return True
    
    if not example_file.exists():
        print("❌ config.example文件不存在")
        return False
    
    print("🔧 首次运行，需要配置API密钥和钉钉Webhook...")
    print()
    
    # 读取示例配置
    with open(example_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 交互式配置
    print("请输入以下配置信息：")
    print()
    
    caiyun_key = input("🌤️  彩玉天气API密钥: ").strip()
    if not caiyun_key:
        print("❌ API密钥不能为空")
        return False
    
    dingtalk_webhook = input("🤖 钉钉机器人Webhook地址: ").strip()
    if not dingtalk_webhook:
        print("❌ Webhook地址不能为空")
        return False
    
    dingtalk_secret = input("🔐 钉钉机器人密钥 (可选): ").strip()
    
    city_name = input("🏙️  城市名称 (默认: 北京): ").strip() or "北京"
    
    longitude = input("🌍 经度 (默认: 116.4074): ").strip() or "116.4074"
    latitude = input("🌍 纬度 (默认: 39.9042): ").strip() or "39.9042"
    
    # 替换配置内容
    content = content.replace("your_caiyun_api_key_here", caiyun_key)
    content = content.replace("https://oapi.dingtalk.com/robot/send?access_token=your_access_token_here", dingtalk_webhook)
    if dingtalk_secret:
        content = content.replace("your_secret_here", dingtalk_secret)
    content = content.replace("北京", city_name)
    content = content.replace("116.4074", longitude)
    content = content.replace("39.9042", latitude)
    
    # 写入.env文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("✅ 配置文件创建成功！")
    return True

def main():
    """主函数"""
    print("🌤️ 天气播报机器人启动器")
    print("=" * 40)
    
    # 检查并创建配置文件
    if not create_env_file():
        sys.exit(1)
    
    print()
    print("选择运行模式：")
    print("1. 测试模式 (发送一次测试消息)")
    print("2. 定时模式 (每小时自动发送)")
    print("3. 自定义间隔")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            print("\n🧪 启动测试模式...")
            os.system("python main.py --test")
            break
        elif choice == "2":
            print("\n⏰ 启动定时模式 (每小时)...")
            os.system("python main.py")
            break
        elif choice == "3":
            interval = input("请输入间隔小时数: ").strip()
            try:
                interval = int(interval)
                if interval <= 0:
                    print("❌ 间隔必须大于0")
                    continue
                print(f"\n⏰ 启动定时模式 (每{interval}小时)...")
                os.system(f"python main.py --interval {interval}")
                break
            except ValueError:
                print("❌ 请输入有效数字")
                continue
        elif choice == "4":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
