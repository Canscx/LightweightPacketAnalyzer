#!/usr/bin/env python3
"""
测试打开会话功能
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.main_window import SessionDialog

def test_session_dialog():
    """测试会话选择对话框"""
    
    # 创建数据管理器
    db_path = "data/test_network_analyzer.db"
    os.makedirs("data", exist_ok=True)
    
    data_manager = DataManager(db_path)
    
    # 创建一些测试会话
    session1_id = data_manager.create_session("测试会话1")
    session2_id = data_manager.create_session("测试会话2")
    
    # 更新会话数据
    data_manager.update_session(session1_id, 100, 50000)
    data_manager.update_session(session2_id, 200, 100000)
    
    print(f"创建测试会话: {session1_id}, {session2_id}")
    
    # 创建主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建并显示会话对话框
    dialog = SessionDialog(root, data_manager)
    selected_session_id = dialog.show()
    
    if selected_session_id:
        print(f"用户选择了会话ID: {selected_session_id}")
    else:
        print("用户取消了选择")
    
    root.destroy()

if __name__ == "__main__":
    test_session_dialog()