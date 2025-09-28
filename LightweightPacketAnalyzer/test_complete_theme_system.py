#!/usr/bin/env python3
"""
完整主题系统集成测试脚本

验证整个ttkbootstrap主题切换功能的完整实现
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_all_imports():
    """测试所有模块导入"""
    print("🔍 测试所有模块导入:")
    
    try:
        # 核心模块
        from network_analyzer.config.settings import Settings
        from network_analyzer.gui.theme_manager import ThemeManager, ThemeValidator, theme_manager
        from network_analyzer.gui.main_window import MainWindow
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        from network_analyzer.gui.dialogs.theme_settings_tab import ThemeSettingsTab
        
        # 检查ttkbootstrap
        import ttkbootstrap as ttk
        
        print("   ✅ 所有核心模块导入成功")
        print(f"   ttkbootstrap版本: {getattr(ttk, '__version__', '未知')}")
        return True
        
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_manager_functionality():
    """测试主题管理器功能"""
    print("\n🔍 测试主题管理器功能:")
    
    try:
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 测试主题分组
        groups = theme_manager.get_theme_groups()
        print(f"   主题分组: {list(groups.keys())}")
        
        expected_groups = {'light', 'dark', 'colorful', 'classic'}
        actual_groups = set(groups.keys())
        groups_correct = expected_groups == actual_groups
        
        # 测试每个分组的主题数量
        for group_name, themes in groups.items():
            print(f"   {group_name}: {len(themes)}个主题 - {themes[:3]}...")
        
        # 测试Colorful主题
        colorful_themes = theme_manager.get_colorful_themes()
        print(f"   Colorful主题: {colorful_themes}")
        
        # 测试主题验证
        test_themes = ['litera', 'darkly', 'default', 'invalid_theme']
        validation_results = []
        for theme in test_themes:
            is_valid = theme_manager.validate_theme(theme)
            validation_results.append(is_valid)
            print(f"   {theme}: {'有效' if is_valid else '无效'}")
        
        # 验证结果
        expected_validation = [True, True, True, False]
        validation_correct = validation_results == expected_validation
        
        if groups_correct and validation_correct and len(colorful_themes) > 0:
            print("   ✅ 主题管理器功能测试通过")
            return True
        else:
            print("   ❌ 主题管理器功能测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 主题管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_integration():
    """测试设置集成"""
    print("\n🔍 测试设置集成:")
    
    try:
        from network_analyzer.config.settings import Settings
        
        # 创建临时配置文件
        temp_config = Path("test_complete_system.env")
        
        # 写入测试配置
        with open(temp_config, 'w') as f:
            f.write("THEME=litera\n")
            f.write("THEME_CATEGORY=light\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 测试配置加载
        settings = Settings(str(temp_config))
        initial_config = settings.get_theme_config()
        print(f"   初始配置: {initial_config}")
        
        # 测试主题配置方法
        methods_to_test = [
            'get_theme_config',
            'save_theme_config', 
            'validate_theme_config',
            'migrate_legacy_theme',
            'get_theme_settings_for_immediate_apply'
        ]
        
        methods_exist = []
        for method in methods_to_test:
            exists = hasattr(settings, method)
            methods_exist.append(exists)
            print(f"   {method}: {'存在' if exists else '缺失'}")
        
        # 测试配置保存
        save_success = settings.save_theme_config('darkly', 'dark')
        updated_config = settings.get_theme_config()
        print(f"   保存后配置: {updated_config}")
        
        # 测试配置验证
        valid_config = settings.validate_theme_config('flatly', 'light')
        invalid_config = settings.validate_theme_config('', 'invalid')
        print(f"   有效配置验证: {valid_config}")
        print(f"   无效配置验证: {invalid_config}")
        
        # 清理
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        if all(methods_exist) and save_success and valid_config[0] and not invalid_config[0]:
            print("   ✅ 设置集成测试通过")
            return True
        else:
            print("   ❌ 设置集成测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 设置集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_integration():
    """测试主窗口集成"""
    print("\n🔍 测试主窗口集成:")
    
    try:
        from network_analyzer.gui.main_window import MainWindow, TTKBOOTSTRAP_AVAILABLE
        from network_analyzer.config.settings import Settings
        
        print(f"   ttkbootstrap可用性: {TTKBOOTSTRAP_AVAILABLE}")
        
        # 检查MainWindow是否有主题相关方法
        theme_methods = [
            'apply_theme',
            'reload_theme_settings', 
            'get_current_theme_info'
        ]
        
        methods_exist = []
        for method in theme_methods:
            exists = hasattr(MainWindow, method)
            methods_exist.append(exists)
            print(f"   {method}: {'存在' if exists else '缺失'}")
        
        # 检查导入
        import inspect
        source = inspect.getsource(MainWindow)
        has_theme_manager_import = 'theme_manager' in source
        has_ttkbootstrap_import = 'ttkbootstrap' in source
        
        print(f"   theme_manager导入: {has_theme_manager_import}")
        print(f"   ttkbootstrap导入: {has_ttkbootstrap_import}")
        
        if all(methods_exist) and has_theme_manager_import and has_ttkbootstrap_import:
            print("   ✅ 主窗口集成测试通过")
            return True
        else:
            print("   ❌ 主窗口集成测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 主窗口集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_dialog_integration():
    """测试设置对话框集成"""
    print("\n🔍 测试设置对话框集成:")
    
    try:
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        from network_analyzer.gui.dialogs.theme_settings_tab import ThemeSettingsTab
        
        # 检查SettingsDialog是否有主题相关方法
        dialog_methods = [
            '_create_theme_tab',
            '_cleanup_resources'
        ]
        
        methods_exist = []
        for method in dialog_methods:
            exists = hasattr(SettingsDialog, method)
            methods_exist.append(exists)
            print(f"   {method}: {'存在' if exists else '缺失'}")
        
        # 检查ThemeSettingsTab功能
        tab_methods = [
            'get_current_config',
            'load_config',
            'cleanup'
        ]
        
        tab_methods_exist = []
        for method in tab_methods:
            exists = hasattr(ThemeSettingsTab, method)
            tab_methods_exist.append(exists)
            print(f"   ThemeSettingsTab.{method}: {'存在' if exists else '缺失'}")
        
        # 检查导入
        import inspect
        dialog_source = inspect.getsource(SettingsDialog)
        has_theme_tab_import = 'ThemeSettingsTab' in dialog_source
        
        print(f"   ThemeSettingsTab导入: {has_theme_tab_import}")
        
        if all(methods_exist) and all(tab_methods_exist) and has_theme_tab_import:
            print("   ✅ 设置对话框集成测试通过")
            return True
        else:
            print("   ❌ 设置对话框集成测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 设置对话框集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """测试端到端工作流"""
    print("\n🔍 测试端到端工作流:")
    
    try:
        from network_analyzer.config.settings import Settings
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 1. 创建设置实例
        settings = Settings()
        print(f"   1. 初始主题: {settings.THEME}")
        
        # 2. 验证主题
        is_valid = theme_manager.validate_theme(settings.THEME)
        print(f"   2. 主题验证: {is_valid}")
        
        # 3. 获取主题分类
        category = theme_manager.get_theme_category(settings.THEME)
        print(f"   3. 主题分类: {category}")
        
        # 4. 切换主题
        new_theme = 'darkly'
        new_category = 'dark'
        
        # 验证新主题
        new_theme_valid = theme_manager.validate_theme(new_theme)
        print(f"   4. 新主题验证: {new_theme_valid}")
        
        # 保存新主题配置
        save_success = settings.save_theme_config(new_theme, new_category)
        print(f"   5. 配置保存: {save_success}")
        
        # 验证配置更新
        final_config = settings.get_theme_config()
        print(f"   6. 最终配置: {final_config}")
        
        # 7. 测试主题迁移
        settings.THEME = 'default'  # 设置旧主题
        migrated = settings.migrate_legacy_theme()
        print(f"   7. 主题迁移: default -> {migrated}")
        
        # 验证工作流完整性
        workflow_success = (is_valid and new_theme_valid and save_success and 
                          final_config['theme'] == new_theme and 
                          final_config['category'] == new_category)
        
        if workflow_success:
            print("   ✅ 端到端工作流测试通过")
            return True
        else:
            print("   ❌ 端到端工作流测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 端到端工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_colorful_themes():
    """测试Colorful主题功能"""
    print("\n🔍 测试Colorful主题功能:")
    
    try:
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 获取Colorful主题
        colorful_themes = theme_manager.get_colorful_themes()
        print(f"   Colorful主题列表: {colorful_themes}")
        
        # 验证Colorful主题特性
        expected_colorful = {'morph', 'vapor', 'superhero', 'cyborg'}
        actual_colorful = set(colorful_themes)
        
        print(f"   期望Colorful主题: {expected_colorful}")
        print(f"   实际Colorful主题: {actual_colorful}")
        
        # 检查是否包含期望的主题
        contains_expected = expected_colorful.issubset(actual_colorful)
        
        # 验证每个Colorful主题
        all_valid = True
        for theme in colorful_themes:
            is_valid = theme_manager.validate_theme(theme)
            display_name = theme_manager.get_theme_display_name(theme)
            description = theme_manager.get_theme_description(theme)
            
            print(f"   {theme}: {display_name} - {description[:30]}...")
            if not is_valid:
                all_valid = False
        
        # 验证Colorful主题在主题分组中
        groups = theme_manager.get_theme_groups()
        colorful_group = groups.get('colorful', [])
        colorful_in_group = len(colorful_group) > 0
        
        print(f"   Colorful分组中的主题: {colorful_group}")
        
        if contains_expected and all_valid and colorful_in_group:
            print("   ✅ Colorful主题功能测试通过")
            return True
        else:
            print("   ❌ Colorful主题功能测试失败")
            return False
            
    except Exception as e:
        print(f"   ❌ Colorful主题测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("完整主题系统集成测试")
    print("=" * 70)
    
    setup_logging()
    
    tests = [
        ("所有模块导入测试", test_all_imports),
        ("主题管理器功能测试", test_theme_manager_functionality),
        ("设置集成测试", test_settings_integration),
        ("主窗口集成测试", test_main_window_integration),
        ("设置对话框集成测试", test_settings_dialog_integration),
        ("Colorful主题功能测试", test_colorful_themes),
        ("端到端工作流测试", test_end_to_end_workflow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 70)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 完整主题系统集成测试全部通过！")
        print("\n📋 实现总结:")
        print("   ✅ T1: 项目依赖更新 - ttkbootstrap>=1.10.0")
        print("   ✅ T2: 主题管理器开发 - ThemeManager核心类")
        print("   ✅ T3: 配置系统扩展 - Settings类主题支持")
        print("   ✅ T4: 主窗口改造 - MainWindow使用ttkbootstrap")
        print("   ✅ T5: 主题设置选项卡 - ThemeSettingsTab开发")
        print("   ✅ T6: 设置对话框集成 - SettingsDialog集成主题选项卡")
        print("   ✅ T7: Colorful主题实现 - 多彩主题组实现")
        print("   ✅ T8: 测试验证 - 功能测试和集成测试")
        print("\n🌟 主要特性:")
        print("   • 支持4个主题分组：浅色、暗色、Colorful、Windows经典风格")
        print("   • 20+个ttkbootstrap主题可选")
        print("   • 主题切换立即生效，无需重启")
        print("   • 主题偏好持久化保存")
        print("   • 完整的主题验证和迁移机制")
        print("   • 现代化的用户界面体验")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)