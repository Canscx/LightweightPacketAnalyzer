#!/usr/bin/env python3
"""
逐步测试UI创建的脚本
"""

import sys
import traceback
import logging
import tkinter as tk
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, 'src')

def test_ui_creation():
    """逐步测试UI创建"""
    print("开始逐步测试UI创建...")
    
    try:
        # 导入必要模块
        from network_analyzer.config.settings import Settings
        import ttkbootstrap as ttk
        from ttkbootstrap import Window
        from network_analyzer.gui.theme_manager import theme_manager
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        
        # 加载配置
        settings = Settings()
        print(f"✓ 配置加载成功: {settings.APP_NAME}")
        
        # 创建窗口
        theme_name = settings.THEME if theme_manager.validate_theme(settings.THEME) else theme_manager.DEFAULT_THEME
        root = Window(themename=theme_name)
        print(f"✓ 窗口创建成功，主题: {theme_name}")
        
        # 设置窗口属性
        root.title(settings.APP_NAME)
        root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        print("✓ 窗口属性设置成功")
        
        # 测试菜单创建
        print("测试菜单创建...")
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="测试", command=lambda: print("菜单点击"))
        print("✓ 菜单创建成功")
        
        # 测试工具栏创建
        print("测试工具栏创建...")
        toolbar = ttk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        test_btn = ttk.Button(toolbar, text="测试按钮", command=lambda: print("按钮点击"))
        test_btn.pack(side=tk.LEFT, padx=2)
        print("✓ 工具栏创建成功")
        
        # 测试主内容区域创建
        print("测试主内容区域创建...")
        main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        print("✓ 主内容区域创建成功")
        
        # 测试数据包列表创建
        print("测试数据包列表创建...")
        columns = ("时间", "源IP", "目标IP", "协议", "长度")
        packet_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            packet_tree.heading(col, text=col)
            packet_tree.column(col, width=100)
        
        packet_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=packet_tree.yview)
        packet_tree.configure(yscrollcommand=packet_scrollbar.set)
        
        packet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        packet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        print("✓ 数据包列表创建成功")
        
        # 测试右侧面板创建
        print("测试右侧面板创建...")
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        detail_frame = ttk.Frame(notebook)
        notebook.add(detail_frame, text="数据包详情")
        
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="统计信息")
        print("✓ 右侧面板创建成功")
        
        # 测试状态栏创建
        print("测试状态栏创建...")
        status_bar = ttk.Frame(root)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_text = ttk.Label(status_bar, text="就绪")
        status_text.pack(side=tk.LEFT, padx=5)
        print("✓ 状态栏创建成功")
        
        # 更新窗口
        root.update()
        print("✓ 窗口更新成功")
        
        # 显示窗口3秒
        print("显示窗口3秒...")
        root.after(3000, root.quit)
        root.mainloop()
        print("✓ 窗口显示测试完成")
        
        return True
        
    except Exception as e:
        print(f"✗ UI创建失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    if test_ui_creation():
        print("\n✓ 所有UI组件创建成功")
        return 0
    else:
        print("\n✗ UI创建失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())