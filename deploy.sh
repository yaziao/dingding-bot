#!/bin/bash
# 天气播报机器人部署脚本

set -e

echo "🌤️ 天气播报机器人部署脚本"
echo "=============================="

# 检查Python版本
echo "🔍 检查Python版本..."
python3 --version

# 安装依赖
echo "📦 安装项目依赖..."
if command -v uv &> /dev/null; then
    echo "使用uv安装依赖..."
    uv pip install -e .
else
    echo "使用pip安装依赖..."
    pip3 install -e .
fi

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 检查配置文件
if [ ! -f ".env" ]; then
    if [ -f "config.example" ]; then
        echo "⚠️  未找到.env配置文件，请复制config.example并填入配置信息："
        echo "   cp config.example .env"
        echo "   nano .env"
    else
        echo "❌ 配置文件模板不存在"
        exit 1
    fi
else
    echo "✅ 配置文件存在"
fi

# 测试运行
echo "🧪 运行测试..."
if python3 main.py --test; then
    echo "✅ 测试通过"
else
    echo "❌ 测试失败，请检查配置"
    exit 1
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "使用方法："
echo "  交互式启动：python3 run.py"
echo "  直接运行：  python3 main.py"
echo "  测试模式：  python3 main.py --test"
echo ""
echo "后台运行："
echo "  screen -S weather-bot"
echo "  python3 main.py"
echo ""
echo "系统服务部署："
echo "  sudo cp weather-bot.service /etc/systemd/system/"
echo "  sudo systemctl enable weather-bot"
echo "  sudo systemctl start weather-bot"
