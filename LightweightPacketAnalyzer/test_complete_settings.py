#!/usr/bin/env python3
"""
完整设置对话框功能测试脚本

测试基础设置和高级设置选项卡的完整功能
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


def test_complete_settings():
    """测试完整设置对话框功能"""
    print("=" * 60)
    print("完整设置对话框功能测试")
    print("=" * 60)
    
    try:
        print("1. 创建主窗口...")
        root = tk.Tk()
        root.title("设置功能测试")
        root.geometry("900x700")
        
        # 创建主窗口内容
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(
            main_frame, 
            text="设置功能完整测试", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        info_text = """
这是设置功能的完整测试界面。

功能特点：
✅ 基础设置选项卡（界面、数据、日志配置）
✅ 高级设置选项卡（性能、捕获、安全配置）
✅ 实时配置验证
✅ 配置保存和加载
✅ 立即生效机制
✅ 重置到默认值
✅ 未保存更改检测

点击下面的按钮打开设置对话框进行测试。
        """
        
        info_label = ttk.Label(
            main_frame, 
            text=info_text.strip(),
            font=("Arial", 10),
            justify=tk.LEFT
        )
        info_label.pack(pady=(0, 20))
        
        print("   ✅ 主窗口创建成功")
        
        print("2. 初始化Settings...")
        settings = Settings()
        print(f"   ✅ Settings初始化成功: {settings.APP_NAME}")
        
        # 显示当前配置信息
        current_config_frame = ttk.LabelFrame(main_frame, text="当前配置信息", padding="10")
        current_config_frame.pack(fill=tk.X, pady=(0, 20))
        
        config_info = f"""窗口大小: {settings.WINDOW_WIDTH}×{settings.WINDOW_HEIGHT}
主题: {settings.THEME}
日志级别: {settings.LOG_LEVEL}
数据保留天数: {settings.DATA_RETENTION_DAYS}
工作线程数: {settings.WORKER_THREADS}
缓冲区大小: {settings.BUFFER_SIZE // 1024}KB"""
        
        config_label = ttk.Label(current_config_frame, text=config_info, font=("Consolas", 9))
        config_label.pack(anchor=tk.W)
        
        print("3. 创建测试按钮...")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def open_settings_dialog():
            """打开设置对话框"""
            try:
                print("\\n" + "="*40)
                print("打开设置对话框...")
                
                dialog = SettingsDialog(root, settings, main_window=None)
                result = dialog.show()
                
                print(f"对话框返回结果: {result}")
                
                if result:
                    print("✅ 用户保存了设置")
                    # 更新显示的配置信息
                    new_config_info = f"""窗口大小: {settings.WINDOW_WIDTH}×{settings.WINDOW_HEIGHT}
主题: {settings.THEME}
日志级别: {settings.LOG_LEVEL}
数据保留天数: {settings.DATA_RETENTION_DAYS}
工作线程数: {settings.WORKER_THREADS}
缓冲区大小: {settings.BUFFER_SIZE // 1024}KB"""
                    config_label.config(text=new_config_info)
                    print("📝 配置信息已更新")
                else:
                    print("📝 用户取消了设置")
                
                print("="*40)
                    
            except Exception as e:
                print(f"❌ 打开设置对话框失败: {e}")
                import traceback
                traceback.print_exc()
        
        def test_settings_validation():
            """测试设置验证功能"""
            try:
                print("\\n测试配置验证功能...")
                
                # 测试有效配置
                valid_settings = {
                    'WINDOW_WIDTH': 1400,
                    'WINDOW_HEIGHT': 900,
                    'LOG_LEVEL': 'DEBUG',
                    'WORKER_THREADS': 4
                }
                
                is_valid, errors = settings.validate_all_settings(valid_settings)
                print(f"有效配置验证: {is_valid}, 错误: {len(errors)}")
                
                # 测试无效配置
                invalid_settings = {
                    'WINDOW_WIDTH': 500,  # 太小
                    'LOG_LEVEL': 'INVALID',  # 无效
                    'WORKER_THREADS': 0  # 无效
                }
                
                is_valid, errors = settings.validate_all_settings(invalid_settings)
                print(f"无效配置验证: {is_valid}, 错误: {len(errors)}")
                for error in errors:
                    print(f"  - {error}")
                
            except Exception as e:
                print(f"❌ 验证测试失败: {e}")
        
        def test_settings_save():
            """测试配置保存功能"""
            try:
                print("\\n测试配置保存功能...")
                
                # 备份当前配置
                backup_path = settings.create_backup()
                print(f"配置备份创建: {Path(backup_path).name}")
                
                # 保存配置
                success = settings.save_to_file()
                print(f"配置保存: {'成功' if success else '失败'}")
                
                # 清理备份
                Path(backup_path).unlink(missing_ok=True)
                
            except Exception as e:
                print(f"❌ 保存测试失败: {e}")
        
        # 创建测试按钮
        open_button = ttk.Button(
            button_frame, 
            text="打开设置对话框", 
            command=open_settings_dialog,
            width=20
        )
        open_button.pack(side=tk.LEFT, padx=(0, 10))
        
        validate_button = ttk.Button(
            button_frame, 
            text="测试配置验证", 
            command=test_settings_validation,
            width=15
        )
        validate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        save_button = ttk.Button(
            button_frame, 
            text="测试配置保存", 
            command=test_settings_save,
            width=15
        )
        save_button.pack(side=tk.LEFT)
        
        print("4. 预测试功能组件...")
        
        # 创建设置对话框实例进行预测试
        dialog = SettingsDialog(root, settings)
        
        # 测试配置收集
        dialog._create_dialog()
        dialog._create_ui()
        dialog._load_current_settings()
        
        collected = dialog._collect_settings()
        print(f"   ✅ 配置收集测试: {len(collected)}项配置")
        
        # 测试验证
        is_valid, errors = dialog._validate_all_settings()
        print(f"   ✅ 配置验证测试: {is_valid}, 错误: {len(errors)}")
        
        # 测试更改检测
        has_changes = dialog._has_unsaved_changes()
        print(f"   ✅ 更改检测测试: {has_changes}")
        
        # 关闭预测试对话框
        dialog.dialog.destroy()
        
        print("\\n" + "=" * 60)
        print("✅ 完整设置对话框功能测试准备完成！")
        print("💡 现在可以进行完整的功能测试")
        print("=" * 60)
        
        # 启动主窗口事件循环
        print("\\n🚀 启动完整功能测试界面...")
        print("   - 点击'打开设置对话框'测试完整功能")
        print("   - 点击'测试配置验证'测试验证机制")
        print("   - 点击'测试配置保存'测试保存功能")
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
    success = test_complete_settings()
    sys.exit(0 if success else 1)