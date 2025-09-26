#!/usr/bin/env python3
"""
SettingsDialog基础框架测试脚本

测试设置对话框的基础UI结构和功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.config.settings import Settings
from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_settings_dialog():
    """测试SettingsDialog基础框架"""
    print("=" * 60)
    print("SettingsDialog基础框架测试")
    print("=" * 60)
    
    try:
        print("1. 创建主窗口...")
        root = tk.Tk()
        root.title("测试主窗口")
        root.geometry("800x600")
        
        # 创建一个简单的主窗口内容
        main_label = ttk.Label(root, text="这是测试主窗口\\n点击按钮打开设置对话框", 
                              font=("Arial", 14), anchor="center")
        main_label.pack(expand=True)
        
        print("   ✅ 主窗口创建成功")
        
        print("2. 初始化Settings...")
        settings = Settings()
        print(f"   ✅ Settings初始化成功: {settings.APP_NAME}")
        
        print("3. 测试SettingsDialog创建...")
        
        def open_settings_dialog():
            """打开设置对话框"""
            try:
                dialog = SettingsDialog(root, settings, main_window=None)
                print("   ✅ SettingsDialog实例创建成功")
                
                # 显示对话框
                result = dialog.show()
                print(f"   ✅ 对话框显示完成，返回结果: {result}")
                
                if result:
                    print("   📝 用户保存了设置")
                else:
                    print("   📝 用户取消了设置")
                    
            except Exception as e:
                print(f"   ❌ 打开设置对话框失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 创建打开设置对话框的按钮
        open_button = ttk.Button(
            root, 
            text="打开设置对话框", 
            command=open_settings_dialog,
            width=20
        )
        open_button.pack(pady=20)
        
        print("4. 测试对话框组件...")
        
        # 创建对话框实例进行组件测试
        dialog = SettingsDialog(root, settings)
        
        # 测试对话框创建
        dialog._create_dialog()
        print("   ✅ 对话框窗口创建成功")
        
        # 测试UI创建
        dialog._create_ui()
        print("   ✅ 对话框UI创建成功")
        
        # 测试配置加载
        dialog._load_current_settings()
        print("   ✅ 配置加载成功")
        
        # 测试绑定设置
        dialog._setup_bindings()
        print("   ✅ 键盘绑定设置成功")
        
        # 测试居中显示
        dialog._center_dialog()
        print("   ✅ 对话框居中显示成功")
        
        # 关闭测试对话框
        dialog.dialog.destroy()
        print("   ✅ 测试对话框已关闭")
        
        print("5. 测试验证功能...")
        
        # 测试设置验证
        is_valid, errors = dialog._validate_all_settings()
        print(f"   ✅ 设置验证: {is_valid}, 错误数: {len(errors)}")
        
        # 测试设置收集
        settings_dict = dialog._collect_settings()
        print(f"   ✅ 设置收集: {len(settings_dict)}项")
        
        print("\\n" + "=" * 60)
        print("✅ SettingsDialog基础框架测试完成！")
        print("💡 现在可以手动测试对话框界面")
        print("=" * 60)
        
        # 启动主窗口事件循环
        print("\\n🚀 启动GUI测试界面...")
        print("   - 点击按钮可以打开设置对话框")
        print("   - 测试各个选项卡和按钮功能")
        print("   - 关闭主窗口结束测试")
        
        root.mainloop()
        
        return True
        
    except Exception as error:
        print(f"\\n❌ 测试失败: {error}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    setup_logging()
    success = test_settings_dialog()
    sys.exit(0 if success else 1)