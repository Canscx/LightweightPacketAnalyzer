"""
网络分析器报告生成模块

该模块提供完整的报告生成功能，支持多种格式输出：
- PDF格式报告
- HTML格式报告  
- CSV数据导出

主要组件：
- ReportGenerator: 统一的报告生成接口
- DataCollector: 数据收集和预处理
- ChartGenerator: 图表生成器
- TemplateManager: 模板管理器
"""

from .report_generator import ReportGenerator
from .data_collector import DataCollector

__version__ = "1.0.0"
__author__ = "Network Analyzer Team"

__all__ = [
    "ReportGenerator",
    "DataCollector",
]