#!/usr/bin/env python3
"""
主题系统测试脚本

测试ThemeManager和Settings扩展的主题功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.gui.theme_manager import ThemeManager, ThemeValidator
from network_analyzer.config.settings import Settings

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_theme_validator():
    """测试主题验证器"""
    print("🔍 测试主题验证器:")
    
    validator = ThemeValidator()
    
    # 测试ttkbootstrap主题验证
    test_themes = ['litera', 'darkly', 'invalid_theme']
    for theme in test_themes:
        is_ttk = validator.is_ttkbootstrap_theme(theme)
        print(f"   {theme}: ttkbootstrap主题 = {is_ttk}")
    
    # 测试经典主题验证
    classic_themes = ['default', 'clam', 'alt', 'classic', 'invalid']
    for theme in classic_themes:
        is_classic = validator.is_tkinter_theme(theme)
        print(f"   {theme}: 经典主题 = {is_classic}")
    
    # 测试主题分类
    test_categories = ['litera', 'darkly', 'default', 'superhero']
    for theme in test_categories:
        category = validator.get_theme_category(theme)
        print(f"   {theme}: 分类 = {category}")
    
    return True

def test_theme_manager():
    """测试主题管理器"""
    print("\n🔍 测试主题管理器:")
    
    manager = ThemeManager()
    
    # 测试获取主题分组
    groups = manager.get_theme_groups()
    print(f"   主题分组数量: {len(groups)}")
    for group_name, themes in groups.items():
        print(f"   {group_name}: {len(themes)}个主题 - {themes[:3]}...")
    
    # 测试获取可用主题
    available = manager.get_available_themes()
    print(f"   可用主题总数: {len(available)}")
    
    # 测试Colorful主题
    colorful = manager.get_colorful_themes()
    print(f"   Colorful主题: {colorful}")
    
    # 测试主题验证
    test_themes = ['litera', 'darkly', 'default', 'invalid_theme']
    for theme in test_themes:
        is_valid = manager.validate_theme(theme)
        print(f"   {theme}: 有效 = {is_valid}")
    
    # 测试主题迁移
    old_themes = ['default', 'clam', 'alt', 'classic']
    for old_theme in old_themes:
        new_theme = manager.migrate_legacy_theme(old_theme)
        print(f"   迁移: {old_theme} -> {new_theme}")
    
    # 测试显示名称
    display_themes = ['litera', 'darkly', 'default']
    for theme in display_themes:
        display_name = manager.get_theme_display_name(theme)
        description = manager.get_theme_description(theme)
        print(f"   {theme}: {display_name} - {description}")
    
    return True

def test_settings_extension():
    """测试Settings类扩展"""
    print("\n🔍 测试Settings类扩展:")
    
    # 创建临时配置文件
    temp_config = Path("test_theme_config.env")
    
    try:
        settings = Settings(str(temp_config))
        
        # 测试默认主题配置
        theme_config = settings.get_theme_config()
        print(f"   默认主题配置: {theme_config}")
        
        # 测试主题配置验证
        valid_configs = [
            ('litera', 'light'),
            ('darkly', 'dark'),
            ('default', 'classic'),
            ('', 'light'),  # 无效
            ('test', 'invalid')  # 无效
        ]
        
        for theme, category in valid_configs:
            is_valid, error = settings.validate_theme_config(theme, category)
            print(f"   验证 ({theme}, {category}): {is_valid} - {error}")
        
        # 测试保存主题配置
        success = settings.save_theme_config('darkly', 'dark')
        print(f"   保存主题配置: {success}")
        
        # 验证配置是否保存成功
        new_config = settings.get_theme_config()
        print(f"   新主题配置: {new_config}")
        
        # 测试主题迁移
        settings.THEME = 'default'  # 设置旧主题
        migrated = settings.migrate_legacy_theme()
        print(f"   主题迁移结果: {migrated}")
        
        # 测试立即生效设置
        immediate = settings.get_theme_settings_for_immediate_apply()
        print(f"   立即生效设置: {immediate}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
        
    finally:
        # 清理临时文件
        if temp_config.exists():
            temp_config.unlink()

def test_integration():
    """测试集成功能"""
    print("\n🔍 测试集成功能:")
    
    try:
        manager = ThemeManager()
        settings = Settings()
        
        # 测试主题应用流程
        test_theme = 'litera'
        
        # 1. 验证主题
        if not manager.validate_theme(test_theme):
            print(f"   ❌ 主题 {test_theme} 无效")
            return False
        
        # 2. 获取主题分类
        category = manager.get_theme_category(test_theme)
        print(f"   主题分类: {test_theme} -> {category}")
        
        # 3. 保存配置
        success = settings.save_theme_config(test_theme, category)
        print(f"   配置保存: {success}")
        
        # 4. 验证配置
        config = settings.get_theme_config()
        print(f"   最终配置: {config}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 集成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("主题系统功能测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("主题验证器测试", test_theme_validator),
        ("主题管理器测试", test_theme_manager),
        ("Settings扩展测试", test_settings_extension),
        ("集成功能测试", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
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
        print("✅ 所有测试通过！主题系统功能正常")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)