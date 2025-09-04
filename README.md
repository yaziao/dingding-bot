# 🌤️ 天气播报机器人

一个基于Python的智能天气播报机器人，使用彩玉天气API获取实时天气数据，并通过钉钉机器人定时推送美化后的天气信息到钉钉群。

## ✨ 功能特性

- 🌡️ **实时天气数据**：集成彩玉天气API，获取准确的天气信息
- 🤖 **钉钉机器人推送**：支持文本和Markdown格式的消息推送
- ⏰ **定时任务调度**：可配置任意间隔的定时播报
- 🎨 **美化消息格式**：丰富的emoji和结构化布局
- 🫁 **空气质量监测**：包含AQI、PM2.5、PM10等空气质量指标
- 💡 **智能提醒**：根据天气状况提供贴心的生活建议
- 📊 **详细天气信息**：温度、湿度、风向风速、能见度、气压等
- 🛡️ **错误处理**：完善的异常处理和日志记录

## 🚀 快速开始

### 1. 环境要求

- Python 3.12+
- uv 包管理器

### 2. 安装依赖

```bash
# 使用uv安装依赖
uv pip install -e .

# 或使用pip
pip install -e .
```

### 3. 配置设置

1. **复制配置模板**：
   ```bash
   cp config.example .env
   ```

2. **编辑配置文件**，填入以下信息：
   ```bash
   # 彩玉天气API配置
   CAIYUN_API_KEY=your_caiyun_api_key_here
   
   # 位置信息 (经度,纬度)
   LONGITUDE=116.4074
   LATITUDE=39.9042
   
   # 钉钉机器人Webhook配置
   DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=your_access_token_here
   DINGTALK_SECRET=your_secret_here  # 可选
   
   # 城市名称
   CITY_NAME=北京
   ```

### 4. 获取API密钥和Webhook

#### 彩玉天气API
1. 访问 [彩玉天气开发平台](https://dashboard.caiyunapp.com/)
2. 注册账号并创建应用
3. 获取API密钥

#### 钉钉机器人
1. 在钉钉群中添加"自定义机器人"
2. 复制Webhook地址
3. 如需安全设置，可启用"加签"功能并获取密钥

### 5. 获取地理坐标
- 访问 [高德地图坐标拾取工具](https://lbs.amap.com/tools/picker)
- 搜索目标城市，获取经纬度坐标

## 🎯 使用方法

### 方法一：使用便捷启动器（推荐）
```bash
python run.py
```
启动器会引导您完成配置并选择运行模式。

### 方法二：直接运行
```bash
# 测试模式（发送一次测试消息）
python main.py --test

# 定时模式（每小时发送）
python main.py

# 自定义间隔（每3小时发送）
python main.py --interval 3
```

## 📁 项目结构

```
dingding/
├── main.py              # 主程序入口
├── run.py               # 便捷启动器
├── pyproject.toml       # 项目配置和依赖
├── config.example       # 配置文件模板
├── README.md           # 使用说明
├── .gitignore          # Git忽略文件
├── logs/               # 日志目录
└── src/                # 源代码目录
    ├── __init__.py     # 包初始化
    ├── config.py       # 配置管理
    ├── weather.py      # 天气API调用
    ├── dingtalk.py     # 钉钉机器人推送
    ├── formatter.py    # 消息格式化
    └── scheduler.py    # 定时任务调度
```

## 🔧 配置说明

### 环境变量配置

| 变量名 | 必填 | 描述 | 示例 |
|--------|------|------|------|
| `CAIYUN_API_KEY` | ✅ | 彩玉天气API密钥 | `your_api_key_here` |
| `LONGITUDE` | ✅ | 目标位置经度 | `116.4074` |
| `LATITUDE` | ✅ | 目标位置纬度 | `39.9042` |
| `DINGTALK_WEBHOOK` | ✅ | 钉钉机器人Webhook地址 | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| `DINGTALK_SECRET` | ❌ | 钉钉机器人密钥（加签） | `your_secret_here` |
| `CITY_NAME` | ❌ | 城市显示名称 | `北京` |

### 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--interval` | 播报间隔（小时） | `1` |
| `--test` | 测试模式，发送一次消息后退出 | `False` |
| `--config` | 指定配置文件路径 | 自动检测 |

## 📱 消息效果预览

### Markdown格式消息
```
## ☀️ 北京天气实况

> 📅 更新时间：2024-01-15 14:00

---

### 🌡️ 基本信息
- **温度：** 15.2°C 😊 凉爽
- **天气：** ☀️ 晴天  
- **湿度：** 💧 45.0%
- **风向风速：** 💨 西北风 3.2m/s
- **能见度：** 👁️ 10.0km
- **气压：** 🏔️ 1013.2hPa

### 🫁 空气质量
- **AQI：** 🟢 35 (优)
- **PM2.5：** 🔹 12.5μg/m³
- **PM10：** 🔸 25.0μg/m³

### 💡 温馨提示
- 🌈 天气不错，适合外出活动！
```

## 🔍 故障排除

### 常见问题

1. **API调用失败**
   - 检查彩玉天气API密钥是否正确
   - 确认API调用次数是否已用完
   - 检查网络连接

2. **钉钉消息发送失败**
   - 验证Webhook地址是否正确
   - 检查机器人是否被移除
   - 确认加签密钥配置

3. **坐标获取天气失败**
   - 确认经纬度格式正确
   - 检查坐标是否在彩玉天气支持范围内

### 日志查看

程序会自动生成日志文件：
- 控制台输出：实时查看运行状态
- 文件日志：`logs/weather_bot.log`
- 日志轮转：每天一个文件，保留30天

## 🔄 部署建议

### 服务器部署
```bash
# 使用screen或tmux保持后台运行
screen -S weather-bot
python main.py --interval 1

# 或使用nohup
nohup python main.py --interval 1 > weather_bot.log 2>&1 &
```

### 使用systemd服务（推荐）
```bash
# 创建服务文件
sudo nano /etc/systemd/system/weather-bot.service

# 启动服务
sudo systemctl enable weather-bot
sudo systemctl start weather-bot
```

### Docker部署
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "main.py"]
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [彩玉天气](https://caiyunapp.com/) - 提供准确的天气数据API
- [钉钉开放平台](https://developers.dingtalk.com/) - 提供机器人推送能力
- 所有开源依赖库的贡献者

---

如有问题或建议，欢迎提交Issue！ 🌟
