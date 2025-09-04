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
echo "1) 基础安装 (推荐 - 稳定可靠)"
echo "2) 图形安装 (可选 - 包含matplotlib)"
echo ""

read -p "请输入选择 [1-2]: " choice

case $choice in
    1)
        echo "🔧 执行基础安装..."
        if [ "$INSTALLER" = "uv" ]; then
            uv sync
        else
            pip install -e .
        fi
        echo "✅ 基础安装完成！"
        echo "   支持功能: 热搜 + 天气 + ASCII雨图"
        echo "   兼容性: 完美支持任何服务器环境"
        ;;
    2)
        echo "🔧 执行图形安装..."
        if [ "$INSTALLER" = "uv" ]; then
            uv sync
            pip install matplotlib numpy
        else
            pip install -e .
            pip install matplotlib numpy
        fi
        echo "✅ 图形安装完成！"
        echo "   支持功能: 热搜 + 天气 + ASCII雨图 + 彩色图表"
        echo "   注意: 如果matplotlib安装失败，系统将自动降级为ASCII模式"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🧪 运行基础测试..."

# 测试导入（使用uv run确保在正确环境中）
if [ "$INSTALLER" = "uv" ]; then
    TEST_CMD="uv run python3"
else
    TEST_CMD="python3"
fi

$TEST_CMD -c "
try:
    from src.hotsearch import HotSearchAPI
    from src.weather import WeatherAPI
    from src.rain_visualizer import RainVisualizer
    from src.formatter import WeatherFormatter
    
    # 检测功能支持
    rv = RainVisualizer()
    if rv.HAS_MATPLOTLIB:
        print('✅ 所有模块导入成功 (支持图形功能)')
    else:
        print('✅ 所有模块导入成功 (ASCII模式)')
        
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    exit(1)
except Exception as e:
    print(f'❌ 系统测试失败: {e}')
    exit(1)
"

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 复制配置文件: cp config.example config"
echo "2. 编辑配置文件: vim config"
if [ "$INSTALLER" = "uv" ]; then
    echo "3. 运行程序: uv run python3 main.py"
else
    echo "3. 运行程序: python3 main.py"
fi
echo ""
echo "📚 更多帮助请查看: INSTALL.md"
