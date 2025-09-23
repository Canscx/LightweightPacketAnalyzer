#!/usr/bin/env python3
"""
调试脚本：精确定位Mock对象与int相加的错误位置
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock, patch
import traceback

def debug_main_window_init():
    """调试MainWindow初始化过程"""
    print("开始调试MainWindow初始化...")
    
    try:
        # 创建模拟的settings对象
        mock_settings = Mock()
        mock_settings.DATABASE_PATH = ":memory:"
        # 设置get_database_path方法返回字符串路径而不是Mock对象
        mock_settings.get_database_path.return_value = ":memory:"
        mock_settings.WINDOW_WIDTH = 1200
        mock_settings.WINDOW_HEIGHT = 800
        mock_settings.APP_NAME = "Test App"
        
        print(f"Settings mock创建成功:")
        print(f"  WINDOW_WIDTH: {mock_settings.WINDOW_WIDTH}")
        print(f"  WINDOW_HEIGHT: {mock_settings.WINDOW_HEIGHT}")
        print(f"  APP_NAME: {mock_settings.APP_NAME}")
        
        # 逐步patch各个依赖
        with patch('network_analyzer.storage.data_manager.DataManager') as mock_data_manager, \
             patch('network_analyzer.capture.packet_capture.PacketCapture') as mock_packet_capture, \
             patch('network_analyzer.processing.data_processor.DataProcessor') as mock_data_processor, \
             patch('tkinter.Tk') as mock_tk:
            
            print("所有依赖已patch")
            
            # 设置tk.Tk的mock，并配置其内部属性
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # 配置tkinter内部需要的属性，避免Mock对象与int/str相加的错误
            mock_root._last_child_ids = {}  # 设置为空字典而不是Mock对象
            mock_root.tk = Mock()  # tkinter内部需要的tk属性
            mock_root._w = "."  # tkinter内部的窗口路径，设置为字符串而不是Mock对象
            
            print("开始导入MainWindow...")
            from network_analyzer.gui.main_window import MainWindow
            print("MainWindow导入成功")
            
            print("开始创建MainWindow实例...")
            
            # 尝试创建MainWindow，但先patch _start_gui_updates
            with patch.object(MainWindow, '_start_gui_updates'):
                window = MainWindow(mock_settings)
                print("MainWindow创建成功！")
                
                # 检查各个属性
                print(f"window.settings: {window.settings}")
                print(f"window.root: {window.root}")
                
    except Exception as e:
        print(f"错误发生: {e}")
        print("完整错误堆栈:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_main_window_init()