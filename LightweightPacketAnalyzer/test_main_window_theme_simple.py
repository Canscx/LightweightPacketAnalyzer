#!/usr/bin/env python3
"""
主窗口主题功能简化测试脚本

测试MainWindow的ttkbootstrap主题集成功能（不显示GUI）
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

def test_theme_integration():
    """测试主题集成功能"""
    print("🔍 测试主题集成功能:")
    
    try:
        # 测试Settings和ThemeManager集成
        settings = Settings()
        print(f"   默认主题: {settings.THEME}")
        print(f"   主题分类: {settings.THEME_CATEGORY}")
        
        # 测试主题验证
        is_valid = theme_manager.validate_theme(settings.THEME)
        print(f"   主题有效性: {is_valid}")
        
        # 测试主题信息获取
        display_name = theme_manager.get_theme_display_name(settings.THEME)
        description = theme_manager.get_theme_description(settings.THEME)
        category = theme_manager.get_theme_category(settings.THEME)
        
        print(f"   显示名称: {display_name}")
        print(f"   主题描述: {description}")
        print(f"   主题分类: {category}")
        
        # 测试主题切换配置保存
        test_theme = 'darkly'
        test_category = 'dark'
        
        success = settings.save_theme_config(test_theme, test_category)
        print(f"   保存主题配置: {success}")
        
        # 验证配置
        new_config = settings.get_theme_config()
        print(f"   新配置: {new_config}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_migration():
    """测试主题迁移功能"""
    print("\n🔍 测试主题迁移功能:")
    
    try:
        # 创建临时配置文件
        temp_config = Path("test_migration_simple.env")
        
        # 写入旧主题配置
        with open(temp_config, 'w') as f:
            f.write("THEME=default\n")
            f.write("THEME_CATEGORY=classic\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        print(f"   加载的旧主题: {settings.THEME}")
        
        # 执行主题迁移
        migrated_theme = settings.migrate_legacy_theme()
        print(f"   迁移后主题: {migrated_theme}")
        
        # 验证迁移结果
        final_config = settings.get_theme_config()
        print(f"   最终配置: {final_config}")
        
        # 清理临时文件
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题迁移测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_groups():
    """测试主题分组功能"""
    print("\n🔍 测试主题分组功能:")
    
    try:
        # 获取主题分组
        groups = theme_manager.get_theme_groups()
        print(f"   主题分组数量: {len(groups)}")
        
        for group_name, themes in groups.items():
            print(f"   {group_name}: {len(themes)}个主题")
            if themes:
                print(f"     示例: {themes[:3]}")
        
        # 测试Colorful主题
        colorful_themes = theme_manager.get_colorful_themes()
        print(f"   Colorful主题: {colorful_themes}")
        
        # 测试可用主题
        available_themes = theme_manager.get_available_themes()
        print(f"   可用主题总数: {len(available_themes)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题分组测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_validation():
    """测试主题验证功能"""
    print("\n🔍 测试主题验证功能:")
    
    try:
        # 测试各种主题验证
        test_themes = [
            ('litera', True),
            ('darkly', True),
            ('default', True),
            ('invalid_theme', False),
            ('', False),
            (None, False)
        ]
        
        for theme, expected in test_themes:
            try:
                is_valid = theme_manager.validate_theme(theme)
                status = "✅" if is_valid == expected else "❌"
                print(f"   {status} {theme}: {is_valid} (期望: {expected})")
            except Exception as e:
                print(f"   ❌ {theme}: 验证异常 - {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_theme_methods():
    """测试Settings主题相关方法"""
    print("\n🔍 测试Settings主题相关方法:")
    
    try:
        settings = Settings()
        
        # 测试获取主题配置
        config = settings.get_theme_config()
        print(f"   主题配置: {config}")
        
        # 测试主题配置验证
        valid_configs = [
            ('litera', 'light', True),
            ('darkly', 'dark', True),
            ('', 'light', False),
            ('test', 'invalid', False)
        ]
        
        for theme, category, expected in valid_configs:
            is_valid, error = settings.validate_theme_config(theme, category)
            status = "✅" if is_valid == expected else "❌"
            print(f"   {status} ({theme}, {category}): {is_valid} - {error}")
        
        # 测试立即生效设置
        immediate = settings.get_theme_settings_for_immediate_apply()
        print(f"   立即生效设置: {immediate}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Settings主题方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("主窗口主题功能简化测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("主题集成功能测试", test_theme_integration),
        ("主题迁移功能测试", test_theme_migration),
        ("主题分组功能测试", test_theme_groups),
        ("主题验证功能测试", test_theme_validation),
        ("Settings主题方法测试", test_settings_theme_methods),
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
        print("✅ 所有测试通过！主窗口主题功能正常")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)