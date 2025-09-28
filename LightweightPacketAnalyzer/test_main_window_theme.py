#!/usr/bin/env python3
"""
主窗口主题功能测试脚本

测试MainWindow的ttkbootstrap主题集成功能
"""

import sys
import os
import logging
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.config.settings import Settings
from network_analyzer.gui.main_window import MainWindow

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_main_window_creation():
    """测试主窗口创建"""
    print("🔍 测试主窗口创建:")
    
    try:
        # 创建设置实例
        settings = Settings()
        print(f"   当前主题配置: {settings.THEME}")
        
        # 创建主窗口
        main_window = MainWindow(settings)
        print("   ✅ 主窗口创建成功")
        
        # 检查窗口类型
        window_type = type(main_window.root).__name__
        print(f"   窗口类型: {window_type}")
        
        # 获取当前主题信息
        theme_info = main_window.get_current_theme_info()
        print(f"   当前主题信息: {theme_info}")
        
        # 测试主题切换
        test_themes = ['darkly', 'flatly', 'litera']
        for theme in test_themes:
            print(f"   测试切换到主题: {theme}")
            main_window.apply_theme(theme)
            time.sleep(0.5)  # 短暂延迟以观察效果
        
        # 显示窗口一段时间
        print("   显示窗口3秒...")
        main_window.root.after(3000, main_window.root.quit)  # 3秒后关闭
        main_window.root.mainloop()
        
        print("   ✅ 主窗口测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主窗口创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_switching():
    """测试主题切换功能"""
    print("\n🔍 测试主题切换功能:")
    
    try:
        settings = Settings()
        main_window = MainWindow(settings)
        
        # 测试各种主题切换
        test_themes = [
            ('litera', 'light'),
            ('darkly', 'dark'),
            ('flatly', 'light'),
            ('superhero', 'dark'),
            ('default', 'classic'),  # 经典主题
            ('invalid_theme', 'unknown')  # 无效主题
        ]
        
        for theme, expected_category in test_themes:
            print(f"   测试主题: {theme}")
            
            # 应用主题
            main_window.apply_theme(theme)
            
            # 检查主题信息
            theme_info = main_window.get_current_theme_info()
            actual_theme = theme_info['theme']
            actual_category = theme_info['category']
            
            if theme == 'invalid_theme':
                # 无效主题应该回退到默认主题
                print(f"     无效主题已回退到: {actual_theme}")
            else:
                print(f"     主题: {actual_theme}, 分类: {actual_category}")
                print(f"     显示名: {theme_info['display_name']}")
        
        # 关闭窗口
        main_window.root.destroy()
        
        print("   ✅ 主题切换测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题切换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_migration():
    """测试主题迁移功能"""
    print("\n🔍 测试主题迁移功能:")
    
    try:
        # 创建临时配置文件
        temp_config = Path("test_migration.env")
        
        # 写入旧主题配置
        with open(temp_config, 'w') as f:
            f.write("THEME=default\n")
            f.write("WINDOW_WIDTH=1200\n")
            f.write("WINDOW_HEIGHT=800\n")
        
        # 加载配置
        settings = Settings(str(temp_config))
        print(f"   加载的旧主题: {settings.THEME}")
        
        # 创建主窗口（应该触发主题迁移）
        main_window = MainWindow(settings)
        
        # 检查迁移后的主题
        theme_info = main_window.get_current_theme_info()
        print(f"   迁移后主题: {theme_info['theme']}")
        print(f"   主题分类: {theme_info['category']}")
        
        # 关闭窗口
        main_window.root.destroy()
        
        # 清理临时文件
        temp_config.unlink()
        
        print("   ✅ 主题迁移测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主题迁移测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_integration():
    """测试设置集成功能"""
    print("\n🔍 测试设置集成功能:")
    
    try:
        settings = Settings()
        main_window = MainWindow(settings)
        
        # 测试重新加载设置
        print("   测试重新加载设置...")
        main_window.reload_settings()
        
        # 测试重新加载主题设置
        print("   测试重新加载主题设置...")
        main_window.reload_theme_settings()
        
        # 测试立即生效设置
        print("   测试立即生效设置...")
        main_window._apply_immediate_settings()
        
        # 获取最终主题信息
        theme_info = main_window.get_current_theme_info()
        print(f"   最终主题信息: {theme_info}")
        
        # 关闭窗口
        main_window.root.destroy()
        
        print("   ✅ 设置集成测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 设置集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("主窗口主题功能测试")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("主窗口创建测试", test_main_window_creation),
        ("主题切换功能测试", test_theme_switching),
        ("主题迁移功能测试", test_theme_migration),
        ("设置集成功能测试", test_settings_integration),
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
        print("✅ 所有测试通过！主窗口主题功能正常")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)