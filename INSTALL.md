# 🛠️ 安装指南

## 📋 系统要求

- Python >= 3.12
- Linux/macOS/Windows

## 🚀 快速安装

### 推荐安装（基础功能）
```bash
# 稳定可靠，支持所有核心功能
uv sync
# 或者
pip install -e .
```

**功能包括：**
- ✅ 热搜功能
- ✅ 天气功能  
- ✅ ASCII文字雨图
- ✅ 完全兼容任何服务器环境

### 高级安装（图形功能）
```bash
# 如果你确实需要彩色图表且环境支持
pip install matplotlib numpy
```

**注意：** 由于matplotlib依赖复杂，建议只在开发环境使用。生产服务器推荐使用基础安装。

## 🔧 服务器环境配置

### 🟢 推荐方案（任何服务器）
```bash
# 基础安装 - 稳定可靠
uv sync
```

### 🟡 可选方案（开发环境）
```bash
# 如果需要图形功能
uv sync && pip install matplotlib numpy
```

### 🔴 避免的方案
- 复杂的图形依赖配置
- C++编译环境依赖
- 不稳定的matplotlib版本

## 📊 功能对比

| 功能 | 基础安装 | 图形安装 | 说明 |
|------|----------|----------|------|
| 热搜推送 | ✅ | ✅ | 支持多平台热搜 |
| 天气预报 | ✅ | ✅ | 实时天气信息 |
| ASCII雨图 | ✅ | ✅ | 文字版降水预报 |
| 彩色图表 | ❌ | ✅ | 图形化数据展示 |
| 服务器兼容 | 🟢 完美 | 🟡 有限 | 编译依赖复杂度 |
| 安装难度 | 🟢 简单 | 🔴 复杂 | 依赖管理复杂度 |

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
