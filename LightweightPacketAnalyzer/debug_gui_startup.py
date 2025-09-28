#!/usr/bin/env python3
"""
GUI启动调试脚本

逐步检查GUI初始化过程，找出问题所在
"""

import sys
import traceback
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, 'src')

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    try:
        from network_analyzer.config.settings import Settings
        print("✓ Settings导入成功")
        
        from network_analyzer.gui.main_window import MainWindow
        print("✓ MainWindow导入成功")
        
        import ttkbootstrap as ttk
        print("✓ ttkbootstrap导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_settings():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")
    try:
        from network_analyzer.config.settings import Settings
        settings = Settings()
        print(f"✓ 配置加载成功")
        print(f"  - APP_NAME: {settings.APP_NAME}")
        print(f"  - THEME: {settings.THEME}")
        print(f"  - WINDOW_WIDTH: {settings.WINDOW_WIDTH}")
        print(f"  - WINDOW_HEIGHT: {settings.WINDOW_HEIGHT}")
        return settings
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        traceback.print_exc()
        return None

def test_mainwindow_step_by_step(settings):
    """逐步测试MainWindow初始化"""
    print("\n=== 逐步测试MainWindow初始化 ===")
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        from network_analyzer.gui.main_window import MainWindow
        from network_analyzer.storage.data_manager import DataManager
        from network_analyzer.capture.packet_capture import PacketCapture
        from network_analyzer.processing.data_processor import DataProcessor
        from network_analyzer.analysis.protocol_parser import ProtocolParser
        from network_analyzer.analysis.packet_formatter import PacketFormatter
        from network_analyzer.gui.theme_manager import theme_manager
        
        print("1. 开始创建MainWindow实例...")
        
        # 手动创建MainWindow的各个组件
        print("2. 初始化数据管理器...")
        data_manager = DataManager(settings.get_database_path())
        print("✓ 数据管理器初始化成功")
        
        print("3. 初始化数据包捕获器...")
        try:
            packet_capture = PacketCapture(settings)
            print("✓ 数据包捕获器初始化成功")
        except ImportError as e:
            print(f"⚠ 数据包捕获器初始化失败: {e}")
            packet_capture = None
        
        print("4. 初始化数据处理器...")
        data_processor = DataProcessor(settings, data_manager)
        print("✓ 数据处理器初始化成功")
        
        print("5. 初始化协议解析器...")
        protocol_parser = ProtocolParser()
        packet_formatter = PacketFormatter()
        print("✓ 协议解析器和格式化器初始化成功")
        
        print("6. 创建主窗口...")
        try:
            import ttkbootstrap as ttk
            from ttkbootstrap import Window
            
            theme_name = settings.THEME if theme_manager.validate_theme(settings.THEME) else theme_manager.DEFAULT_THEME
            root = Window(themename=theme_name)
            print(f"✓ 使用ttkbootstrap主题: {theme_name}")
        except Exception as e:
            print(f"✗ 窗口创建失败: {e}")
            return None
        
        print("7. 设置窗口属性...")
        root.title(settings.APP_NAME)
        root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        print("✓ 窗口属性设置成功")
        
        print("8. 测试UI组件创建...")
        
        # 测试菜单创建
        print("  8.1 创建菜单栏...")
        try:
            import tkinter as tk
            menubar = tk.Menu(root)
            root.config(menu=menubar)
            print("  ✓ 菜单栏创建成功")
        except Exception as e:
            print(f"  ✗ 菜单栏创建失败: {e}")
            traceback.print_exc()
            return None
        
        # 测试工具栏创建
        print("  8.2 创建工具栏...")
        try:
            toolbar = ttk.Frame(root)
            toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
            print("  ✓ 工具栏创建成功")
        except Exception as e:
            print(f"  ✗ 工具栏创建失败: {e}")
            traceback.print_exc()
            return None
        
        # 测试主内容区域
        print("  8.3 创建主内容区域...")
        try:
            main_frame = ttk.Frame(root)
            main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=2)
            print("  ✓ 主内容区域创建成功")
        except Exception as e:
            print(f"  ✗ 主内容区域创建失败: {e}")
            traceback.print_exc()
            return None
        
        # 测试状态栏
        print("  8.4 创建状态栏...")
        try:
            status_frame = ttk.Frame(root)
            status_frame.pack(side=tk.BOTTOM, fill=tk.X)
            print("  ✓ 状态栏创建成功")
        except Exception as e:
            print(f"  ✗ 状态栏创建失败: {e}")
            traceback.print_exc()
            return None
        
        print("9. 测试窗口显示...")
        try:
            root.update()
            print("✓ 窗口更新成功")
            
            # 显示窗口3秒
            print("显示窗口3秒...")
            root.after(3000, root.quit)
            root.mainloop()
            print("✓ 窗口显示测试完成")
            
        except Exception as e:
            print(f"✗ 窗口显示失败: {e}")
            traceback.print_exc()
            return None
        
        return True
        
    except Exception as e:
        print(f"✗ MainWindow初始化失败: {e}")
        traceback.print_exc()
        return None

def test_actual_mainwindow(settings):
    """测试实际的MainWindow类"""
    print("\n=== 测试实际MainWindow类 ===")
    
    try:
        from network_analyzer.gui.main_window import MainWindow
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        
        print("创建MainWindow实例...")
        
        # 使用超时机制
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("MainWindow初始化超时")
        
        # 设置5秒超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            app = MainWindow(settings)
            signal.alarm(0)  # 取消超时
            print("✓ MainWindow创建成功")
            
            # 测试窗口显示
            print("测试窗口显示...")
            app.root.after(2000, app.root.quit)
            app.root.mainloop()
            print("✓ 窗口显示成功")
            
            return True
            
        except TimeoutError:
            print("✗ MainWindow初始化超时")
            return False
        
    except Exception as e:
        print(f"✗ MainWindow测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始GUI启动调试...")
    
    # 测试导入
    if not test_imports():
        return 1
    
    # 测试配置
    settings = test_settings()
    if not settings:
        return 1
    
    # 逐步测试MainWindow
    if not test_mainwindow_step_by_step(settings):
        return 1
    
    # 测试实际MainWindow
    if not test_actual_mainwindow(settings):
        return 1
    
    print("\n=== 所有测试完成 ===")
    print("✓ GUI启动调试成功")
    return 0

if __name__ == "__main__":
    sys.exit(main())