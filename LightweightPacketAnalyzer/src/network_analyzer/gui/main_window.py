"""
主窗口模块

提供应用程序的主图形界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional

from network_analyzer.config.settings import Settings
from network_analyzer.storage.data_manager import DataManager


class MainWindow:
    """主窗口类"""
    
    def __init__(self, settings: Settings):
        """
        初始化主窗口
        
        Args:
            settings: 应用程序配置
        """
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据管理器
        self.data_manager = DataManager(settings.get_database_path())
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title(settings.APP_NAME)
        self.root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap("icon.ico")  # 可以添加图标文件
            pass
        except Exception:
            pass
        
        # 初始化界面
        self._init_ui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("主窗口初始化完成")
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主要内容区域
        self._create_main_content()
        
        # 创建状态栏
        self._create_status_bar()
    
    def _create_menu(self) -> None:
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建会话", command=self._new_session)
        file_menu.add_command(label="打开会话", command=self._open_session)
        file_menu.add_command(label="保存会话", command=self._save_session)
        file_menu.add_separator()
        file_menu.add_command(label="导出数据", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)
        
        # 捕获菜单
        capture_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="捕获", menu=capture_menu)
        capture_menu.add_command(label="开始捕获", command=self._start_capture)
        capture_menu.add_command(label="停止捕获", command=self._stop_capture)
        capture_menu.add_separator()
        capture_menu.add_command(label="捕获选项", command=self._capture_options)
        
        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="协议统计", command=self._protocol_statistics)
        analysis_menu.add_command(label="流量趋势", command=self._traffic_trends)
        analysis_menu.add_command(label="生成报告", command=self._generate_report)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="数据库管理", command=self._database_management)
        tools_menu.add_command(label="清理旧数据", command=self._cleanup_data)
        tools_menu.add_separator()
        tools_menu.add_command(label="设置", command=self._show_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_toolbar(self) -> None:
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # 捕获控制按钮
        self.start_btn = ttk.Button(
            self.toolbar, 
            text="开始捕获", 
            command=self._start_capture
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(
            self.toolbar, 
            text="停止捕获", 
            command=self._stop_capture,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 分析按钮
        ttk.Button(
            self.toolbar, 
            text="协议统计", 
            command=self._protocol_statistics
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            self.toolbar, 
            text="流量趋势", 
            command=self._traffic_trends
        ).pack(side=tk.LEFT, padx=2)
        
        # 状态指示器
        self.status_label = ttk.Label(self.toolbar, text="就绪")
        self.status_label.pack(side=tk.RIGHT, padx=10)
    
    def _create_main_content(self) -> None:
        """创建主要内容区域"""
        # 创建主要的分割窗口
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 数据包列表
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=2)
        
        # 数据包列表
        self._create_packet_list()
        
        # 右侧面板 - 详细信息和统计
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=1)
        
        # 创建右侧的标签页
        self._create_right_panel()
    
    def _create_packet_list(self) -> None:
        """创建数据包列表"""
        # 数据包列表标题
        ttk.Label(self.left_frame, text="数据包列表", font=("Arial", 12, "bold")).pack(pady=5)
        
        # 创建Treeview用于显示数据包
        columns = ("时间", "源IP", "目标IP", "协议", "长度")
        self.packet_tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.packet_tree.heading(col, text=col)
            self.packet_tree.column(col, width=100)
        
        # 添加滚动条
        packet_scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.packet_tree.yview)
        self.packet_tree.configure(yscrollcommand=packet_scrollbar.set)
        
        # 打包组件
        self.packet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        packet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.packet_tree.bind("<<TreeviewSelect>>", self._on_packet_select)
    
    def _create_right_panel(self) -> None:
        """创建右侧面板"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 数据包详情标签页
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="数据包详情")
        
        # 详情文本框
        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, state=tk.DISABLED)
        detail_scrollbar = ttk.Scrollbar(self.detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 统计信息标签页
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="统计信息")
        
        # 统计信息文本框
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, state=tk.DISABLED)
        stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_status_bar(self) -> None:
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态信息
        self.status_text = ttk.Label(self.status_bar, text="就绪")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # 数据包计数
        self.packet_count_label = ttk.Label(self.status_bar, text="数据包: 0")
        self.packet_count_label.pack(side=tk.RIGHT, padx=5)
    
    # 菜单和按钮事件处理方法（占位符）
    def _new_session(self) -> None:
        """新建会话"""
        messagebox.showinfo("提示", "新建会话功能将在后续版本中实现")
    
    def _open_session(self) -> None:
        """打开会话"""
        messagebox.showinfo("提示", "打开会话功能将在后续版本中实现")
    
    def _save_session(self) -> None:
        """保存会话"""
        messagebox.showinfo("提示", "保存会话功能将在后续版本中实现")
    
    def _export_data(self) -> None:
        """导出数据"""
        messagebox.showinfo("提示", "导出数据功能将在后续版本中实现")
    
    def _start_capture(self) -> None:
        """开始捕获"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_text.config(text="正在捕获...")
        self.logger.info("开始数据包捕获")
        messagebox.showinfo("提示", "数据包捕获功能将在后续版本中实现")
    
    def _stop_capture(self) -> None:
        """停止捕获"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_text.config(text="就绪")
        self.logger.info("停止数据包捕获")
    
    def _capture_options(self) -> None:
        """捕获选项"""
        messagebox.showinfo("提示", "捕获选项功能将在后续版本中实现")
    
    def _protocol_statistics(self) -> None:
        """协议统计"""
        messagebox.showinfo("提示", "协议统计功能将在后续版本中实现")
    
    def _traffic_trends(self) -> None:
        """流量趋势"""
        messagebox.showinfo("提示", "流量趋势功能将在后续版本中实现")
    
    def _generate_report(self) -> None:
        """生成报告"""
        messagebox.showinfo("提示", "生成报告功能将在后续版本中实现")
    
    def _database_management(self) -> None:
        """数据库管理"""
        info = self.data_manager.get_database_info()
        message = f"""数据库信息:
路径: {info['database_path']}
大小: {info['database_size']} 字节
数据包数量: {info['packet_count']}
统计记录数量: {info['statistics_count']}
会话数量: {info['session_count']}"""
        messagebox.showinfo("数据库信息", message)
    
    def _cleanup_data(self) -> None:
        """清理旧数据"""
        result = messagebox.askyesno("确认", "确定要清理30天前的旧数据吗？")
        if result:
            deleted_count = self.data_manager.cleanup_old_data()
            messagebox.showinfo("完成", f"已清理 {deleted_count} 条旧记录")
    
    def _show_settings(self) -> None:
        """显示设置"""
        messagebox.showinfo("提示", "设置功能将在后续版本中实现")
    
    def _show_help(self) -> None:
        """显示帮助"""
        help_text = """网络流量统计系统使用说明:

1. 点击"开始捕获"按钮开始捕获网络数据包
2. 在数据包列表中查看捕获的数据包
3. 点击数据包查看详细信息
4. 使用"分析"菜单查看统计信息
5. 使用"文件"菜单保存和导出数据

注意: 需要管理员权限才能捕获网络数据包"""
        messagebox.showinfo("使用说明", help_text)
    
    def _show_about(self) -> None:
        """显示关于信息"""
        about_text = f"""网络流量统计系统 v{self.settings.VERSION}

这是一个轻量级的网络数据包分析器，
用于计算机网络课程设计。

开发者: Student
邮箱: student@example.com"""
        messagebox.showinfo("关于", about_text)
    
    def _on_packet_select(self, event) -> None:
        """数据包选择事件处理"""
        selection = self.packet_tree.selection()
        if selection:
            # 这里可以显示选中数据包的详细信息
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, "数据包详细信息将在后续版本中显示")
            self.detail_text.config(state=tk.DISABLED)
    
    def _on_closing(self) -> None:
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.logger.info("用户关闭应用程序")
            self.root.destroy()
    
    def run(self) -> int:
        """
        运行应用程序
        
        Returns:
            程序退出码
        """
        try:
            self.root.mainloop()
            return 0
        except Exception as e:
            self.logger.error(f"GUI运行出错: {e}", exc_info=True)
            return 1