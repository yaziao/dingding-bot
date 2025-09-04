"""雨图可视化模块"""
import io
import base64
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from .weather import WeatherData, HourlyWeatherData
from loguru import logger

# 可选的matplotlib导入，处理服务器环境兼容性
try:
    import matplotlib
    # 设置后端，避免在无GUI环境中出错
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.font_manager import FontProperties
    from matplotlib.dates import DateFormatter, HourLocator
    import numpy as np
    HAS_MATPLOTLIB = True
    logger.info("matplotlib导入成功")
except ImportError as e:
    HAS_MATPLOTLIB = False
    logger.warning(f"matplotlib导入失败，将只使用ASCII雨图: {e}")
except Exception as e:
    HAS_MATPLOTLIB = False
    logger.warning(f"matplotlib初始化失败，将只使用ASCII雨图: {e}")

class RainVisualizer:
    """雨图可视化器"""
    
    def __init__(self):
        # 存储matplotlib支持状态
        self.HAS_MATPLOTLIB = HAS_MATPLOTLIB
        # 只在有matplotlib时设置字体
        if HAS_MATPLOTLIB:
            try:
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
            except Exception as e:
                logger.warning(f"matplotlib字体设置失败: {e}")
        
    def generate_rain_chart(self, weather_data: WeatherData, city_name: str, 
                          extended_hours: int = 12) -> Optional[str]:
        """
        生成雨图
        
        Args:
            weather_data: 天气数据
            city_name: 城市名称
            extended_hours: 扩展预报小时数
            
        Returns:
            base64编码的图片字符串，如果生成失败返回None
        """
        # 如果没有matplotlib，直接返回None，让系统使用ASCII雨图
        if not HAS_MATPLOTLIB:
            logger.info("matplotlib不可用，跳过图形雨图生成")
            return None
            
        try:
            # 准备数据
            times, precipitations, weather_descs = self._prepare_rain_data(
                weather_data, extended_hours
            )
            
            if not times or len(times) < 2:
                logger.warning("降水数据不足，无法生成雨图")
                return None
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 设置背景色
            fig.patch.set_facecolor('#f0f8ff')
            ax.set_facecolor('#ffffff')
            
            # 绘制降水柱状图
            bars = ax.bar(times, precipitations, width=0.8/24, 
                         color=self._get_precipitation_colors(precipitations),
                         alpha=0.7, edgecolor='white', linewidth=0.5)
            
            # 设置标题和标签
            current_time = datetime.now().strftime("%m月%d日 %H:%M")
            ax.set_title(f'🌧️ {city_name}降水预报图 ({current_time})', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('时间', fontsize=12)
            ax.set_ylabel('降水量 (mm/h)', fontsize=12)
            
            # 设置时间轴格式
            ax.xaxis.set_major_locator(HourLocator(interval=2))
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            
            # 旋转时间标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 设置Y轴范围
            max_precip = max(precipitations) if precipitations else 1
            ax.set_ylim(0, max(max_precip * 1.2, 0.5))
            
            # 添加网格
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # 添加降水等级标签
            self._add_precipitation_labels(ax, bars, precipitations)
            
            # 添加天气状态标记
            self._add_weather_icons(ax, times, weather_descs, precipitations)
            
            # 添加图例
            self._add_legend(ax)
            
            # 添加统计信息
            self._add_statistics(ax, precipitations, times)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存为base64字符串
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#f0f8ff', edgecolor='none')
            buffer.seek(0)
            
            # 转换为base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 清理资源
            plt.close(fig)
            buffer.close()
            
            logger.info(f"成功生成{city_name}雨图")
            return image_base64
            
        except Exception as e:
            logger.error(f"生成雨图失败: {e}")
            return None
    
    def _prepare_rain_data(self, weather_data: WeatherData, 
                          extended_hours: int) -> Tuple[List[datetime], List[float], List[str]]:
        """准备雨图数据"""
        times = []
        precipitations = []
        weather_descs = []
        
        current_time = datetime.now()
        
        # 添加当前时间的数据（使用实时降水数据）
        times.append(current_time)
        current_precip = weather_data.precipitation  # 使用真实的实时降水量
        precipitations.append(current_precip)
        weather_descs.append(weather_data.weather_desc)
        
        # 添加小时级预报数据
        for hour_data in weather_data.hourly_forecast:
            times.append(hour_data.datetime)
            precipitations.append(hour_data.precipitation)
            weather_descs.append(hour_data.weather_desc)
        
        # 限制使用真实预报数据，如果不足就截取现有数据
        # 优先使用真实的API数据，而不是模拟数据
        max_real_hours = min(extended_hours, len(times))
        times = times[:max_real_hours]
        precipitations = precipitations[:max_real_hours]
        weather_descs = weather_descs[:max_real_hours]
        
        return times, precipitations, weather_descs
    
    def _simulate_precipitation(self, weather_desc: str, base_precip: float) -> float:
        """模拟降水量"""
        import random
        
        if "雨" in weather_desc:
            if "小雨" in weather_desc:
                return random.uniform(0.1, 2.0)
            elif "中雨" in weather_desc:
                return random.uniform(2.0, 8.0)
            elif "大雨" in weather_desc:
                return random.uniform(8.0, 20.0)
            elif "暴雨" in weather_desc:
                return random.uniform(20.0, 50.0)
            else:
                return random.uniform(0.1, 5.0)
        elif "雪" in weather_desc:
            return random.uniform(0.0, 2.0)  # 雪的等价降水量
        else:
            return random.uniform(0.0, 0.1)  # 无降水或微量
    
    def _simulate_weather_desc(self, current_desc: str) -> str:
        """模拟天气描述"""
        import random
        
        # 基于当前天气状态的转换概率
        if "雨" in current_desc:
            options = [current_desc, "多云", "阴天"]
            weights = [0.6, 0.2, 0.2]
        elif "云" in current_desc:
            options = [current_desc, "晴天", "小雨"]
            weights = [0.7, 0.2, 0.1]
        else:
            options = [current_desc, "多云"]
            weights = [0.8, 0.2]
        
        return random.choices(options, weights=weights)[0]
    
    def _get_precipitation_colors(self, precipitations: List[float]) -> List[str]:
        """根据降水量获取颜色"""
        colors = []
        for precip in precipitations:
            if precip == 0:
                colors.append('#e6f3ff')  # 无降水 - 浅蓝
            elif precip < 0.5:
                colors.append('#b3d9ff')  # 微雨 - 淡蓝
            elif precip < 2.0:
                colors.append('#66b3ff')  # 小雨 - 蓝色
            elif precip < 8.0:
                colors.append('#0080ff')  # 中雨 - 中蓝
            elif precip < 20.0:
                colors.append('#0066cc')  # 大雨 - 深蓝
            else:
                colors.append('#004080')  # 暴雨 - 深深蓝
        return colors
    
    def _add_precipitation_labels(self, ax, bars, precipitations: List[float]):
        """添加降水量标签"""
        for bar, precip in zip(bars, precipitations):
            if precip > 0.1:  # 只为有意义的降水量添加标签
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{precip:.1f}', ha='center', va='bottom',
                       fontsize=8, fontweight='bold')
    
    def _add_weather_icons(self, ax, times: List[datetime], 
                          weather_descs: List[str], precipitations: List[float]):
        """添加天气状态图标"""
        y_pos = ax.get_ylim()[1] * 0.9
        
        for i, (time, desc) in enumerate(zip(times[::2], weather_descs[::2])):  # 每隔一个小时显示
            if i >= len(times):
                break
                
            icon = self._get_weather_icon(desc)
            ax.text(time, y_pos, icon, ha='center', va='center',
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3",
                   facecolor='white', alpha=0.8))
    
    def _get_weather_icon(self, weather_desc: str) -> str:
        """获取天气图标"""
        if "晴" in weather_desc:
            return "☀️"
        elif "云" in weather_desc:
            return "☁️"
        elif "阴" in weather_desc:
            return "☁️"
        elif "雨" in weather_desc:
            return "🌧️"
        elif "雪" in weather_desc:
            return "🌨️"
        elif "雾" in weather_desc:
            return "🌫️"
        else:
            return "🌈"
    
    def _add_legend(self, ax):
        """添加图例"""
        legend_elements = [
            patches.Patch(color='#e6f3ff', label='无降水 (0mm)'),
            patches.Patch(color='#66b3ff', label='小雨 (0.1-2mm)'),
            patches.Patch(color='#0080ff', label='中雨 (2-8mm)'),
            patches.Patch(color='#0066cc', label='大雨 (8-20mm)'),
            patches.Patch(color='#004080', label='暴雨 (>20mm)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', 
                 bbox_to_anchor=(1, 1), fontsize=10)
    
    def _add_statistics(self, ax, precipitations: List[float], times: List[datetime]):
        """添加统计信息"""
        if not precipitations:
            return
            
        total_precip = sum(precipitations)
        max_precip = max(precipitations)
        avg_precip = total_precip / len(precipitations)
        
        # 计算预报时长
        if len(times) >= 2:
            duration = (times[-1] - times[0]).total_seconds() / 3600
        else:
            duration = 1
        
        stats_text = f"预报时长: {duration:.0f}小时\n"
        stats_text += f"总降水量: {total_precip:.1f}mm\n"
        stats_text += f"最大降水: {max_precip:.1f}mm/h\n"
        stats_text += f"平均降水: {avg_precip:.1f}mm/h"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5",
               facecolor='white', alpha=0.9), fontsize=10)
    
    def generate_simple_rain_chart(self, weather_data: WeatherData, 
                                  city_name: str) -> Optional[str]:
        """生成简化版雨图（只用ASCII字符）"""
        try:
            # 使用真实的彩云天气数据
            times, precipitations, weather_descs = self._prepare_rain_data(weather_data, 24)
            
            if not times or len(times) < 2:
                return None
            
            # 格式化时间为字符串
            time_strings = [t.strftime("%H:%M") for t in times]
            
            # 生成ASCII雨图
            chart = self._create_ascii_rain_chart(precipitations, time_strings, city_name)
            return chart
            
        except Exception as e:
            logger.error(f"生成简化雨图失败: {e}")
            return None
    
    def _create_ascii_rain_chart(self, precipitations: List[float], 
                                times: List[str], city_name: str) -> str:
        """创建ASCII雨图（参考彩云天气风格）"""
        hours_count = len(precipitations)
        chart = f"🌧️ {city_name} {hours_count}小时降水预报\n"
        chart += "=" * min(40, 20 + hours_count) + "\n"
        
        # 找到最大降水量用于缩放
        max_precip = max(precipitations) if any(p > 0 for p in precipitations) else 1
        
        # 彩云天气风格的降水强度分级
        def get_rain_char(precip: float) -> str:
            if precip <= 0:
                return "·"
            elif precip <= 0.25:
                return "░"  # 微雨
            elif precip <= 1.0:
                return "▒"  # 小雨
            elif precip <= 4.0:
                return "▓"  # 中雨
            elif precip <= 10.0:
                return "█"  # 大雨
            else:
                return "█"  # 暴雨
        
        # 生成降水强度图表（更紧凑的垂直显示）
        scale_levels = [10, 5, 2, 1, 0.5, 0.1]
        for level in scale_levels:
            if max_precip >= level or level == 0.1:
                line = f"{level:4.1f}|"
                for precip in precipitations:
                    if precip >= level:
                        line += get_rain_char(precip)
                    else:
                        line += " "
                chart += line + "\n"
        
        # 添加基线
        chart += "    +" + "─" * len(precipitations) + "\n"
        
        # 添加时间轴（显示小时）
        chart += "     "
        for i, time in enumerate(times):
            if i % 3 == 0 or i == len(times) - 1:  # 每3小时显示一次，加上最后一个
                hour = time.split(":")[0] if ":" in time else time
                chart += f"{hour:>2}" + " " * (2 if i % 3 == 0 else 0)
            else:
                chart += "   "
        
        chart += "\n"
        
        # 添加彩云天气风格的图例
        chart += "\n图例: █暴雨 ▓大雨 ▒中雨 ░小雨 ·无雨\n"
        
        # 添加统计信息
        total = sum(precipitations)
        max_val = max(precipitations) if precipitations else 0
        has_rain = any(p > 0 for p in precipitations)
        
        chart += f"📊 {hours_count}h总量: {total:.1f}mm"
        if has_rain:
            chart += f" | 峰值: {max_val:.1f}mm/h"
            # 参考彩云天气的预警等级
            if max_val >= 20:
                chart += " 🔴暴雨"
            elif max_val >= 10:
                chart += " 🟠大雨"
            elif max_val >= 4:
                chart += " 🟡中雨"
            elif max_val >= 1:
                chart += " 🔵小雨"
            else:
                chart += " 🟢微雨"
        else:
            chart += " | 无降水 ☀️"
        
        # 添加实时数据来源标注
        chart += "\n💫 数据来源: 彩云天气API"
        
        return chart
