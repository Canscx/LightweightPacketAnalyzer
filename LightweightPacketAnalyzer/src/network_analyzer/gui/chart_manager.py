"""
图表管理器

提供matplotlib图表的创建、更新、导出功能。
"""

import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np

# 设置matplotlib中文字体支持
import matplotlib.font_manager as fm

def setup_chinese_font():
    """设置中文字体支持"""
    try:
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
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.family'] = 'sans-serif'
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
    except Exception:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False

# 初始化字体设置
setup_chinese_font()


class ChartManager:
    """图表管理器，负责matplotlib图表的创建和管理"""
    
    def __init__(self, parent_widget: tk.Widget):
        """
        初始化图表管理器
        
        Args:
            parent_widget: 父级tkinter组件
        """
        self.parent = parent_widget
        self.logger = logging.getLogger(__name__)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # 创建tkinter画布
        self.canvas = FigureCanvasTkAgg(self.figure, parent_widget)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # 将Canvas widget添加到父容器中
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # 协议线条存储
        self.protocol_lines = {}
        self.protocol_colors = {
            'TCP': '#1f77b4',    # 蓝色
            'UDP': '#ff7f0e',    # 橙色
            'ICMP': '#2ca02c',   # 绿色
            'DNS': '#d62728',    # 红色
            'HTTP': '#9467bd',   # 紫色
            'HTTPS': '#8c564b',  # 棕色
            'Other': '#7f7f7f'   # 灰色
        }
        
        # 图表配置
        self.setup_chart_style()
        
        self.logger.info("图表管理器初始化完成")
    
    def setup_chart_style(self) -> None:
        """设置图表样式"""
        try:
            # 设置图表标题和标签（使用英文避免字体问题）
            self.ax.set_title('Network Traffic Trends', fontsize=16, fontweight='bold', pad=20)
            self.ax.set_xlabel('Time', fontsize=12)
            self.ax.set_ylabel('Packet Count', fontsize=12)
            
            # 设置网格
            self.ax.grid(True, alpha=0.3, linestyle='--')
            
            # 设置背景色
            self.ax.set_facecolor('#f8f9fa')
            self.figure.patch.set_facecolor('white')
            
            # 清除现有的时间轴设置，稍后根据数据动态设置
            
            # 自动调整布局
            self.figure.tight_layout()
            
        except Exception as e:
            self.logger.error(f"设置图表样式失败: {e}")
    
    def create_trends_chart(self, data: Dict[str, Any]) -> None:
        """
        创建趋势图表
        
        Args:
            data: 趋势数据，格式：
            {
                'timestamps': [datetime, ...],
                'data': {
                    'TCP': {'counts': [int, ...], 'bytes': [int, ...]},
                    'UDP': {'counts': [int, ...], 'bytes': [int, ...]},
                    ...
                }
            }
        """
        try:
            self.logger.info(f"开始创建趋势图表，数据: {data is not None}")
            
            if not data or 'timestamps' not in data or 'data' not in data:
                self.logger.warning("数据格式无效，创建空图表")
                self._create_empty_chart()
                return
            
            timestamps = data['timestamps']
            protocol_data = data['data']
            
            self.logger.info(f"时间戳数量: {len(timestamps)}, 协议数量: {len(protocol_data)}")
            
            if not timestamps:
                self.logger.warning("时间戳数据为空，创建空图表")
                self._create_empty_chart()
                return
            
            # 清除现有线条
            self.clear_chart()
            
            # 为每个协议创建趋势线
            lines_created = 0
            for protocol, values in protocol_data.items():
                if protocol in self.protocol_colors:
                    counts = values.get('counts', [])
                    self.logger.debug(f"协议 {protocol}: {len(counts)} 个数据点")
                    
                    if counts and len(counts) == len(timestamps):
                        line, = self.ax.plot(
                            timestamps, 
                            counts,
                            label=f'{protocol} ({sum(counts)} packets)',
                            color=self.protocol_colors[protocol],
                            linewidth=2,
                            marker='o',
                            markersize=3,
                            alpha=0.8
                        )
                        self.protocol_lines[protocol] = line
                        lines_created += 1
                        self.logger.debug(f"成功创建 {protocol} 趋势线")
            
            self.logger.info(f"共创建 {lines_created} 条趋势线")
            
            # 如果没有创建任何线条，显示空图表
            if lines_created == 0:
                self._create_empty_chart()
            else:
                # 更新图表显示
                self.update_chart_display()
            
        except Exception as e:
            self.logger.error(f"创建趋势图表失败: {e}")
            self._create_empty_chart()
    
    def _create_empty_chart(self) -> None:
        """创建空图表"""
        try:
            self.clear_chart()
            # 添加提示文本
            self.ax.text(0.5, 0.5, 'No data available\nPlease capture some packets first', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=14, alpha=0.6)
            self.canvas.draw()
            self.logger.info("已创建空图表")
        except Exception as e:
            self.logger.error(f"创建空图表失败: {e}")
    
    def update_chart_data(self, data: Dict[str, Any]) -> None:
        """
        更新图表数据
        
        Args:
            data: 新的趋势数据
        """
        try:
            if not data or 'timestamps' not in data or 'data' not in data:
                return
            
            timestamps = data['timestamps']
            protocol_data = data['data']
            
            if not timestamps:
                return
            
            # 更新现有线条数据
            for protocol, line in self.protocol_lines.items():
                if protocol in protocol_data:
                    counts = protocol_data[protocol].get('counts', [])
                    if counts and len(counts) == len(timestamps):
                        line.set_data(timestamps, counts)
                        # 更新标签
                        line.set_label(f'{protocol} ({sum(counts)} packets)')
            
            # 如果有新协议，添加新线条
            for protocol, values in protocol_data.items():
                if protocol not in self.protocol_lines and protocol in self.protocol_colors:
                    counts = values.get('counts', [])
                    if counts and len(counts) == len(timestamps):
                        line, = self.ax.plot(
                            timestamps, 
                            counts,
                            label=f'{protocol} ({sum(counts)} packets)',
                            color=self.protocol_colors[protocol],
                            linewidth=2,
                            marker='o',
                            markersize=3,
                            alpha=0.8
                        )
                        self.protocol_lines[protocol] = line
            
            # 更新图表显示
            self.update_chart_display()
            
        except Exception as e:
            self.logger.error(f"更新图表数据失败: {e}")
    
    def update_chart_display(self) -> None:
        """更新图表显示"""
        try:
            # 重新计算坐标轴范围
            self.ax.relim()
            self.ax.autoscale_view()
            
            # 动态设置时间轴格式
            if self.protocol_lines:
                # 获取时间范围
                xlim = self.ax.get_xlim()
                time_range_hours = (xlim[1] - xlim[0]) * 24  # 转换为小时
                
                if time_range_hours <= 1:  # 1小时内，显示分:秒
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
                    self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
                elif time_range_hours <= 6:  # 6小时内，显示时:分
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
                else:  # 超过6小时，显示时:分
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            
            # 更新图例
            if self.protocol_lines:
                self.ax.legend(loc='upper right', framealpha=0.9)
            
            # 格式化时间轴（旋转标签）
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
            
            # 重绘画布
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"更新图表显示失败: {e}")
    
    def toggle_protocol_line(self, protocol: str, visible: bool) -> None:
        """
        切换协议线显示状态
        
        Args:
            protocol: 协议名称
            visible: 是否可见
        """
        try:
            if protocol in self.protocol_lines:
                line = self.protocol_lines[protocol]
                line.set_visible(visible)
                
                # 重新绘制
                self.canvas.draw()
                
                self.logger.debug(f"协议 {protocol} 线条可见性设置为: {visible}")
            
        except Exception as e:
            self.logger.error(f"切换协议线显示失败: {e}")
    
    def clear_chart(self) -> None:
        """清除图表内容"""
        try:
            self.ax.clear()
            self.protocol_lines.clear()
            self.setup_chart_style()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"清除图表失败: {e}")
    
    def export_to_png(self, filepath: Optional[str] = None, dpi: int = 300) -> bool:
        """
        导出图表为PNG图片
        
        Args:
            filepath: 文件路径，None时弹出保存对话框
            dpi: 图片分辨率
            
        Returns:
            是否导出成功
        """
        try:
            if filepath is None:
                # 弹出文件保存对话框
                filepath = filedialog.asksaveasfilename(
                    title="保存流量趋势图",
                    defaultextension=".png",
                    filetypes=[
                        ("PNG图片", "*.png"),
                        ("所有文件", "*.*")
                    ],
                    initialfile=f"traffic_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
            
            if not filepath:
                return False
            
            # 保存图片
            self.figure.savefig(
                filepath,
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none',
                format='png'
            )
            
            messagebox.showinfo("导出成功", f"流量趋势图已保存到:\n{filepath}")
            self.logger.info(f"图表导出成功: {filepath}")
            return True
            
        except Exception as e:
            error_msg = f"导出图表失败: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("导出失败", error_msg)
            return False
    
    def set_time_range(self, start_time: datetime, end_time: datetime) -> None:
        """
        设置时间轴范围
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        """
        try:
            self.ax.set_xlim(start_time, end_time)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"设置时间范围失败: {e}")
    
    def set_y_range(self, min_value: float, max_value: float) -> None:
        """
        设置Y轴范围
        
        Args:
            min_value: 最小值
            max_value: 最大值
        """
        try:
            self.ax.set_ylim(min_value, max_value)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"设置Y轴范围失败: {e}")
    
    def get_canvas_widget(self) -> tk.Widget:
        """获取tkinter画布组件"""
        return self.canvas_widget
    
    def destroy(self) -> None:
        """销毁图表管理器"""
        try:
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'figure'):
                plt.close(self.figure)
            
            self.logger.info("图表管理器已销毁")
            
        except Exception as e:
            self.logger.error(f"销毁图表管理器失败: {e}")
    
    def add_protocol_color(self, protocol: str, color: str) -> None:
        """
        添加协议颜色配置
        
        Args:
            protocol: 协议名称
            color: 颜色值（十六进制）
        """
        self.protocol_colors[protocol] = color
        self.logger.debug(f"添加协议颜色配置: {protocol} -> {color}")
    
    def get_protocol_colors(self) -> Dict[str, str]:
        """获取协议颜色配置"""
        return self.protocol_colors.copy()
    
    def set_chart_title(self, title: str) -> None:
        """
        设置图表标题
        
        Args:
            title: 标题文本
        """
        try:
            self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"设置图表标题失败: {e}")
    
    def enable_zoom_pan(self) -> None:
        """启用缩放和平移功能"""
        try:
            # 启用matplotlib的导航工具栏功能
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            
            if not hasattr(self, 'toolbar'):
                self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
                self.toolbar.update()
            
        except Exception as e:
            self.logger.error(f"启用缩放平移功能失败: {e}")