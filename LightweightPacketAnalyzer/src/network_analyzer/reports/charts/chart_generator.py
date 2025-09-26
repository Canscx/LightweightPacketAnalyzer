"""
图表生成器

提供各种统计图表的生成功能，支持：
- 饼图：协议分布统计
- 线图：流量趋势分析
- 直方图：数据包大小分布
- 条形图：Top协议统计
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime


logger = logging.getLogger(__name__)


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化图表生成器
        
        Args:
            output_dir: 图表输出目录，默认为临时目录
        """
        if output_dir is None:
            output_dir = Path.cwd() / "temp" / "charts"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # 设置中文字体
        self._setup_chinese_font()
        
        # 设置图表样式
        self._setup_chart_style()
    
    def _setup_chinese_font(self):
        """设置中文字体支持"""
        try:
            # 方法1: 尝试直接使用字体文件路径
            font_paths = [
                r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑
                r"C:\Windows\Fonts\simhei.ttf",  # 黑体
                r"C:\Windows\Fonts\simsun.ttc",  # 宋体
            ]
            
            self.font_path = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.font_path = font_path
                    self.logger.info(f"找到中文字体文件: {font_path}")
                    break
            
            # 方法2: 使用系统字体名称作为备选
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun']
            
            self.font_name = None
            for font_name in chinese_fonts:
                if font_name in available_fonts:
                    self.font_name = font_name
                    break
            
            # 应用字体设置
            self._apply_font_settings()
                
        except Exception as e:
            self.logger.error(f"设置中文字体失败: {e}")
            # 设置安全的默认字体
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
    
    def _apply_font_settings(self):
        """应用字体设置"""
        try:
            if self.font_name:
                # 使用系统字体名称
                plt.rcParams.update({
                    'font.family': 'sans-serif',
                    'font.sans-serif': [self.font_name, 'DejaVu Sans', 'Arial'],
                    'axes.unicode_minus': False
                })
                self.logger.info(f"应用系统字体: {self.font_name}")
            else:
                # 使用默认字体
                plt.rcParams.update({
                    'font.family': 'sans-serif', 
                    'font.sans-serif': ['DejaVu Sans', 'Arial'],
                    'axes.unicode_minus': False
                })
                self.logger.warning("使用默认字体")
                
        except Exception as e:
            self.logger.error(f"应用字体设置失败: {e}")
    
    def _ensure_chinese_font(self):
        """确保中文字体设置（在每次绘图前调用）"""
        try:
            # 重新应用字体设置
            self._apply_font_settings()
            
            # 如果有字体文件路径，创建FontProperties对象
            if hasattr(self, 'font_path') and self.font_path:
                from matplotlib.font_manager import FontProperties
                self.font_prop = FontProperties(fname=self.font_path)
            else:
                self.font_prop = None
                
        except Exception as e:
            self.logger.error(f"确保中文字体失败: {e}")
            self.font_prop = None
    
    def _setup_chart_style(self):
        """设置图表样式"""
        try:
            # 设置图表样式
            plt.style.use('default')
            
            # 自定义样式参数
            plt.rcParams.update({
                'figure.figsize': (10, 6),
                'figure.dpi': 100,
                'savefig.dpi': 300,
                'savefig.bbox': 'tight',
                'axes.grid': True,
                'grid.alpha': 0.3,
                'axes.spines.top': False,
                'axes.spines.right': False,
            })
            
        except Exception as e:
            self.logger.error(f"设置图表样式失败: {e}")
    
    def generate_protocol_pie_chart(self, protocol_data: Dict[str, int], 
                                  title: str = "协议分布统计") -> str:
        """
        生成协议分布饼图
        
        Args:
            protocol_data: 协议数据 {协议名: 数量}
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            # 准备数据
            protocols = list(protocol_data.keys())
            counts = list(protocol_data.values())
            
            # 处理数据：合并小比例协议
            total = sum(counts)
            threshold = total * 0.02  # 小于2%的协议合并为"其他"
            
            filtered_protocols = []
            filtered_counts = []
            other_count = 0
            
            for protocol, count in zip(protocols, counts):
                if count >= threshold:
                    filtered_protocols.append(protocol)
                    filtered_counts.append(count)
                else:
                    other_count += count
            
            if other_count > 0:
                filtered_protocols.append("其他")
                filtered_counts.append(other_count)
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 生成颜色
            colors = plt.cm.Set3(np.linspace(0, 1, len(filtered_protocols)))
            
            # 绘制饼图
            wedges, texts, autotexts = ax.pie(
                filtered_counts,
                labels=filtered_protocols,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05] * len(filtered_protocols)  # 轻微分离
            )
            
            # 设置标题（使用中文字体）
            if hasattr(self, 'font_prop') and self.font_prop:
                ax.set_title(title, fontproperties=self.font_prop, fontsize=16, fontweight='bold', pad=20)
            else:
                ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                if hasattr(self, 'font_prop') and self.font_prop:
                    autotext.set_fontproperties(self.font_prop)
            
            # 设置标签字体
            for text in texts:
                if hasattr(self, 'font_prop') and self.font_prop:
                    text.set_fontproperties(self.font_prop)
            
            # 添加图例
            legend = ax.legend(wedges, filtered_protocols, 
                             title="协议类型",
                             loc="center left",
                             bbox_to_anchor=(1, 0, 0.5, 1))
            
            # 设置图例字体
            if hasattr(self, 'font_prop') and self.font_prop:
                legend.get_title().set_fontproperties(self.font_prop)
                for text in legend.get_texts():
                    text.set_fontproperties(self.font_prop)
            
            # 保存图表
            filename = f"protocol_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            self.logger.info(f"协议饼图生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成协议饼图失败: {e}")
            raise
    
    def generate_traffic_trend_chart(self, time_data: List[float], 
                                   packet_counts: List[int],
                                   title: str = "流量趋势分析") -> str:
        """
        生成流量趋势线图
        
        Args:
            time_data: 时间数据列表
            packet_counts: 对应的数据包数量
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            # 转换时间数据
            timestamps = [datetime.fromtimestamp(t) for t in time_data]
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 绘制线图
            ax.plot(timestamps, packet_counts, 
                   color='#007acc', linewidth=2, marker='o', markersize=4)
            
            # 设置标题和标签（使用中文字体）
            if hasattr(self, 'font_prop') and self.font_prop:
                ax.set_title(title, fontproperties=self.font_prop, fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('时间', fontproperties=self.font_prop, fontsize=12)
                ax.set_ylabel('数据包数量', fontproperties=self.font_prop, fontsize=12)
            else:
                ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('时间', fontsize=12)
                ax.set_ylabel('数据包数量', fontsize=12)
            
            # 格式化x轴时间显示
            fig.autofmt_xdate()
            
            # 添加网格
            ax.grid(True, alpha=0.3)
            
            # 添加数值标注（仅在数据点较少时）
            if len(packet_counts) <= 20:
                for i, (x, y) in enumerate(zip(timestamps, packet_counts)):
                    ax.annotate(f'{y}', (x, y), textcoords="offset points", 
                              xytext=(0,10), ha='center', fontsize=8)
            
            # 保存图表
            filename = f"traffic_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            self.logger.info(f"流量趋势图生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成流量趋势图失败: {e}")
            raise
    
    def generate_top_protocols_bar_chart(self, protocol_data: List[Tuple[str, int]], 
                                       title: str = "Top协议统计") -> str:
        """
        生成Top协议条形图
        
        Args:
            protocol_data: 协议数据列表 [(协议名, 数量), ...]
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            # 准备数据
            protocols = [item[0] for item in protocol_data]
            counts = [item[1] for item in protocol_data]
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 生成颜色渐变
            colors = plt.cm.viridis(np.linspace(0, 1, len(protocols)))
            
            # 绘制条形图
            bars = ax.bar(protocols, counts, color=colors)
            
            # 设置标题和标签（使用中文字体）
            if hasattr(self, 'font_prop') and self.font_prop:
                ax.set_title(title, fontproperties=self.font_prop, fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('协议类型', fontproperties=self.font_prop, fontsize=12)
                ax.set_ylabel('数据包数量', fontproperties=self.font_prop, fontsize=12)
            else:
                ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('协议类型', fontsize=12)
                ax.set_ylabel('数据包数量', fontsize=12)
            
            # 旋转x轴标签以避免重叠
            plt.xticks(rotation=45, ha='right')
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=10)
            
            # 保存图表
            filename = f"top_protocols_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            self.logger.info(f"Top协议条形图生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成Top协议条形图失败: {e}")
            raise
    
    def generate_packet_size_histogram(self, packet_sizes: List[int], 
                                     title: str = "数据包大小分布") -> str:
        """
        生成数据包大小分布直方图
        
        Args:
            packet_sizes: 数据包大小列表
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 计算合适的bin数量
            bin_count = min(50, max(10, len(packet_sizes) // 20))
            
            # 绘制直方图
            n, bins, patches = ax.hist(packet_sizes, bins=bin_count, 
                                     color='skyblue', alpha=0.7, edgecolor='black')
            
            # 设置标题和标签
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('数据包大小 (字节)', fontsize=12)
            ax.set_ylabel('频次', fontsize=12)
            
            # 添加统计信息
            mean_size = np.mean(packet_sizes)
            median_size = np.median(packet_sizes)
            
            ax.axvline(mean_size, color='red', linestyle='--', 
                      label=f'平均值: {mean_size:.1f}')
            ax.axvline(median_size, color='green', linestyle='--', 
                      label=f'中位数: {median_size:.1f}')
            
            ax.legend()
            
            # 保存图表
            filename = f"packet_size_hist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            self.logger.info(f"数据包大小直方图生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成数据包大小直方图失败: {e}")
            raise
    
    def generate_combined_chart(self, data: Dict[str, Any], 
                              chart_type: str = "dashboard") -> str:
        """
        生成组合图表（仪表板样式）
        
        Args:
            data: 图表数据
            chart_type: 图表类型
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            # 创建子图布局
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 设置主标题
            if hasattr(self, 'font_prop') and self.font_prop:
                fig.suptitle('网络流量分析仪表板', fontproperties=self.font_prop, fontsize=20, fontweight='bold')
            else:
                fig.suptitle('网络流量分析仪表板', fontsize=20, fontweight='bold')
            
            # 1. 协议分布饼图
            if 'protocol_distribution' in data:
                protocol_data = data['protocol_distribution']
                protocols = list(protocol_data.keys())
                counts = list(protocol_data.values())
                
                wedges, texts, autotexts = ax1.pie(counts, labels=protocols, autopct='%1.1f%%', startangle=90)
                
                # 设置字体
                if hasattr(self, 'font_prop') and self.font_prop:
                    ax1.set_title('协议分布', fontproperties=self.font_prop, fontsize=14, fontweight='bold')
                    for text in texts:
                        text.set_fontproperties(self.font_prop)
                    for autotext in autotexts:
                        autotext.set_fontproperties(self.font_prop)
                else:
                    ax1.set_title('协议分布', fontsize=14, fontweight='bold')
            
            # 2. 流量趋势线图
            if 'traffic_trends' in data:
                trends = data['traffic_trends']
                if 'time_data' in trends and 'packet_counts' in trends:
                    ax2.plot(trends['time_data'], trends['packet_counts'], 
                            color='#007acc', linewidth=2)
                    
                    if hasattr(self, 'font_prop') and self.font_prop:
                        ax2.set_title('流量趋势', fontproperties=self.font_prop, fontsize=14, fontweight='bold')
                        ax2.set_xlabel('时间', fontproperties=self.font_prop)
                        ax2.set_ylabel('数据包数量', fontproperties=self.font_prop)
                    else:
                        ax2.set_title('流量趋势', fontsize=14, fontweight='bold')
                        ax2.set_xlabel('时间')
                        ax2.set_ylabel('数据包数量')
            
            # 3. Top协议条形图
            if 'top_protocols' in data:
                top_data = data['top_protocols'][:10]  # 取前10个
                protocols = [item[0] for item in top_data]
                counts = [item[1] for item in top_data]
                
                ax3.bar(protocols, counts, color='lightcoral')
                
                if hasattr(self, 'font_prop') and self.font_prop:
                    ax3.set_title('Top协议', fontproperties=self.font_prop, fontsize=14, fontweight='bold')
                    ax3.set_xlabel('协议', fontproperties=self.font_prop)
                    ax3.set_ylabel('数据包数量', fontproperties=self.font_prop)
                else:
                    ax3.set_title('Top协议', fontsize=14, fontweight='bold')
                    ax3.set_xlabel('协议')
                    ax3.set_ylabel('数据包数量')
                    
                plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            
            # 4. 数据包大小分布
            if 'packet_sizes' in data:
                sizes = data['packet_sizes']
                ax4.hist(sizes, bins=30, color='lightgreen', alpha=0.7)
                
                if hasattr(self, 'font_prop') and self.font_prop:
                    ax4.set_title('数据包大小分布', fontproperties=self.font_prop, fontsize=14, fontweight='bold')
                    ax4.set_xlabel('大小 (字节)', fontproperties=self.font_prop)
                else:
                    ax4.set_title('数据包大小分布', fontsize=14, fontweight='bold')
                    ax4.set_xlabel('大小 (字节)')
                ax4.set_ylabel('频次')
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            self.logger.info(f"组合图表生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成组合图表失败: {e}")
            raise
    
    def cleanup_old_charts(self, keep_days: int = 7):
        """
        清理旧的图表文件
        
        Args:
            keep_days: 保留天数
        """
        try:
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (keep_days * 24 * 3600)
            
            for file_path in self.output_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    self.logger.debug(f"删除旧图表文件: {file_path}")
            
        except Exception as e:
            self.logger.error(f"清理旧图表失败: {e}")
    
    def get_chart_info(self, chart_path: str) -> Dict[str, Any]:
        """
        获取图表文件信息
        
        Args:
            chart_path: 图表文件路径
            
        Returns:
            Dict: 图表信息
        """
        try:
            path = Path(chart_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'filename': path.name,
                'size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
            
        except Exception as e:
            self.logger.error(f"获取图表信息失败: {e}")
            return {'exists': False}