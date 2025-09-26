#!/usr/bin/env python3
"""
测试报告生成对话框UI改进

测试窗口大小调整后的界面效果
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.dialogs.report_generation_dialog import show_report_generation_dialog


def test_report_dialog_ui():
    """测试报告生成对话框UI"""
    print("🧪 测试报告生成对话框UI改进...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("UI测试 - 报告生成对话框")
    root.geometry("400x300")
    
    # 初始化数据管理器
    data_manager = DataManager("test_traffic_trends.db")
    
    # 创建测试按钮
    test_frame = ttk.Frame(root, padding="20")
    test_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(test_frame, text="点击按钮测试报告生成对话框", 
              font=("Arial", 12)).pack(pady=10)
    
    def open_dialog():
        """打开报告生成对话框"""
        try:
            show_report_generation_dialog(root, data_manager)
        except Exception as e:
            print(f"❌ 打开对话框失败: {e}")
    
    test_button = ttk.Button(test_frame, text="打开报告生成对话框", 
                           command=open_dialog)
    test_button.pack(pady=20)
    
    # 添加说明
    info_text = """
UI改进说明：
• 窗口大小：700x650（原600x500）
• 允许调整大小
• 最小尺寸：650x600
• 改进网格布局响应性
    """
    
    ttk.Label(test_frame, text=info_text, justify=tk.LEFT, 
              foreground="blue").pack(pady=10)
    
    print("✅ 测试界面已启动")
    print("📋 请点击按钮测试报告生成对话框的新界面")
    print("🔍 检查点：")
    print("   - 窗口大小是否合适")
    print("   - 底部按钮是否可见和可点击")
    print("   - 是否可以调整窗口大小")
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    test_report_dialog_ui()