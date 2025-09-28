#!/usr/bin/env python3
"""
ttkbootstrap安装验证脚本

验证ttkbootstrap库是否正确安装并可以正常使用
"""

import sys
import logging

def test_ttkbootstrap_import():
    """测试ttkbootstrap导入"""
    try:
        import ttkbootstrap as ttk
        print("✅ ttkbootstrap导入成功")
        
        # 尝试获取版本信息
        try:
            version = ttk.__version__
            print(f"   版本: {version}")
        except AttributeError:
            # 如果没有__version__属性，尝试其他方式
            try:
                import pkg_resources
                version = pkg_resources.get_distribution("ttkbootstrap").version
                print(f"   版本: {version}")
            except:
                print("   版本: 无法获取版本信息")
        
        return True
    except ImportError as e:
        print(f"❌ ttkbootstrap导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        import ttkbootstrap as ttk
        
        # 测试创建窗口
        root = ttk.Window(themename="litera")
        print("✅ 窗口创建成功")
        
        # 测试获取主题列表
        themes = root.style.theme_names()
        print(f"✅ 可用主题数量: {len(themes)}")
        print(f"   主题列表: {list(themes)[:5]}...")  # 显示前5个主题
        
        # 测试创建组件
        button = ttk.Button(root, text="测试按钮", bootstyle="primary")
        print("✅ 组件创建成功")
        
        # 关闭窗口
        root.destroy()
        print("✅ 窗口销毁成功")
        
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_theme_switching():
    """测试主题切换"""
    try:
        import ttkbootstrap as ttk
        
        root = ttk.Window(themename="litera")
        
        # 测试切换到不同主题
        test_themes = ["darkly", "flatly", "cosmo"]
        for theme in test_themes:
            try:
                root.style.theme_use(theme)
                print(f"✅ 主题切换成功: {theme}")
            except Exception as e:
                print(f"❌ 主题切换失败 {theme}: {e}")
                return False
        
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ 主题切换测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("ttkbootstrap安装验证测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_ttkbootstrap_import),
        ("基本功能测试", test_basic_functionality),
        ("主题切换测试", test_theme_switching),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   测试失败，请检查安装")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！ttkbootstrap安装成功")
        return True
    else:
        print("❌ 部分测试失败，请检查安装")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)