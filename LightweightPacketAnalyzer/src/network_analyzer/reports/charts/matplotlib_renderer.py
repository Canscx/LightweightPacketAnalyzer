"""
Matplotlib渲染器

提供底层的Matplotlib图表渲染功能，包括：
- 图表样式配置
- 渲染参数管理
- 输出格式控制
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np


logger = logging.getLogger(__name__)


class MatplotlibRenderer:
    """Matplotlib渲染器"""
    
    def __init__(self, style: str = 'default', dpi: int = 300):
        """
        初始化渲染器
        
        Args:
            style: 图表样式
            dpi: 图片分辨率
        """
        self.style = style
        self.dpi = dpi
        self.logger = logging.getLogger(__name__)
        
        # 应用样式
        self._apply_style()
    
    def _apply_style(self):
        """应用图表样式"""
        try:
            plt.style.use(self.style)
            
            # 自定义样式参数
            custom_params = {
                'figure.dpi': 100,
                'savefig.dpi': self.dpi,
                'savefig.bbox': 'tight',
                'savefig.pad_inches': 0.1,
                'font.size': 10,
                'axes.titlesize': 14,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 10,
                'axes.grid': True,
                'grid.alpha': 0.3,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.axisbelow': True,
            }
            
            plt.rcParams.update(custom_params)
            
        except Exception as e:
            self.logger.error(f"应用图表样式失败: {e}")
    
    def create_figure(self, figsize: Tuple[float, float] = (10, 6)) -> Tuple[plt.Figure, plt.Axes]:
        """
        创建图表对象
        
        Args:
            figsize: 图表尺寸
            
        Returns:
            Tuple: (Figure对象, Axes对象)
        """
        try:
            fig, ax = plt.subplots(figsize=figsize)
            return fig, ax
        except Exception as e:
            self.logger.error(f"创建图表对象失败: {e}")
            raise
    
    def save_figure(self, fig: plt.Figure, filepath: str, 
                   format: str = 'png', **kwargs) -> bool:
        """
        保存图表到文件
        
        Args:
            fig: Figure对象
            filepath: 保存路径
            format: 文件格式
            **kwargs: 额外参数
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 默认保存参数
            save_params = {
                'dpi': self.dpi,
                'bbox_inches': 'tight',
                'pad_inches': 0.1,
                'facecolor': 'white',
                'edgecolor': 'none'
            }
            
            # 更新用户参数
            save_params.update(kwargs)
            
            # 保存图表
            fig.savefig(filepath, format=format, **save_params)
            
            self.logger.debug(f"图表保存成功: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存图表失败: {e}")
            return False
        finally:
            plt.close(fig)
    
    def create_color_palette(self, n_colors: int, 
                           palette: str = 'viridis') -> np.ndarray:
        """
        创建颜色调色板
        
        Args:
            n_colors: 颜色数量
            palette: 调色板名称
            
        Returns:
            np.ndarray: 颜色数组
        """
        try:
            if palette in plt.colormaps():
                cmap = plt.get_cmap(palette)
                return cmap(np.linspace(0, 1, n_colors))
            else:
                # 使用默认颜色
                return plt.cm.tab10(np.linspace(0, 1, n_colors))
                
        except Exception as e:
            self.logger.error(f"创建颜色调色板失败: {e}")
            # 返回基础颜色
            return np.array(['blue', 'red', 'green', 'orange', 'purple'] * (n_colors // 5 + 1))[:n_colors]
    
    def add_watermark(self, ax: plt.Axes, text: str = "轻量级数据包分析器"):
        """
        添加水印
        
        Args:
            ax: Axes对象
            text: 水印文本
        """
        try:
            ax.text(0.95, 0.05, text, 
                   transform=ax.transAxes,
                   fontsize=8, alpha=0.5,
                   ha='right', va='bottom',
                   style='italic')
        except Exception as e:
            self.logger.error(f"添加水印失败: {e}")
    
    def format_axes(self, ax: plt.Axes, 
                   title: Optional[str] = None,
                   xlabel: Optional[str] = None,
                   ylabel: Optional[str] = None,
                   grid: bool = True):
        """
        格式化坐标轴
        
        Args:
            ax: Axes对象
            title: 标题
            xlabel: X轴标签
            ylabel: Y轴标签
            grid: 是否显示网格
        """
        try:
            if title:
                ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=12)
            
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=12)
            
            if grid:
                ax.grid(True, alpha=0.3)
            
            # 添加水印
            self.add_watermark(ax)
            
        except Exception as e:
            self.logger.error(f"格式化坐标轴失败: {e}")
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的输出格式
        
        Returns:
            List[str]: 支持的格式列表
        """
        try:
            return list(plt.gcf().canvas.get_supported_filetypes().keys())
        except Exception as e:
            self.logger.error(f"获取支持格式失败: {e}")
            return ['png', 'jpg', 'pdf', 'svg']