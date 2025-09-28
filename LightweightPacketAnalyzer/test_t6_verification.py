#!/usr/bin/env python3
"""
T6验证脚本 - 设置对话框集成验证

验证SettingsDialog成功集成ThemeSettingsTab
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

def verify_imports():
    """验证导入"""
    print("🔍 验证导入:")
    
    try:
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        from network_analyzer.gui.dialogs.theme_settings_tab import ThemeSettingsTab
        from network_analyzer.config.settings import Settings
        from network_analyzer.gui.theme_manager import theme_manager
        
        print("   ✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

def verify_settings_dialog_structure():
    """验证设置对话框结构"""
    print("\n🔍 验证设置对话框结构:")
    
    try:
        from network_analyzer.gui.dialogs.settings_dialog import SettingsDialog
        from network_analyzer.config.settings import Settings
        
        # 检查SettingsDialog类是否有主题相关方法
        has_create_theme_tab = hasattr(SettingsDialog, '_create_theme_tab')
        has_cleanup_resources = hasattr(SettingsDialog, '_cleanup_resources')
        
        print(f"   _create_theme_tab方法: {has_create_theme_tab}")
        print(f"   _cleanup_resources方法: {has_cleanup_resources}")
        
        # 检查导入
        import inspect
        source = inspect.getsource(SettingsDialog)
        has_theme_import = 'ThemeSettingsTab' in source
        
        print(f"   ThemeSettingsTab导入: {has_theme_import}")
        
        if has_create_theme_tab and has_cleanup_resources and has_theme_import:
            print("   ✅ 设置对话框结构验证通过")
            return True
        else:
            print("   ❌ 设置对话框结构验证失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 结构验证失败: {e}")
        return False

def verify_theme_integration():
    """验证主题集成"""
    print("\n🔍 验证主题集成:")
    
    try:
        from network_analyzer.config.settings import Settings
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 创建设置实例
        settings = Settings()
        
        # 验证主题配置
        theme_config = settings.get_theme_config()
        print(f"   当前主题配置: {theme_config}")
        
        # 验证主题管理器
        groups = theme_manager.get_theme_groups()
        print(f"   主题分组数量: {len(groups)}")
        
        # 验证主题验证
        current_theme = settings.THEME
        is_valid = theme_manager.validate_theme(current_theme)
        print(f"   当前主题 {current_theme} 有效性: {is_valid}")
        
        # 验证主题保存
        test_theme = 'litera'
        test_category = 'light'
        save_success = settings.save_theme_config(test_theme, test_category)
        print(f"   主题配置保存: {save_success}")
        
        if is_valid and save_success and len(groups) >= 4:
            print("   ✅ 主题集成验证通过")
            return True
        else:
            print("   ❌ 主题集成验证失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 主题集成验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_configuration_flow():
    """验证配置流程"""
    print("\n🔍 验证配置流程:")
    
    try:
        from network_analyzer.config.settings import Settings
        
        # 创建临时配置文件
        temp_config = Path("test_t6_config.env")
        
        # 写入测试配置
        with open(temp_config, 'w') as f:
            f.write("THEME=darkly\n")
            f.write("THEME_CATEGORY=dark\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        initial_config = settings.get_theme_config()
        print(f"   初始配置: {initial_config}")
        
        # 修改配置
        new_theme = 'flatly'
        new_category = 'light'
        success = settings.save_theme_config(new_theme, new_category)
        
        if success:
            # 验证配置更新
            updated_config = settings.get_theme_config()
            print(f"   更新后配置: {updated_config}")
            
            config_updated = (updated_config['theme'] == new_theme and 
                            updated_config['category'] == new_category)
            
            if config_updated:
                print("   ✅ 配置流程验证通过")
                result = True
            else:
                print("   ❌ 配置更新验证失败")
                result = False
        else:
            print("   ❌ 配置保存失败")
            result = False
        
        # 清理临时文件
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        return result
        
    except Exception as e:
        print(f"   ❌ 配置流程验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_theme_categories():
    """验证主题分类"""
    print("\n🔍 验证主题分类:")
    
    try:
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 验证4个主题分组
        groups = theme_manager.get_theme_groups()
        expected_groups = {'light', 'dark', 'colorful', 'classic'}
        actual_groups = set(groups.keys())
        
        print(f"   期望分组: {expected_groups}")
        print(f"   实际分组: {actual_groups}")
        
        groups_match = expected_groups == actual_groups
        
        # 验证每个分组都有主题
        all_groups_have_themes = all(len(themes) > 0 for themes in groups.values())
        
        print(f"   分组匹配: {groups_match}")
        print(f"   所有分组都有主题: {all_groups_have_themes}")
        
        # 验证Colorful主题
        colorful_themes = theme_manager.get_colorful_themes()
        print(f"   Colorful主题: {colorful_themes}")
        
        if groups_match and all_groups_have_themes and len(colorful_themes) > 0:
            print("   ✅ 主题分类验证通过")
            return True
        else:
            print("   ❌ 主题分类验证失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 主题分类验证失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("T6验证 - 设置对话框集成")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("导入验证", verify_imports),
        ("设置对话框结构验证", verify_settings_dialog_structure),
        ("主题集成验证", verify_theme_integration),
        ("配置流程验证", verify_configuration_flow),
        ("主题分类验证", verify_theme_categories),
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
    
    print("\n" + "=" * 60)
    print(f"验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ T6验证通过！设置对话框集成成功")
        print("\n🎉 主要成果:")
        print("   • SettingsDialog成功集成ThemeSettingsTab")
        print("   • 支持4个主题分组：浅色、暗色、Colorful、Windows经典")
        print("   • 主题配置变量正确初始化和管理")
        print("   • 主题切换和配置保存功能正常")
        print("   • 资源清理机制完善")
        return True
    else:
        print("❌ T6验证失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)