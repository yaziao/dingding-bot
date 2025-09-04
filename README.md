# 🤖 多任务播报机器人

一个基于Python的智能多任务播报机器人，支持天气播报、热搜榜单等多种信息推送，通过钉钉机器人定时推送美化后的信息到钉钉群。采用模块化架构，方便扩展新的推送任务。

## ✨ 功能特性

- 🌡️ **实时天气数据**：集成彩玉天气API，获取准确的天气信息
- 🔮 **小时级预报**：支持未来2小时的详细天气预报
- 🔥 **热搜榜单**：支持微博热搜、知乎热榜等多种热搜数据源
- 🤖 **钉钉机器人推送**：支持文本和Markdown格式的消息推送
- ⏰ **定时任务调度**：可配置任意间隔的定时播报，支持整点执行
- 🎨 **美化消息格式**：丰富的emoji和结构化布局
- 🫁 **空气质量监测**：包含AQI、PM2.5、PM10等空气质量指标
- 💡 **智能提醒**：根据天气状况提供贴心的生活建议
- 📊 **详细天气信息**：温度、湿度、风向风速、能见度、气压等
- 🌧️ **降水预警**：智能识别未来降雨趋势并提前提醒
- 🔧 **模块化架构**：基于任务的可扩展架构，方便添加新功能
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

# 显示执行计划
python main.py --show-schedule

# 正常运行（根据配置文件中的cron表达式执行）
python main.py
```

## 📁 项目结构

```
dingding/
├── main.py              # 主程序入口
├── run.py               # 便捷启动器
├── task_manager.py      # 任务管理工具
├── cron_helper.py       # Cron表达式辅助工具
├── pyproject.toml       # 项目配置和依赖
├── config.example       # 配置文件模板
├── README.md           # 使用说明
├── .gitignore          # Git忽略文件
├── logs/               # 日志目录
└── src/                # 源代码目录
    ├── __init__.py     # 包初始化
    ├── config.py       # 配置管理
    ├── weather.py      # 天气API调用
    ├── hotsearch.py    # 热搜API调用
    ├── dingtalk.py     # 钉钉机器人推送
    ├── formatter.py    # 天气消息格式化
    ├── hotsearch_formatter.py  # 热搜消息格式化
    ├── scheduler.py    # 定时任务调度
    ├── base/           # 基础架构
    │   ├── __init__.py
    │   ├── task_base.py    # 任务基类
    │   └── task_manager.py # 任务管理器
    └── tasks/          # 具体任务实现
        ├── __init__.py
        ├── weather_task.py     # 天气播报任务
        └── hotsearch_task.py   # 热搜榜单任务
```

## 🔧 配置说明

### 基础配置

| 变量名 | 必填 | 描述 | 示例 |
|--------|------|------|------|
| `CAIYUN_API_KEY` | ✅ | 彩玉天气API密钥 | `your_api_key_here` |
| `LONGITUDE` | ✅ | 目标位置经度 | `116.4074` |
| `LATITUDE` | ✅ | 目标位置纬度 | `39.9042` |
| `DINGTALK_WEBHOOK` | ✅ | 钉钉机器人Webhook地址 | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| `DINGTALK_SECRET` | ❌ | 钉钉机器人密钥（加签） | `your_secret_here` |
| `CITY_NAME` | ❌ | 城市显示名称 | `北京` |

### ⏰ Cron定时任务配置

项目支持使用cron表达式灵活配置每个任务的执行时间：

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `WEATHER_TASK_CRON` | 天气播报任务执行时间 | `0 * * * *` | 每小时执行 |
| `WEATHER_TASK_ENABLED` | 是否启用天气任务 | `true` | `true/false` |
| `HOTSEARCH_TASK_CRON` | 热搜榜单任务执行时间 | `0 */2 * * *` | 每2小时执行 |
| `HOTSEARCH_TASK_ENABLED` | 是否启用热搜任务 | `true` | `true/false` |
| `HOTSEARCH_TASK_SOURCE` | 热搜数据源 | `weibo` | `weibo/zhihu/douyin等` |

#### 添加更多热搜源

```bash
# 知乎热榜 - 每天8点、12点、18点执行
HOTSEARCH_ZHIHU_CRON=0 8,12,18 * * *
HOTSEARCH_ZHIHU_ENABLED=true

# 抖音热搜 - 每4小时执行
HOTSEARCH_DOUYIN_CRON=0 */4 * * *
HOTSEARCH_DOUYIN_ENABLED=true
```

### 命令行参数

| 参数 | 描述 |
|------|------|
| `--test` | 测试模式，发送一次消息后退出 |
| `--show-schedule` | 显示任务执行计划并退出 |
| `--config` | 指定配置文件路径 |

### 🕐 Cron表达式说明

Cron表达式格式：`分 时 日 月 周`

#### 常用示例

| Cron表达式 | 说明 |
|------------|------|
| `0 * * * *` | 每小时执行 |
| `0 */2 * * *` | 每2小时执行 |
| `0 8,12,18 * * *` | 每天8点、12点、18点执行 |
| `30 6 * * *` | 每天早上6:30执行 |
| `0 9 * * 1-5` | 工作日9点执行 |
| `*/15 * * * *` | 每15分钟执行 |

#### Cron辅助工具

```bash
# 显示常见示例
python cron_helper.py examples

# 验证cron表达式
python cron_helper.py validate "0 */2 * * *"

# 查看下次执行时间
python cron_helper.py next "0 8,12,18 * * *"

# 解释cron表达式
python cron_helper.py explain "0 9 * * 1-5"
```

## 🔧 任务管理

项目支持多种任务的独立管理，可以通过任务管理工具进行控制：

```bash
# 查看所有任务
python task_manager.py list

# 测试所有任务
python task_manager.py test

# 测试特定任务
python task_manager.py test --task "天气播报"

# 启用/禁用任务
python task_manager.py enable --task "热搜榜单-weibo"
python task_manager.py disable --task "热搜榜单-weibo"

# 查看详细状态
python task_manager.py status
```

### 默认任务

- **天气播报**：获取实时天气和未来2小时预报
- **热搜榜单-weibo**：获取微博热搜榜单

### 添加自定义任务

创建新任务只需要继承 `TaskBase` 类：

```python
from src.base import TaskBase

class CustomTask(TaskBase):
    def __init__(self, dingtalk_bot):
        super().__init__("自定义任务", dingtalk_bot)
    
    def fetch_data(self):
        # 实现数据获取逻辑
        return {"data": "your_data"}
    
    def format_message(self, data):
        # 实现消息格式化逻辑
        return "标题", "内容"
```

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

### 🔮 未来2小时预报

**📅 1小时后 (15:00)**
- **温度：** 16.1°C
- **天气：** ☀️ 晴天
- **湿度：** 💧 42.0%
- **风向风速：** 💨 西北风 3.1m/s

**📅 2小时后 (16:00)**
- **温度：** 15.8°C
- **天气：** ⛅ 多云 (微雨)
- **湿度：** 💧 45.0%
- **风向风速：** 💨 西风 2.8m/s

### 💡 温馨提示
- 🌈 天气不错，适合外出活动！
- ☂️ 未来2小时可能有降雨，记得带伞！
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
