"""
统计数据可视化模块

提供协议统计数据的图表可视化功能，支持多种图表类型和自定义样式。
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import tkinter as tk
from dataclasses import dataclass

from .protocol_statistics import ProtocolDistribution, TimeSeriesData


@dataclass
class ChartConfig:
    """图表配置类"""
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 100
    style: str = "default"
    color_scheme: str = "tab10"
    show_grid: bool = True
    show_legend: bool = True
    font_size: int = 10


@dataclass
class ChartData:
    """图表数据类"""
    figure: Figure
    canvas: Optional[FigureCanvasTkAgg] = None
    chart_type: str = ""
    data_summary: Dict[str, Any] = None


class StatisticsVisualizer:
    """统计数据可视化器
    
    提供协议统计数据的多种图表可视化功能，包括：
    - 协议分布饼图
    - 协议分布柱状图
    - 时间序列折线图
    - 协议对比图表
    - 流量趋势图
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """初始化可视化器
        
        Args:
            config: 图表配置，如果为None则使用默认配置
        """
        self.config = config or ChartConfig()
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """设置matplotlib样式和中文字体"""
        plt.style.use(self.config.style)
        plt.rcParams['font.size'] = self.config.font_size
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置中文字体
        try:
            import matplotlib.font_manager as fm
            
            # 检查系统可用字体
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            # 优先级排序的中文字体列表
            chinese_fonts = [
                'Microsoft YaHei',
                'SimHei', 
                'SimSun',
                'Microsoft YaHei UI',
                'PingFang SC',
                'Hiragino Sans GB',
                'Source Han Sans CN',
                'Noto Sans CJK SC',
                'WenQuanYi Micro Hei'
            ]
            
            # 查找可用的中文字体
            selected_font = None
            for font_name in chinese_fonts:
                if font_name in available_fonts:
                    selected_font = font_name
                    break
            
            if selected_font:
                plt.rcParams['font.sans-serif'] = [selected_font, 'DejaVu Sans']
                plt.rcParams['font.family'] = 'sans-serif'
            else:
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
                
        except Exception:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    
    def create_protocol_pie_chart(self, 
                                 distribution: ProtocolDistribution,
                                 config: Optional[ChartConfig] = None) -> ChartData:
        """创建协议分布饼图
        
        Args:
            distribution: 协议分布数据
            config: 图表配置，如果为None则使用默认配置
            
        Returns:
            ChartData: 包含图表对象的数据
        """
        chart_config = config or self.config
        
        fig, ax = plt.subplots(figsize=chart_config.figsize, dpi=chart_config.dpi)
        
        if not distribution.protocol_counts:
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(chart_config.title or '协议分布 - 数据包数量')
            return ChartData(figure=fig, chart_type="pie", 
                           data_summary={"total_packets": 0, "protocols": 0})
        
        # 准备数据
        protocols = list(distribution.protocol_counts.keys())
        counts = list(distribution.protocol_counts.values())
        
        # 计算百分比
        total = sum(counts)
        percentages = [count/total*100 for count in counts]
        
        # 创建饼图
        colors = plt.cm.get_cmap(chart_config.color_scheme)(np.linspace(0, 1, len(protocols)))
        wedges, texts, autotexts = ax.pie(counts, labels=protocols, autopct='%1.1f%%',
                                         colors=colors, startangle=90)
        
        # 设置样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(chart_config.title or f'协议分布 - 数据包数量 (总计: {total:,})')
        
        if chart_config.show_legend:
            ax.legend(wedges, [f'{p}: {c:,}' for p, c in zip(protocols, counts)],
                     title="协议统计", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        return ChartData(
            figure=fig,
            chart_type="pie",
            data_summary={
                "total_packets": total,
                "protocols": len(protocols),
                "top_protocol": protocols[counts.index(max(counts))] if counts else None,
                "distribution": dict(zip(protocols, percentages))
            }
        )
    
    def create_protocol_bar_chart(self, 
                                 distribution: ProtocolDistribution,
                                 chart_type: str = "packets",
                                 config: Optional[ChartConfig] = None) -> ChartData:
        """创建协议分布柱状图
        
        Args:
            distribution: 协议分布数据
            chart_type: 图表类型 ("packets" 或 "bytes")
            config: 图表配置
            
        Returns:
            ChartData: 包含图表对象的数据
        """
        chart_config = config or self.config
        
        fig, ax = plt.subplots(figsize=chart_config.figsize, dpi=chart_config.dpi)
        
        # 选择数据源
        if chart_type == "bytes":
            data_dict = distribution.protocol_bytes
            ylabel = "字节数"
            title_suffix = "字节数量"
        else:
            data_dict = distribution.protocol_counts
            ylabel = "数据包数"
            title_suffix = "数据包数量"
        
        if not data_dict:
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(chart_config.title or f'协议分布 - {title_suffix}')
            return ChartData(figure=fig, chart_type="bar", 
                           data_summary={"total": 0, "protocols": 0})
        
        # 准备数据并排序
        protocols = list(data_dict.keys())
        values = list(data_dict.values())
        
        # 按值排序
        sorted_data = sorted(zip(protocols, values), key=lambda x: x[1], reverse=True)
        protocols, values = zip(*sorted_data)
        
        # 创建柱状图
        colors = plt.cm.get_cmap(chart_config.color_scheme)(np.linspace(0, 1, len(protocols)))
        bars = ax.bar(protocols, values, color=colors)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:,}', ha='center', va='bottom')
        
        # 设置样式
        ax.set_xlabel(chart_config.xlabel or "协议类型")
        ax.set_ylabel(chart_config.ylabel or ylabel)
        ax.set_title(chart_config.title or f'协议分布 - {title_suffix}')
        
        if chart_config.show_grid:
            ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签以避免重叠
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        total = sum(values)
        return ChartData(
            figure=fig,
            chart_type="bar",
            data_summary={
                "total": total,
                "protocols": len(protocols),
                "top_protocol": protocols[0] if protocols else None,
                "chart_type": chart_type
            }
        )
    
    def create_time_series_chart(self, 
                                time_series_data: List[TimeSeriesData],
                                config: Optional[ChartConfig] = None) -> ChartData:
        """创建时间序列折线图
        
        Args:
            time_series_data: 时间序列数据列表
            config: 图表配置
            
        Returns:
            ChartData: 包含图表对象的数据
        """
        chart_config = config or self.config
        
        fig, ax = plt.subplots(figsize=chart_config.figsize, dpi=chart_config.dpi)
        
        if not time_series_data:
            ax.text(0.5, 0.5, '暂无时间序列数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(chart_config.title or '协议流量时间序列')
            return ChartData(figure=fig, chart_type="timeseries", 
                           data_summary={"protocols": 0, "time_points": 0})
        
        # 绘制每个协议的时间序列
        colors = plt.cm.get_cmap(chart_config.color_scheme)(
            np.linspace(0, 1, len(time_series_data)))
        
        protocol_stats = {}
        
        for i, ts_data in enumerate(time_series_data):
            if not ts_data.timestamps or not ts_data.values:
                continue
                
            # 转换时间戳为datetime对象
            times = [datetime.fromtimestamp(ts) for ts in ts_data.timestamps]
            
            # 绘制折线
            ax.plot(times, ts_data.values, 
                   label=f'{ts_data.protocol} ({ts_data.interval}s间隔)',
                   color=colors[i], marker='o', linewidth=2, markersize=4)
            
            # 统计信息
            protocol_stats[ts_data.protocol] = {
                "max_value": max(ts_data.values),
                "avg_value": sum(ts_data.values) / len(ts_data.values),
                "time_points": len(ts_data.values)
            }
        
        # 设置样式
        ax.set_xlabel(chart_config.xlabel or "时间")
        ax.set_ylabel(chart_config.ylabel or "数据包数/秒")
        ax.set_title(chart_config.title or "协议流量时间序列")
        
        if chart_config.show_grid:
            ax.grid(True, alpha=0.3)
        
        if chart_config.show_legend and time_series_data:
            ax.legend()
        
        # 格式化时间轴
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return ChartData(
            figure=fig,
            chart_type="timeseries",
            data_summary={
                "protocols": len(time_series_data),
                "time_points": sum(len(ts.timestamps) for ts in time_series_data),
                "protocol_stats": protocol_stats
            }
        )
    
    def create_comparison_chart(self, 
                               protocol_data: Dict[str, Dict[str, int]],
                               config: Optional[ChartConfig] = None) -> ChartData:
        """创建协议对比图表
        
        Args:
            protocol_data: 协议对比数据 {protocol: {metric: value}}
            config: 图表配置
            
        Returns:
            ChartData: 包含图表对象的数据
        """
        chart_config = config or self.config
        
        fig, ax = plt.subplots(figsize=chart_config.figsize, dpi=chart_config.dpi)
        
        if not protocol_data:
            ax.text(0.5, 0.5, '暂无对比数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(chart_config.title or '协议对比')
            return ChartData(figure=fig, chart_type="comparison", 
                           data_summary={"protocols": 0})
        
        # 准备数据
        protocols = list(protocol_data.keys())
        metrics = set()
        for data in protocol_data.values():
            metrics.update(data.keys())
        metrics = list(metrics)
        
        # 创建分组柱状图
        x = np.arange(len(protocols))
        width = 0.8 / len(metrics) if metrics else 0.8
        
        colors = plt.cm.get_cmap(chart_config.color_scheme)(np.linspace(0, 1, len(metrics)))
        
        for i, metric in enumerate(metrics):
            values = [protocol_data[protocol].get(metric, 0) for protocol in protocols]
            offset = (i - len(metrics)/2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=metric, color=colors[i])
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                if value > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:,}', ha='center', va='bottom', fontsize=8)
        
        # 设置样式
        ax.set_xlabel(chart_config.xlabel or "协议")
        ax.set_ylabel(chart_config.ylabel or "数量")
        ax.set_title(chart_config.title or "协议对比")
        ax.set_xticks(x)
        ax.set_xticklabels(protocols)
        
        if chart_config.show_grid:
            ax.grid(True, alpha=0.3)
        
        if chart_config.show_legend and metrics:
            ax.legend()
        
        plt.tight_layout()
        
        return ChartData(
            figure=fig,
            chart_type="comparison",
            data_summary={
                "protocols": len(protocols),
                "metrics": len(metrics),
                "total_comparisons": len(protocols) * len(metrics)
            }
        )
    
    def create_traffic_trend_chart(self, 
                                  distribution: ProtocolDistribution,
                                  config: Optional[ChartConfig] = None) -> ChartData:
        """创建流量趋势图表
        
        Args:
            distribution: 协议分布数据
            config: 图表配置
            
        Returns:
            ChartData: 包含图表对象的数据
        """
        chart_config = config or self.config
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(chart_config.figsize[0], 
                                                     chart_config.figsize[1] * 1.2), 
                                      dpi=chart_config.dpi)
        
        if not distribution.protocol_counts:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=14)
            ax1.set_title('数据包流量趋势')
            ax2.set_title('字节流量趋势')
            return ChartData(figure=fig, chart_type="trend", 
                           data_summary={"protocols": 0})
        
        # 准备数据
        protocols = list(distribution.protocol_counts.keys())
        packet_counts = list(distribution.protocol_counts.values())
        byte_counts = [distribution.protocol_bytes.get(p, 0) for p in protocols]
        
        # 排序
        sorted_packet_data = sorted(zip(protocols, packet_counts), key=lambda x: x[1], reverse=True)
        sorted_byte_data = sorted(zip(protocols, byte_counts), key=lambda x: x[1], reverse=True)
        
        # 数据包趋势图
        protocols_p, counts_p = zip(*sorted_packet_data)
        colors = plt.cm.get_cmap(chart_config.color_scheme)(np.linspace(0, 1, len(protocols_p)))
        
        bars1 = ax1.bar(protocols_p, counts_p, color=colors)
        ax1.set_title('数据包流量趋势')
        ax1.set_ylabel('数据包数')
        
        # 字节趋势图
        protocols_b, counts_b = zip(*sorted_byte_data)
        bars2 = ax2.bar(protocols_b, counts_b, color=colors)
        ax2.set_title('字节流量趋势')
        ax2.set_ylabel('字节数')
        ax2.set_xlabel('协议')
        
        # 添加数值标签
        for bars, counts in [(bars1, counts_p), (bars2, counts_b)]:
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax = bar.axes
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{count:,}', ha='center', va='bottom', fontsize=8)
        
        # 设置网格
        if chart_config.show_grid:
            ax1.grid(True, alpha=0.3)
            ax2.grid(True, alpha=0.3)
        
        # 旋转标签
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        return ChartData(
            figure=fig,
            chart_type="trend",
            data_summary={
                "protocols": len(protocols),
                "total_packets": sum(packet_counts),
                "total_bytes": sum(byte_counts),
                "top_packet_protocol": protocols_p[0] if protocols_p else None,
                "top_byte_protocol": protocols_b[0] if protocols_b else None
            }
        )
    
    def embed_chart_in_tkinter(self, chart_data: ChartData, parent: tk.Widget) -> FigureCanvasTkAgg:
        """将图表嵌入到Tkinter窗口中
        
        Args:
            chart_data: 图表数据
            parent: 父窗口组件
            
        Returns:
            FigureCanvasTkAgg: Tkinter画布对象
        """
        canvas = FigureCanvasTkAgg(chart_data.figure, parent)
        canvas.draw()
        chart_data.canvas = canvas
        return canvas
    
    def save_chart(self, chart_data: ChartData, filepath: str, **kwargs):
        """保存图表到文件
        
        Args:
            chart_data: 图表数据
            filepath: 保存路径
            **kwargs: 保存参数 (dpi, bbox_inches等)
        """
        save_kwargs = {
            'dpi': kwargs.get('dpi', 300),
            'bbox_inches': kwargs.get('bbox_inches', 'tight'),
            'facecolor': kwargs.get('facecolor', 'white'),
            'edgecolor': kwargs.get('edgecolor', 'none')
        }
        
        chart_data.figure.savefig(filepath, **save_kwargs)
    
    def close_chart(self, chart_data: ChartData):
        """关闭图表并释放资源
        
        Args:
            chart_data: 图表数据
        """
        if chart_data.canvas:
            chart_data.canvas.get_tk_widget().destroy()
        plt.close(chart_data.figure)
    
    # 兼容性方法 - 为protocol_stats_dialog.py提供向后兼容
    def create_pie_chart(self, distribution: ProtocolDistribution, config: Optional[ChartConfig] = None, parent: Optional[tk.Widget] = None) -> Optional[FigureCanvasTkAgg]:
        """创建饼图 (兼容性方法)
        
        Args:
            distribution: 协议分布数据
            config: 图表配置
            parent: 父窗口组件
            
        Returns:
            FigureCanvasTkAgg: Tkinter画布对象，如果出错则返回None
        """
        try:
            chart_data = self.create_protocol_pie_chart(distribution, config)
            # 如果没有提供父窗口，创建一个临时的
            if parent is None:
                import tkinter as tk
                parent = tk.Frame()
            canvas = FigureCanvasTkAgg(chart_data.figure, parent)
            canvas.draw()
            return canvas
        except Exception as e:
            print(f"创建饼图失败: {e}")
            return None
    
    def create_bar_chart(self, distribution: ProtocolDistribution, config: Optional[ChartConfig] = None, parent: Optional[tk.Widget] = None) -> Optional[FigureCanvasTkAgg]:
        """创建柱状图 (兼容性方法)
        
        Args:
            distribution: 协议分布数据
            config: 图表配置
            parent: 父窗口组件
            
        Returns:
            FigureCanvasTkAgg: Tkinter画布对象，如果出错则返回None
        """
        try:
            chart_data = self.create_protocol_bar_chart(distribution, "packets", config)
            # 如果没有提供父窗口，创建一个临时的
            if parent is None:
                import tkinter as tk
                parent = tk.Frame()
            canvas = FigureCanvasTkAgg(chart_data.figure, parent)
            canvas.draw()
            return canvas
        except Exception as e:
            print(f"创建柱状图失败: {e}")
            return None