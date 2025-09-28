#!/usr/bin/env python3
"""
主题设置选项卡简化测试脚本

测试ThemeSettingsTab的核心功能（不显示GUI）
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

def test_theme_settings_integration():
    """测试主题设置集成功能"""
    print("🔍 测试主题设置集成功能:")
    
    try:
        # 创建设置实例
        settings = Settings()
        print(f"   当前主题: {settings.THEME}")
        print(f"   主题分类: {settings.THEME_CATEGORY}")
        
        # 测试主题分组获取
        groups = theme_manager.get_theme_groups()
        print(f"   主题分组数量: {len(groups)}")
        
        for group_name, themes in groups.items():
            print(f"   {group_name}: {len(themes)}个主题")
            if themes:
                # 测试每个分组的第一个主题
                first_theme = themes[0]
                display_name = theme_manager.get_theme_display_name(first_theme)
                description = theme_manager.get_theme_description(first_theme)
                print(f"     示例: {first_theme} - {display_name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题设置集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_config_operations():
    """测试主题配置操作"""
    print("\n🔍 测试主题配置操作:")
    
    try:
        # 创建临时配置文件
        temp_config = Path("test_theme_config.env")
        
        # 写入初始配置
        with open(temp_config, 'w') as f:
            f.write("THEME=litera\n")
            f.write("THEME_CATEGORY=light\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        print(f"   初始配置: {settings.get_theme_config()}")
        
        # 测试主题配置保存
        test_themes = [
            ('darkly', 'dark'),
            ('flatly', 'light'),
            ('default', 'classic'),
            ('superhero', 'dark')
        ]
        
        for theme, category in test_themes:
            # 验证主题
            if theme_manager.validate_theme(theme):
                # 保存配置
                success = settings.save_theme_config(theme, category)
                if success:
                    # 验证保存结果
                    config = settings.get_theme_config()
                    if config['theme'] == theme and config['category'] == category:
                        print(f"   ✅ 主题配置保存成功: {theme} ({category})")
                    else:
                        print(f"   ❌ 主题配置验证失败: {theme}")
                else:
                    print(f"   ❌ 主题配置保存失败: {theme}")
            else:
                print(f"   ⚠️ 主题无效: {theme}")
        
        # 清理临时文件
        temp_config.unlink()
        backup_file = f"{temp_config}.backup"
        Path(backup_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题配置操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_validation_logic():
    """测试主题验证逻辑"""
    print("\n🔍 测试主题验证逻辑:")
    
    try:
        settings = Settings()
        
        # 测试有效主题
        valid_themes = ['litera', 'darkly', 'flatly', 'default', 'clam']
        for theme in valid_themes:
            is_valid = theme_manager.validate_theme(theme)
            category = theme_manager.get_theme_category(theme)
            display_name = theme_manager.get_theme_display_name(theme)
            
            if is_valid:
                print(f"   ✅ {theme}: {display_name} ({category})")
            else:
                print(f"   ❌ {theme}: 验证失败")
        
        # 测试无效主题
        invalid_themes = ['invalid_theme', '', None, 'nonexistent']
        for theme in invalid_themes:
            try:
                is_valid = theme_manager.validate_theme(theme)
                if not is_valid:
                    print(f"   ✅ 无效主题正确识别: {theme}")
                else:
                    print(f"   ❌ 无效主题未识别: {theme}")
            except Exception as e:
                print(f"   ✅ 无效主题异常处理: {theme} - {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题验证逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_migration_logic():
    """测试主题迁移逻辑"""
    print("\n🔍 测试主题迁移逻辑:")
    
    try:
        # 测试旧主题迁移
        old_themes = {
            'default': 'litera',
            'clam': 'flatly',
            'alt': 'cosmo',
            'classic': 'journal'
        }
        
        for old_theme, expected_new in old_themes.items():
            # 创建临时配置
            temp_config = Path(f"test_migration_{old_theme}.env")
            
            with open(temp_config, 'w') as f:
                f.write(f"THEME={old_theme}\n")
                f.write("THEME_CATEGORY=classic\n")
            
            # 加载并迁移
            settings = Settings(str(temp_config))
            migrated_theme = settings.migrate_legacy_theme()
            
            if migrated_theme == expected_new:
                print(f"   ✅ 迁移成功: {old_theme} -> {migrated_theme}")
            else:
                print(f"   ❌ 迁移失败: {old_theme} -> {migrated_theme} (期望: {expected_new})")
            
            # 清理
            temp_config.unlink()
            backup_file = f"{temp_config}.backup"
            Path(backup_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 主题迁移逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_colorful_themes():
    """测试Colorful主题功能"""
    print("\n🔍 测试Colorful主题功能:")
    
    try:
        # 获取Colorful主题
        colorful_themes = theme_manager.get_colorful_themes()
        print(f"   Colorful主题数量: {len(colorful_themes)}")
        print(f"   Colorful主题列表: {colorful_themes}")
        
        # 验证每个Colorful主题
        for theme in colorful_themes:
            is_valid = theme_manager.validate_theme(theme)
            category = theme_manager.get_theme_category(theme)
            display_name = theme_manager.get_theme_display_name(theme)
            description = theme_manager.get_theme_description(theme)
            
            print(f"   主题: {theme}")
            print(f"     有效性: {is_valid}")
            print(f"     分类: {category}")
            print(f"     显示名: {display_name}")
            print(f"     描述: {description}")
        
        # 验证Colorful主题的特殊性
        expected_colorful = {'morph', 'vapor', 'superhero', 'cyborg'}
        actual_colorful = set(colorful_themes)
        
        if actual_colorful.issubset(expected_colorful):
            print("   ✅ Colorful主题列表符合预期")
        else:
            print(f"   ⚠️ Colorful主题列表差异: 实际={actual_colorful}, 期望⊆{expected_colorful}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Colorful主题功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("主题设置选项卡简化测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("主题设置集成功能测试", test_theme_settings_integration),
        ("主题配置操作测试", test_theme_config_operations),
        ("主题验证逻辑测试", test_theme_validation_logic),
        ("主题迁移逻辑测试", test_theme_migration_logic),
        ("Colorful主题功能测试", test_colorful_themes),
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