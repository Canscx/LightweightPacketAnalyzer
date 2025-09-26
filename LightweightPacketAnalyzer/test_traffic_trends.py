#!/usr/bin/env python3
"""
流量趋势功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from datetime import datetime, timedelta
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.traffic_trends_dialog import TrafficTrendsDialog

def test_traffic_trends():
    """测试流量趋势功能"""
    print("开始测试流量趋势功能...")
    
    # 创建主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        # 初始化数据管理器
        data_manager = DataManager("network_analyzer.db")
        print("数据管理器初始化成功")
        
        # 创建流量趋势对话框
        trends_dialog = TrafficTrendsDialog(root, data_manager)
        print("流量趋势对话框创建成功")
        
        # 显示对话框
        trends_dialog.show()
        print("流量趋势对话框已显示")
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("测试完成")

if __name__ == "__main__":
    test_traffic_trends()