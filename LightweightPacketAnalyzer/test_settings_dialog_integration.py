#!/usr/bin/env python3
"""
设置对话框集成测试脚本

测试SettingsDialog与ThemeSettingsTab的集成功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.config.settings import Settings
from network_analyzer.gui.theme_manager import theme_manager

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_settings_dialog_structure():
    """测试设置对话框结构"""
    print("🔍 测试设置对话框结构:")
    
    try:
        # 导入测试
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        from network_analyzer.gui.dialogs.theme_settings_tab import ThemeSettingsTab
        
        print("   ✅ 导入成功")
        
        # 检查SettingsDialog是否有主题相关属性
        settings = Settings()
        
        # 模拟创建对话框（不显示）
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建设置对话框实例
        dialog = SettingsDialog(root, settings)
        
        # 创建对话框和UI（但不显示）
        dialog._create_dialog()
        dialog._create_ui()
        
        # 检查是否有主题选项卡相关属性
        has_theme_tab = hasattr(dialog, 'theme_tab')
        print(f"   主题选项卡属性: {has_theme_tab}")
        
        # 检查配置变量
        has_theme_vars = 'THEME' in dialog.config_vars and 'THEME_CATEGORY' in dialog.config_vars
        print(f"   主题配置变量: {has_theme_vars}")
        
        # 清理
        root.destroy()
        
        if has_theme_tab and has_theme_vars:
            print("   ✅ 设置对话框结构正确")
            return True
        else:
            print("   ❌ 设置对话框结构不完整")
            return False
        
    except Exception as e:
        print(f"   ❌ 设置对话框结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_config_integration():
    """测试主题配置集成"""
    print("\n🔍 测试主题配置集成:")
    
    try:
        # 创建临时配置文件
        temp_config = Path("test_dialog_integration.env")
        
        # 写入测试配置
        with open(temp_config, 'w') as f:
            f.write("THEME=litera\n")
            f.write("THEME_CATEGORY=light\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        print(f"   加载的配置: {settings.get_theme_config()}")
        
        # 测试配置变量初始化
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(root, settings)
        
        # 创建对话框和UI
        dialog._create_dialog()
        dialog._create_ui()
        
        # 检查配置变量值
        theme_var_value = dialog.config_vars['THEME'].get()
        category_var_value = dialog.config_vars['THEME_CATEGORY'].get()
        
        print(f"   主题变量值: {theme_var_value}")
        print(f"   分类变量值: {category_var_value}")
        
        # 验证值是否正确
        config_correct = (theme_var_value == settings.THEME and 
                         category_var_value == settings.THEME_CATEGORY)
        
        if config_correct:
            print("   ✅ 主题配置集成正确")
        else:
            print("   ❌ 主题配置集成错误")
        
        # 清理
        root.destroy()
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        return config_correct
        
    except Exception as e:
        print(f"   ❌ 主题配置集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_validation_integration():
    """测试主题验证集成"""
    print("\n🔍 测试主题验证集成:")
    
    try:
        settings = Settings()
        
        # 测试主题管理器与设置的集成
        current_theme = settings.THEME
        is_valid = theme_manager.validate_theme(current_theme)
        category = theme_manager.get_theme_category(current_theme)
        
        print(f"   当前主题: {current_theme}")
        print(f"   主题有效性: {is_valid}")
        print(f"   主题分类: {category}")
        
        # 测试主题分组
        groups = theme_manager.get_theme_groups()
        print(f"   主题分组数量: {len(groups)}")
        
        # 验证当前主题在分组中
        theme_in_groups = False
        for group_name, themes in groups.items():
            if current_theme in themes:
                theme_in_groups = True
                print(f"   当前主题在分组: {group_name}")
                break
        
        if not theme_in_groups and theme_manager.validator.is_tkinter_theme(current_theme):
            print(f"   当前主题是经典主题: {current_theme}")
            theme_in_groups = True
        
        # 测试主题切换配置
        test_themes = ['darkly', 'flatly', 'default']
        for theme in test_themes:
            if theme_manager.validate_theme(theme):
                test_category = theme_manager.get_theme_category(theme)
                success = settings.save_theme_config(theme, test_category)
                if success:
                    print(f"   ✅ 主题配置保存成功: {theme}")
                else:
                    print(f"   ❌ 主题配置保存失败: {theme}")
        
        if is_valid and theme_in_groups:
            print("   ✅ 主题验证集成正确")
            return True
        else:
            print("   ❌ 主题验证集成错误")
            return False
        
    except Exception as e:
        print(f"   ❌ 主题验证集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_collection():
    """测试设置收集功能"""
    print("\n🔍 测试设置收集功能:")
    
    try:
        settings = Settings()
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(root, settings)
        
        # 创建对话框和UI
        dialog._create_dialog()
        dialog._create_ui()
        
        # 修改主题配置变量
        test_theme = 'darkly'
        test_category = 'dark'
        
        dialog.config_vars['THEME'].set(test_theme)
        dialog.config_vars['THEME_CATEGORY'].set(test_category)
        
        # 收集设置
        collected = dialog._collect_settings()
        
        print(f"   收集的主题: {collected.get('THEME')}")
        print(f"   收集的分类: {collected.get('THEME_CATEGORY')}")
        
        # 验证收集结果
        collection_correct = (collected.get('THEME') == test_theme and 
                            collected.get('THEME_CATEGORY') == test_category)
        
        if collection_correct:
            print("   ✅ 设置收集功能正确")
        else:
            print("   ❌ 设置收集功能错误")
        
        # 清理
        root.destroy()
        
        return collection_correct
        
    except Exception as e:
        print(f"   ❌ 设置收集功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cleanup_functionality():
    """测试清理功能"""
    print("\n🔍 测试清理功能:")
    
    try:
        settings = Settings()
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(root, settings)
        
        # 创建对话框和UI
        dialog._create_dialog()
        dialog._create_ui()
        
        # 检查是否有清理方法
        has_cleanup = hasattr(dialog, '_cleanup_resources')
        print(f"   清理方法存在: {has_cleanup}")
        
        # 检查是否有主题选项卡实例
        has_theme_tab_instance = hasattr(dialog, 'theme_settings_tab')
        print(f"   主题选项卡实例: {has_theme_tab_instance}")
        
        # 测试清理方法
        if has_cleanup:
            try:
                dialog._cleanup_resources()
                print("   ✅ 清理方法执行成功")
                cleanup_success = True
            except Exception as e:
                print(f"   ❌ 清理方法执行失败: {e}")
                cleanup_success = False
        else:
            cleanup_success = False
        
        # 清理
        root.destroy()
        
        return has_cleanup and cleanup_success
        
    except Exception as e:
        print(f"   ❌ 清理功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("设置对话框集成测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("设置对话框结构测试", test_settings_dialog_structure),
        ("主题配置集成测试", test_theme_config_integration),
        ("主题验证集成测试", test_theme_validation_integration),
        ("设置收集功能测试", test_settings_collection),
        ("清理功能测试", test_cleanup_functionality),
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
        print("✅ 所有测试通过！设置对话框集成功能正常")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)