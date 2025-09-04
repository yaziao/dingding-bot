#!/bin/bash
# 自动安装脚本

set -e

echo "🚀 DingDing Bot 自动安装脚本"
echo "================================"

# 检查Python版本
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "检测到Python版本: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)"; then
    echo "❌ 需要Python 3.12或更高版本"
    exit 1
fi

# 检查是否有uv
if command -v uv &> /dev/null; then
    INSTALLER="uv"
    echo "✅ 使用uv作为包管理器"
else
    INSTALLER="pip"
    echo "✅ 使用pip作为包管理器"
fi

echo ""
echo "请选择安装类型："
echo "1) 基础安装 (推荐服务器环境)"
echo "2) 兼容安装 (老版本编译器)"
echo "3) 完整安装 (需要C++17支持)"
echo ""

read -p "请输入选择 [1-3]: " choice

case $choice in
    1)
        echo "🔧 执行基础安装..."
        if [ "$INSTALLER" = "uv" ]; then
            uv sync
        else
            pip install -e .
        fi
        echo "✅ 基础安装完成！支持功能: 热搜 + 天气 + ASCII雨图"
        ;;
    2)
        echo "🔧 执行兼容安装..."
        if [ "$INSTALLER" = "uv" ]; then
            uv sync --extra graphics-legacy
        else
            pip install -e ".[graphics-legacy]"
        fi
        echo "✅ 兼容安装完成！支持功能: 热搜 + 天气 + ASCII雨图 + 彩色图表"
        ;;
    3)
        echo "🔧 执行完整安装..."
        if [ "$INSTALLER" = "uv" ]; then
            uv sync --extra graphics
        else
            pip install -e ".[graphics]"
        fi
        echo "✅ 完整安装完成！支持功能: 热搜 + 天气 + ASCII雨图 + 彩色图表"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🧪 运行基础测试..."

# 测试导入
python3 -c "
try:
    from src.hotsearch import HotSearchAPI
    from src.weather import WeatherAPI
    from src.rain_visualizer import RainVisualizer
    print('✅ 所有模块导入成功')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    exit(1)
"

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 复制配置文件: cp config.example config"
echo "2. 编辑配置文件: vim config"
echo "3. 运行程序: python3 main.py"
echo ""
echo "📚 更多帮助请查看: INSTALL.md"
