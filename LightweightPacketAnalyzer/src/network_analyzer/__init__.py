"""
网络流量统计系统 (Network Traffic Analyzer)

一个轻量级的网络数据包分析器，用于计算机网络课程设计。
"""

__version__ = "0.1.0"
__author__ = "Student"
__email__ = "student@example.com"
__description__ = "轻量级网络数据包分析器 - 计算机网络课程设计"

# 导入主要模块
from .main import main

# 定义公共API
__all__ = [
    "main",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]