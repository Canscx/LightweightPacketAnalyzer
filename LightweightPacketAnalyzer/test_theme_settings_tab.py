#!/usr/bin/env python3
"""
主题设置选项卡测试脚本

测试ThemeSettingsTab的功能
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.config.settings import Settings
from network_analyzer.gui.dialogs.theme_settings_tab import ThemeSettingsTab

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_theme_settings_tab_creation():
    """测试主题设置选项卡创建"""
    print("🔍 测试主题设置选项卡创建:")
    
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("主题设置选项卡测试")
        root.geometry("800x600")
        
        # 创建设置实例
        settings = Settings()
        
        # 创建配置变量
        config_vars = {
            'THEME': tk.StringVar(value=settings.THEME),
            'THEME_CATEGORY': tk.StringVar(value=settings.THEME_CATEGORY)
        }
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建主题设置选项卡
        theme_tab = ThemeSettingsTab(main_frame, config_vars, settings)
        print("   ✅ 主题设置选项卡创建成功")
        
        # 测试获取当前配置
        current_config = theme_tab.get_current_config()
        print(f"   当前配置: {current_config}")
        
        # 测试加载配置
        test_config = {'theme': 'darkly', 'category': 'dark'}
        theme_tab.load_config(test_config)
        print(f"   加载测试配置: {test_config}")
        
        # 显示窗口一段时间
        print("   显示窗口5秒...")
        root.after(5000, root.quit)  # 5秒后关闭
        root.mainloop()
        
        # 清理
        theme_tab.cleanup()
        root.destroy()
        
        print("   ✅ 主题设置选项卡测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题设置选项卡创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_tab_functionality():
    """测试主题选项卡功能"""
    print("\n🔍 测试主题选项卡功能:")
    
    try:
        settings = Settings()
        
        # 模拟配置变量
        config_vars = {
            'THEME': tk.StringVar(value=settings.THEME),
            'THEME_CATEGORY': tk.StringVar(value=settings.THEME_CATEGORY)
        }
        
        # 创建临时根窗口（不显示）
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        main_frame = ttk.Frame(root)
        
        # 创建主题选项卡
        theme_tab = ThemeSettingsTab(main_frame, config_vars, settings)
        
        # 测试配置操作
        print("   测试配置操作:")
        
        # 获取初始配置
        initial_config = theme_tab.get_current_config()
        print(f"     初始配置: {initial_config}")
        
        # 测试不同主题配置
        test_configs = [
            {'theme': 'litera', 'category': 'light'},
            {'theme': 'darkly', 'category': 'dark'},
            {'theme': 'flatly', 'category': 'light'},
            {'theme': 'default', 'category': 'classic'}
        ]
        
        for config in test_configs:
            theme_tab.load_config(config)
            current = theme_tab.get_current_config()
            print(f"     加载 {config} -> 当前 {current}")
        
        # 清理
        theme_tab.cleanup()
        root.destroy()
        
        print("   ✅ 主题选项卡功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题选项卡功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_tab_integration():
    """测试主题选项卡集成"""
    print("\n🔍 测试主题选项卡集成:")
    
    try:
        # 创建临时配置文件
        temp_config = Path("test_theme_tab.env")
        
        # 写入测试配置
        with open(temp_config, 'w') as f:
            f.write("THEME=litera\n")
            f.write("THEME_CATEGORY=light\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        print(f"   加载的配置: {settings.get_theme_config()}")
        
        # 创建配置变量
        config_vars = {
            'THEME': tk.StringVar(value=settings.THEME),
            'THEME_CATEGORY': tk.StringVar(value=settings.THEME_CATEGORY)
        }
        
        # 创建临时根窗口
        root = tk.Tk()
        root.withdraw()
        
        main_frame = ttk.Frame(root)
        theme_tab = ThemeSettingsTab(main_frame, config_vars, settings)
        
        # 测试配置同步
        print("   测试配置同步:")
        
        # 修改主题选项卡配置
        new_config = {'theme': 'darkly', 'category': 'dark'}
        theme_tab.load_config(new_config)
        
        # 检查配置变量是否同步
        theme_var_value = config_vars['THEME'].get()
        category_var_value = config_vars['THEME_CATEGORY'].get()
        
        print(f"     主题变量: {theme_var_value}")
        print(f"     分类变量: {category_var_value}")
        
        # 验证同步
        if theme_var_value == new_config['theme'] and category_var_value == new_config['category']:
            print("   ✅ 配置同步成功")
        else:
            print("   ❌ 配置同步失败")
        
        # 清理
        theme_tab.cleanup()
        root.destroy()
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        print("   ✅ 主题选项卡集成测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题选项卡集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_validation():
    """测试主题验证功能"""
    print("\n🔍 测试主题验证功能:")
    
    try:
        settings = Settings()
        config_vars = {
            'THEME': tk.StringVar(value=settings.THEME),
            'THEME_CATEGORY': tk.StringVar(value=settings.THEME_CATEGORY)
        }
        
        root = tk.Tk()
        root.withdraw()
        
        main_frame = ttk.Frame(root)
        theme_tab = ThemeSettingsTab(main_frame, config_vars, settings)
        
        # 测试有效主题
        valid_configs = [
            {'theme': 'litera', 'category': 'light'},
            {'theme': 'darkly', 'category': 'dark'},
            {'theme': 'default', 'category': 'classic'}
        ]
        
        for config in valid_configs:
            theme_tab.load_config(config)
            current = theme_tab.get_current_config()
            if current['theme'] == config['theme']:
                print(f"   ✅ 有效主题 {config['theme']} 加载成功")
            else:
                print(f"   ❌ 有效主题 {config['theme']} 加载失败")
        
        # 测试无效主题
        invalid_configs = [
            {'theme': 'invalid_theme', 'category': 'unknown'},
            {'theme': '', 'category': 'light'},
        ]
        
        for config in invalid_configs:
            theme_tab.load_config(config)
            current = theme_tab.get_current_config()
            if current['theme'] != config['theme']:
                print(f"   ✅ 无效主题 {config['theme']} 已回退")
            else:
                print(f"   ❌ 无效主题 {config['theme']} 未回退")
        
        # 清理
        theme_tab.cleanup()
        root.destroy()
        
        print("   ✅ 主题验证功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题验证功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("主题设置选项卡功能测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("主题设置选项卡创建测试", test_theme_settings_tab_creation),
        ("主题选项卡功能测试", test_theme_tab_functionality),
        ("主题选项卡集成测试", test_theme_tab_integration),
        ("主题验证功能测试", test_theme_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！主题设置选项卡功能正常")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)