#!/usr/bin/env python3
"""
协议统计对话框测试脚本

测试T4: ProtocolStatsDialog统计对话框界面的实现
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.config.settings import Settings
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.dialogs.protocol_stats_dialog import ProtocolStatsDialog


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_protocol_stats_dialog():
    """测试协议统计对话框"""
    print("开始测试协议统计对话框...")
    
    try:
        # 初始化设置和数据管理器
        settings = Settings()
        data_manager = DataManager(settings.DATABASE_PATH)
        
        # 创建主窗口
        root = tk.Tk()
        root.title("协议统计对话框测试")
        root.geometry("400x300")
        
        # 获取可用的会话
        sessions = data_manager.get_sessions()
        if not sessions:
            messagebox.showerror("错误", "数据库中没有会话数据，请先运行主程序创建会话")
            root.destroy()
            return False
        
        print(f"找到 {len(sessions)} 个会话")
        
        # 使用第一个会话进行测试
        test_session_id = sessions[0]['id']
        print(f"使用会话ID: {test_session_id}")
        
        # 创建测试按钮
        def open_dialog():
            try:
                dialog = ProtocolStatsDialog(root, data_manager, test_session_id)
                result = dialog.show()
                if result:
                    print("对话框返回结果:", result)
                else:
                    print("用户取消了对话框")
            except Exception as e:
                print(f"打开对话框失败: {e}")
                messagebox.showerror("错误", f"打开对话框失败: {e}")
        
        # 创建界面
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="协议统计对话框测试", font=("Arial", 16)).pack(pady=10)
        tk.Label(frame, text=f"测试会话ID: {test_session_id}").pack(pady=5)
        
        tk.Button(frame, text="打开协议统计对话框", command=open_dialog, 
                 font=("Arial", 12), padx=20, pady=10).pack(pady=20)
        
        tk.Button(frame, text="退出", command=root.quit, 
                 font=("Arial", 12), padx=20, pady=5).pack()
        
        print("测试界面已创建，点击按钮测试对话框功能")
        
        # 运行主循环
        root.mainloop()
        
        print("协议统计对话框测试完成")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_dialog_components():
    """测试对话框组件"""
    print("\n测试对话框组件...")
    
    try:
        # 测试导入
        from network_analyzer.gui.dialogs.protocol_stats_dialog import ProtocolStatsDialog
        print("✓ ProtocolStatsDialog导入成功")
        
        # 测试依赖组件
        from network_analyzer.statistics.protocol_statistics import ProtocolStatistics
        from network_analyzer.statistics.statistics_visualizer import StatisticsVisualizer
        print("✓ 依赖组件导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    """主函数"""
    setup_logging()
    
    print("=" * 50)
    print("协议统计对话框 (T4) 测试")
    print("=" * 50)
    
    # 测试组件导入
    if not test_dialog_components():
        print("组件测试失败，退出")
        return 1
    
    # 测试对话框功能
    if not test_protocol_stats_dialog():
        print("对话框测试失败")
        return 1
    
    print("\n所有测试完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())