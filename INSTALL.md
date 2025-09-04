# 🛠️ 安装指南

## 📋 系统要求

- Python >= 3.12
- Linux/macOS/Windows

## 🚀 快速安装

**注意：可选依赖组是互斥的，请只选择其中一种安装方式**

### 基础安装（无图形功能）
```bash
# 适合服务器环境，只支持ASCII雨图
uv sync
# 或者
pip install -e .
```

### 完整安装（包含图形功能）
```bash
# 支持彩色雨图生成，需要C++17支持
uv sync --extra graphics
# 或者
pip install -e ".[graphics]"
```

### 兼容老版本编译器安装
```bash
# 适合不支持C++17的服务器环境
uv sync --extra graphics-legacy
# 或者
pip install -e ".[graphics-legacy]"
```

## 🔧 服务器环境配置

### 情况1：支持C++17的现代服务器
```bash
# 安装完整功能
uv sync --extra graphics
```

### 情况2：老版本服务器（不支持C++17）
```bash
# 使用兼容版本
uv sync --extra graphics-legacy
```

### 情况3：纯服务器环境（无图形需求）
```bash
# 基础安装，只使用ASCII雨图
uv sync
```

## 📊 功能差异

| 安装方式 | ASCII雨图 | 彩色图表 | 服务器兼容性 |
|---------|-----------|----------|-------------|
| 基础安装 | ✅ | ❌ | 🟢 最佳 |
| 兼容安装 | ✅ | ✅ | 🟡 良好 |
| 完整安装 | ✅ | ✅ | 🔴 需要C++17 |

## 🧪 测试安装

```bash
# 测试基础功能
python -c "from src.hotsearch import HotSearchAPI; print('热搜功能正常')"

# 测试天气功能
python -c "from src.weather import WeatherAPI; print('天气功能正常')"

# 测试雨图功能
python -c "from src.rain_visualizer import RainVisualizer; print('雨图功能正常')"
```

## ⚠️ 常见问题

### contourpy编译错误
```
ERROR: Failed building wheel for contourpy
```

**解决方案：**
1. 使用兼容安装：`pip install -e ".[graphics-legacy]"`
2. 或使用基础安装：`pip install -e .`

### matplotlib导入错误
```
ImportError: No module named 'matplotlib'
```

**解决方案：**
- 系统会自动降级到ASCII雨图，不影响基本功能

### 服务器无GUI环境
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**解决方案：**
- 代码已自动配置 `matplotlib.use('Agg')` 后端
- 无需额外配置

## 📝 部署建议

### 生产服务器
```bash
# 推荐使用基础安装，稳定可靠
uv sync
```

### 开发环境
```bash
# 使用完整功能进行测试
uv sync --extra graphics
```

### Docker环境
```dockerfile
# Dockerfile示例
FROM python:3.12-slim

# 安装uv
RUN pip install uv

# 基础安装（推荐）
RUN uv sync

# 或兼容安装
# RUN uv sync --extra graphics-legacy
```
