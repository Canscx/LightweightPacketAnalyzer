"""
主窗口模块

提供应用程序的主图形界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
import threading
import queue
import time
from datetime import datetime
from typing import Optional, Dict, Any

from network_analyzer.config.settings import Settings
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.capture.packet_capture import PacketCapture
from network_analyzer.processing.data_processor import DataProcessor
from network_analyzer.analysis.protocol_parser import ProtocolParser
from network_analyzer.analysis.packet_formatter import PacketFormatter
from network_analyzer.analysis.packet_cache import packet_cache


class SessionDialog:
    """会话选择对话框类"""
    
    def __init__(self, parent: tk.Tk, data_manager: DataManager):
        """
        初始化会话选择对话框
        
        Args:
            parent: 父窗口
            data_manager: 数据管理器实例
        """
        self.parent = parent
        self.data_manager = data_manager
        self.selected_session_id = None
        self.sessions = []
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择会话")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_dialog()
        
        # 创建UI组件
        self._create_ui()
        
        # 加载会话列表
        self._load_sessions()
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_dialog(self) -> None:
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        
        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 获取对话框大小
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_ui(self) -> None:
        """创建对话框UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="选择要打开的会话", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 会话列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 会话列表
        columns = ("会话名称", "开始时间", "数据包数", "总字节数")
        self.session_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=12
        )
        
        # 设置列标题和宽度
        self.session_tree.heading("会话名称", text="会话名称")
        self.session_tree.heading("开始时间", text="开始时间")
        self.session_tree.heading("数据包数", text="数据包数")
        self.session_tree.heading("总字节数", text="总字节数")
        
        self.session_tree.column("会话名称", width=150)
        self.session_tree.column("开始时间", width=150)
        self.session_tree.column("数据包数", width=80)
        self.session_tree.column("总字节数", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.session_tree.yview)
        self.session_tree.configure(yscrollcommand=scrollbar.set)
        
        # 打包列表和滚动条
        self.session_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.session_tree.bind("<Double-1>", self._on_double_click)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, 
            text="取消", 
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 确定按钮
        self.ok_btn = ttk.Button(
            button_frame, 
            text="确定", 
            command=self._on_ok,
            state=tk.DISABLED
        )
        self.ok_btn.pack(side=tk.RIGHT)
        
        # 绑定选择事件
        self.session_tree.bind("<<TreeviewSelect>>", self._on_session_select)
    
    def _load_sessions(self) -> None:
        """加载并显示会话列表"""
        try:
            # 获取所有会话
            self.sessions = self.data_manager.get_sessions()
            
            # 清空现有列表
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
            
            # 添加会话到列表
            for session in self.sessions:
                # 格式化时间
                start_time = session.get('start_time', 0)
                if start_time:
                    from datetime import datetime
                    formatted_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_time = "未知"
                
                # 格式化数据包数和字节数
                packet_count = session.get('packet_count', 0)
                total_bytes = session.get('total_bytes', 0)
                
                # 插入到树形视图
                self.session_tree.insert('', 'end', values=(
                    session.get('session_name', '未命名会话'),
                    formatted_time,
                    f"{packet_count:,}",
                    f"{total_bytes:,}"
                ))
            
            # 如果没有会话，显示提示
            if not self.sessions:
                self.session_tree.insert('', 'end', values=(
                    "没有找到已保存的会话", "", "", ""
                ))
                
        except Exception as e:
            logging.getLogger(__name__).error(f"加载会话列表失败: {e}")
            messagebox.showerror("错误", f"加载会话列表失败: {e}")
    
    def _on_session_select(self, event) -> None:
        """处理会话选择事件"""
        selection = self.session_tree.selection()
        if selection and self.sessions:
            # 获取选中的索引
            item = selection[0]
            index = self.session_tree.index(item)
            
            # 检查是否是有效的会话
            if 0 <= index < len(self.sessions):
                self.selected_session_id = self.sessions[index]['id']
                self.ok_btn.config(state=tk.NORMAL)
            else:
                self.selected_session_id = None
                self.ok_btn.config(state=tk.DISABLED)
        else:
            self.selected_session_id = None
            self.ok_btn.config(state=tk.DISABLED)
    
    def _on_double_click(self, event) -> None:
        """处理双击事件"""
        if self.selected_session_id:
            self._on_ok()
    
    def _on_ok(self) -> None:
        """处理确定按钮点击"""
        if self.selected_session_id:
            self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """处理取消按钮点击"""
        self.selected_session_id = None
        self.dialog.destroy()
    
    def show(self) -> Optional[int]:
        """
        显示对话框并等待用户选择
        
        Returns:
            选中的会话ID，如果取消则返回None
        """
        # 等待对话框关闭
        self.dialog.wait_window()
        return self.selected_session_id


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
        
        # 初始化数据包捕获器
        try:
            self.packet_capture = PacketCapture(settings)
            self.logger.info("数据包捕获器初始化成功")
        except ImportError as e:
            self.logger.error(f"数据包捕获器初始化失败: {e}")
            self.packet_capture = None
        
        # 初始化数据处理器
        self.data_processor = DataProcessor(settings, self.data_manager)
        self.logger.info("数据处理器初始化成功")
        
        # 初始化协议解析器和格式化器
        self.protocol_parser = ProtocolParser()
        self.packet_formatter = PacketFormatter()
        self.logger.info("协议解析器和格式化器初始化成功")
        
        # 线程安全的数据传递队列
        self.packet_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        
        # GUI更新标志
        self._gui_update_active = False
        self._update_timer_id = None
        
        # 当前会话管理
        self.current_session_id = None
        self.current_session_name = None
        
        # 捕获状态管理
        self.is_capturing = False
        
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
        
        # 设置数据包回调
        if self.packet_capture:
            self.packet_capture.set_packet_callback(self._on_packet_received)
        
        # 初始化界面
        self._init_ui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 启动GUI更新定时器
        self._start_gui_updates()
        
        self.logger.info("主窗口初始化完成")
    
    def _on_packet_received(self, packet_info: Dict[str, Any]) -> None:
        """
        数据包接收回调函数
        
        Args:
            packet_info: 数据包信息
        """
        try:
            # 将数据包放入队列，避免阻塞捕获线程
            self.packet_queue.put(packet_info, block=False)
        except queue.Full:
            self.logger.warning("数据包队列已满，丢弃数据包")
    
    def _start_gui_updates(self) -> None:
        """启动GUI更新定时器"""
        self._update_timer_active = True
        self._schedule_gui_update()
    
    def _stop_gui_updates(self) -> None:
        """停止GUI更新定时器"""
        self._update_timer_active = False
    
    def _schedule_gui_update(self) -> None:
        """调度GUI更新"""
        if hasattr(self, '_update_timer_active') and self._update_timer_active:
            self._update_timer_id = self.root.after(200, self._update_gui)  # 每200ms更新一次，减少更新频率
    
    def _update_gui(self) -> None:
        """更新GUI显示"""
        try:
            # 处理数据包队列 - 只处理显示，不进行数据库操作
            packets_processed = 0
            display_packets = []
            
            # 批量获取数据包
            while not self.packet_queue.empty() and packets_processed < 20:
                try:
                    packet_info = self.packet_queue.get_nowait()
                    display_packets.append(packet_info)
                    packets_processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"获取数据包失败: {e}")
            
            # 异步处理数据包（数据库操作）
            for packet_info in display_packets:
                try:
                    # 异步保存到数据库（不阻塞GUI）
                    self.data_processor.process_packet(packet_info)
                    
                    # 立即添加到GUI显示
                    self._add_packet_to_list(packet_info)
                    
                except Exception as e:
                    self.logger.error(f"处理数据包失败: {e}")
            
            # 限制显示的数据包数量，防止内存无限增长
            self._limit_packet_display()
            
            # 更新统计信息
            self._update_statistics()
            
            # 更新数据库队列状态信息
            self._update_queue_status()
            
        except Exception as e:
            self.logger.error(f"GUI更新失败: {e}")
        finally:
            # 继续调度下一次更新
            if hasattr(self, '_update_timer_active') and self._update_timer_active:
                self._schedule_gui_update()
    
    def _limit_packet_display(self) -> None:
        """限制数据包显示数量，防止内存无限增长"""
        try:
            if hasattr(self, 'packet_tree') and self.packet_tree:
                # 获取当前显示的数据包数量
                children = self.packet_tree.get_children()
                max_display_packets = 1000  # 最多显示1000个数据包
                
                # 如果超过限制，删除最旧的数据包
                if len(children) > max_display_packets:
                    # 删除最旧的数据包（前面的）
                    for i in range(len(children) - max_display_packets):
                        self.packet_tree.delete(children[i])
        except Exception as e:
            self.logger.error(f"限制数据包显示失败: {e}")
    
    def _update_queue_status(self) -> None:
        """更新数据库队列状态信息"""
        try:
            if hasattr(self.data_processor, 'get_queue_status'):
                queue_status = self.data_processor.get_queue_status()
                queue_size = queue_status.get('queue_size', 0)
                thread_alive = queue_status.get('thread_alive', False)
                
                # 更新状态栏显示队列信息
                if hasattr(self, 'status_text'):
                    current_text = self.status_text.cget('text')
                    # 添加队列状态信息
                    if '|' in current_text:
                        base_text = current_text.split('|')[0]
                    else:
                        base_text = current_text
                    
                    status_info = f"| DB队列: {queue_size}"
                    if not thread_alive:
                        status_info += " (线程停止)"
                    
                    self.status_text.config(text=base_text + status_info)
        except Exception as e:
            self.logger.error(f"更新队列状态失败: {e}")
    
    def _add_packet_to_list(self, packet_info: Dict[str, Any]) -> None:
        """添加数据包到列表显示"""
        try:
            # 格式化数据包信息
            timestamp = packet_info.get('timestamp', '')
            src_ip = packet_info.get('src_ip', 'N/A')
            dst_ip = packet_info.get('dst_ip', 'N/A')
            protocol = packet_info.get('protocol', 'Unknown')
            length = packet_info.get('length', 0)
            
            # 插入到树形视图
            self.packet_tree.insert('', 'end', values=(
                timestamp, src_ip, dst_ip, protocol, length
            ))
            
            # 自动滚动到最新数据包
            children = self.packet_tree.get_children()
            if children:
                self.packet_tree.see(children[-1])
                
        except Exception as e:
            self.logger.error(f"添加数据包到列表失败: {e}")
    
    def _update_statistics(self) -> None:
        """更新统计信息显示"""
        try:
            stats = self.data_processor.get_current_stats()
            
            # 更新状态栏
            total_packets = stats.get('total_packets', 0)
            total_bytes = stats.get('total_bytes', 0)
            self.status_text.config(text=f"正在捕获... 数据包: {total_packets}, 字节: {total_bytes}")
            
            # 更新右侧统计面板（如果存在）
            # 这里可以添加更详细的统计信息更新
            
        except Exception as e:
            self.logger.error(f"更新统计信息失败: {e}")
    
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
        
        # 绑定键盘快捷键
        self._bind_keyboard_shortcuts()
    
    def _bind_keyboard_shortcuts(self) -> None:
        """绑定键盘快捷键"""
        # 绑定Ctrl+S到保存会话功能
        self.root.bind('<Control-s>', lambda event: self._save_session())
        self.root.bind('<Control-S>', lambda event: self._save_session())
    
    def _create_menu(self) -> None:
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建会话", command=self._new_session)
        file_menu.add_command(label="打开会话", command=self._open_session)
        file_menu.add_command(label="保存会话", command=self._save_session, accelerator="Ctrl+S")
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
        
        # 创建详情面板的子标签页
        self.detail_notebook = ttk.Notebook(self.detail_frame)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 协议树标签页
        self.tree_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.tree_frame, text="协议层次")
        
        # 协议树视图
        self.protocol_tree = ttk.Treeview(self.tree_frame, show="tree headings")
        self.protocol_tree["columns"] = ("value",)
        self.protocol_tree.heading("#0", text="字段")
        self.protocol_tree.heading("value", text="值")
        self.protocol_tree.column("#0", width=200)
        self.protocol_tree.column("value", width=300)
        
        tree_scrollbar_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.protocol_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.protocol_tree.xview)
        self.protocol_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        self.protocol_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 十六进制视图标签页
        self.hex_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.hex_frame, text="十六进制")
        
        # 十六进制文本框
        self.hex_text = tk.Text(self.hex_frame, wrap=tk.NONE, state=tk.DISABLED, font=("Courier", 10))
        hex_scrollbar_y = ttk.Scrollbar(self.hex_frame, orient=tk.VERTICAL, command=self.hex_text.yview)
        hex_scrollbar_x = ttk.Scrollbar(self.hex_frame, orient=tk.HORIZONTAL, command=self.hex_text.xview)
        self.hex_text.configure(yscrollcommand=hex_scrollbar_y.set, xscrollcommand=hex_scrollbar_x.set)
        
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hex_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        hex_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 原始数据标签页
        self.raw_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.raw_frame, text="原始数据")
        
        # 原始数据文本框
        self.raw_text = tk.Text(self.raw_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Courier", 10))
        raw_scrollbar = ttk.Scrollbar(self.raw_frame, orient=tk.VERTICAL, command=self.raw_text.yview)
        self.raw_text.configure(yscrollcommand=raw_scrollbar.set)
        
        self.raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        raw_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        """新建会话
        
        完整的新建会话流程：
        1. 检查当前捕获状态
        2. 询问是否保存当前数据
        3. 获取新会话名称
        4. 保存当前会话数据（如需要）
        5. 重置GUI组件
        6. 创建新会话
        7. 更新界面状态
        """
        try:
            # 步骤1: 检查当前捕获状态
            if self._check_capture_status():
                messagebox.showwarning("警告", "请先停止数据包捕获后再新建会话")
                return
            
            # 步骤2: 询问是否保存当前数据
            save_choice = self._ask_save_current_data()
            if save_choice == "cancel":
                return  # 用户取消操作
            elif save_choice == "yes":
                # 保存当前会话数据
                if not self._save_current_session():
                    messagebox.showerror("错误", "保存当前会话失败，无法继续新建会话")
                    return
            
            # 步骤3: 获取新会话名称
            session_name = self._get_session_name()
            if not session_name:
                return  # 用户取消或输入无效
            
            # 步骤4: 重置GUI组件和数据处理器
            self._reset_gui_components()
            
            # 步骤5: 创建新会话
            try:
                session_id = self.data_manager.create_session(session_name)
                if not session_id:
                    messagebox.showerror("错误", "创建新会话失败")
                    return
                
                # 更新当前会话信息
                self.current_session_id = session_id
                self.current_session_name = session_name
                
                # 步骤6: 更新界面状态
                self._update_session_status(session_name)
                
                # 显示成功消息
                messagebox.showinfo("成功", f"新会话 '{session_name}' 创建成功")
                
                logging.info(f"新会话创建成功: {session_name} (ID: {session_id})")
                
            except Exception as e:
                logging.error(f"创建新会话时发生错误: {str(e)}")
                messagebox.showerror("错误", f"创建新会话时发生错误: {str(e)}")
                
        except Exception as e:
            logging.error(f"新建会话过程中发生未预期错误: {str(e)}")
            messagebox.showerror("错误", f"新建会话失败: {str(e)}")
    
    def _update_session_status(self, session_name: str) -> None:
        """更新会话状态显示
        
        Args:
            session_name: 会话名称
        """
        try:
            # 更新状态栏
            if hasattr(self, 'status_text'):
                self.status_text.config(text=f"当前会话: {session_name}")
            
            # 更新窗口标题
            if hasattr(self, 'root'):
                app_name = getattr(self.settings, 'APP_NAME', 'Network Analyzer')
                self.root.title(f"{app_name} - {session_name}")
                
        except Exception as e:
            logging.error(f"更新会话状态时发生错误: {str(e)}")
    
    def new_session(self) -> bool:
        """公共接口：新建会话
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 记录操作前的状态
            old_session_id = getattr(self, 'current_session_id', None)
            old_session_name = getattr(self, 'current_session_name', None)
            
            # 执行新建会话
            self._new_session()
            
            # 检查是否成功创建了新会话
            new_session_id = getattr(self, 'current_session_id', None)
            return new_session_id is not None and new_session_id != old_session_id
            
        except Exception as e:
            logging.error(f"新建会话公共接口调用失败: {str(e)}")
            return False
    
    def _open_session(self) -> None:
        """打开会话"""
        try:
            # 检查是否正在捕获
            if self.is_capturing:
                messagebox.showwarning("警告", "请先停止当前捕获再打开会话")
                return
            
            # 创建并显示会话选择对话框
            dialog = SessionDialog(self.root, self.data_manager)
            selected_session_id = dialog.show()
            
            if selected_session_id:
                # 加载选中的会话数据
                self._load_session_data(selected_session_id)
                
                # 更新状态栏
                self.status_text.config(text=f"已打开会话 ID: {selected_session_id}")
                
                # 记录日志
                self.logger.info(f"成功打开会话: {selected_session_id}")
                
        except Exception as e:
            self.logger.error(f"打开会话失败: {e}")
            messagebox.showerror("错误", f"打开会话失败: {e}")
    
    def _load_session_data(self, session_id: int) -> None:
        """
        加载会话数据到GUI
        
        Args:
            session_id: 会话ID
        """
        try:
            # 重置GUI组件
            self._reset_gui_components()
            
            # 获取会话数据包
            packets = self.data_manager.get_packets_by_session(session_id)
            
            # 加载数据包到列表
            for packet in packets:
                self._add_packet_to_list(packet)
            
            # 更新会话状态
            self.current_session_id = session_id
            
            # 获取会话信息
            sessions = self.data_manager.get_sessions()
            session_info = next((s for s in sessions if s['id'] == session_id), None)
            
            if session_info:
                self.current_session_name = session_info.get('session_name', f'会话{session_id}')
                
                # 更新统计信息
                self._update_session_statistics(session_info)
            
            self.logger.info(f"成功加载会话数据: {session_id}, 数据包数: {len(packets)}")
            
        except Exception as e:
            self.logger.error(f"加载会话数据失败: {e}")
            raise
    
    def _update_session_statistics(self, session_info: Dict[str, Any]) -> None:
        """
        更新会话统计信息显示
        
        Args:
            session_info: 会话信息字典
        """
        try:
            if hasattr(self, 'stats_text'):
                stats_text = f"""会话统计信息:
会话名称: {session_info.get('session_name', '未知')}
开始时间: {datetime.fromtimestamp(session_info.get('start_time', 0)).strftime('%Y-%m-%d %H:%M:%S')}
结束时间: {datetime.fromtimestamp(session_info.get('end_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if session_info.get('end_time') else '未结束'}
数据包数: {session_info.get('packet_count', 0):,}
总字节数: {session_info.get('total_bytes', 0):,}
"""
                
                self.stats_text.config(state=tk.NORMAL)
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, stats_text)
                self.stats_text.config(state=tk.DISABLED)
                
        except Exception as e:
            self.logger.error(f"更新会话统计信息失败: {e}")

    def _save_session(self) -> None:
        """保存会话"""
        try:
            # 检查是否有数据可以保存
            if not hasattr(self, 'data_processor') or self.data_processor is None:
                messagebox.showwarning(
                    "无法保存",
                    "当前没有可保存的会话数据。\n请先创建新会话或开始数据捕获。",
                    parent=self.root
                )
                return
            
            # 检查是否有数据包数据
            stats = self.data_processor.get_statistics()
            if stats.get('total_packets', 0) == 0:
                result = messagebox.askyesno(
                    "确认保存",
                    "当前会话没有捕获到数据包。\n是否仍要保存空会话？",
                    parent=self.root
                )
                if not result:
                    return
            
            # 调用现有的保存逻辑
            success = self._save_current_session()
            
            if success:
                self.logger.info("通过菜单保存会话成功")
            else:
                self.logger.warning("通过菜单保存会话失败")
                
        except Exception as e:
            self.logger.error(f"保存会话时发生未预期错误: {e}")
            messagebox.showerror(
                "保存失败",
                f"保存会话时发生错误:\n{str(e)}",
                parent=self.root
            )
    
    def _export_data(self) -> None:
        """导出数据"""
        try:
            from tkinter import filedialog
            
            # 选择导出文件
            filename = filedialog.asksaveasfilename(
                title="导出数据",
                defaultextension=".csv",
                filetypes=[
                    ("CSV文件", "*.csv"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if filename:
                # 获取当前统计数据
                stats = self.data_processor.get_current_stats()
                
                if filename.endswith('.json'):
                    import json
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
                else:
                    # 导出为CSV格式
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['指标', '数值'])
                        writer.writerow(['总数据包', stats.get('total_packets', 0)])
                        writer.writerow(['总字节数', stats.get('total_bytes', 0)])
                        writer.writerow(['数据包速率', f"{stats.get('packet_rate', 0):.2f} pps"])
                        writer.writerow(['字节速率', f"{stats.get('byte_rate', 0):.2f} Bps"])
                        
                        # 协议分布
                        writer.writerow([])
                        writer.writerow(['协议分布'])
                        for protocol, count in stats.get('protocol_counts', {}).items():
                            writer.writerow([protocol, count])
                
                messagebox.showinfo("成功", f"数据已导出到: {filename}")
                self.logger.info(f"数据导出成功: {filename}")
                
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")
    
    def _start_capture(self) -> None:
        """开始捕获"""
        if not self.packet_capture:
            messagebox.showerror("错误", "数据包捕获器未初始化，请检查网络权限")
            return
            
        try:
            # 设置数据包回调函数
            self.packet_capture.set_packet_callback(self._on_packet_received)
            
            # 开始捕获
            if self.packet_capture.start_capture():
                self.is_capturing = True  # 更新捕获状态
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.status_text.config(text="正在捕获...")
                self.logger.info("开始数据包捕获")
                
                # 启动GUI更新定时器
                self._start_gui_updates()
            else:
                messagebox.showerror("错误", "无法开始数据包捕获，请检查网络接口和权限")
                
        except Exception as e:
            self.logger.error(f"启动捕获失败: {e}")
            messagebox.showerror("错误", f"启动捕获失败: {str(e)}")
    
    def _stop_capture(self) -> None:
        """停止捕获"""
        if not self.packet_capture:
            return
            
        try:
            # 停止捕获
            self.packet_capture.stop_capture()
            
            # 更新捕获状态
            self.is_capturing = False
            
            # 停止GUI更新定时器
            self._stop_gui_updates()
            
            # 更新当前会话的结束时间
            if hasattr(self, 'current_session_id') and self.current_session_id:
                try:
                    stats = self.data_processor.get_current_stats()
                    self.data_manager.update_session(
                        self.current_session_id,
                        packet_count=stats.get('total_packets', 0),
                        total_bytes=stats.get('total_bytes', 0)
                    )
                except Exception as e:
                    self.logger.error(f"更新会话信息失败: {e}")
            
            # 更新UI状态
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_text.config(text="就绪")
            self.logger.info("停止数据包捕获")
            
            # 显示最终统计信息
            stats = self.data_processor.get_current_stats()
            messagebox.showinfo("捕获完成", 
                f"捕获完成！\n"
                f"总数据包: {stats.get('total_packets', 0)}\n"
                f"总字节数: {stats.get('total_bytes', 0)}")
                
        except Exception as e:
            self.logger.error(f"停止捕获失败: {e}")
            messagebox.showerror("错误", f"停止捕获失败: {str(e)}")
            # 即使出错也要恢复UI状态
            self.is_capturing = False  # 确保状态正确
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_text.config(text="就绪")

    def _check_capture_status(self) -> bool:
        """
        检查当前捕获状态
        
        Returns:
            bool: 如果正在捕获返回True，否则返回False
        """
        try:
            # 检查packet_capture是否存在且正在捕获
            if self.packet_capture is not None:
                return self.packet_capture.is_capturing
            else:
                return False
        except Exception as e:
            self.logger.error(f"检查捕获状态失败: {e}")
            return False

    def _get_session_name(self) -> Optional[str]:
        """
        获取用户输入的会话名称
        
        Returns:
            Optional[str]: 用户输入的会话名称，如果取消则返回None
        """
        try:
            session_name = simpledialog.askstring(
                "新建会话",
                "请输入会话名称:",
                parent=self.root,
                initialvalue="新会话"
            )
            
            # 验证输入
            if session_name is not None:
                session_name = session_name.strip()
                if not session_name:
                    messagebox.showerror("错误", "会话名称不能为空")
                    return None
                if len(session_name) > 100:
                    messagebox.showerror("错误", "会话名称长度不能超过100个字符")
                    return None
            
            return session_name
        except Exception as e:
            self.logger.error(f"获取会话名称失败: {e}")
            messagebox.showerror("错误", "获取会话名称时发生错误")
            return None

    def _ask_save_current_data(self) -> str:
        """
        询问是否保存当前数据
        
        Returns:
            str: 用户选择 'yes'/'no'/'cancel'
        """
        try:
            result = messagebox.askyesnocancel(
                "保存数据",
                "当前会话有数据，是否保存？\n\n"
                "是 - 保存并新建会话\n"
                "否 - 不保存直接新建\n"
                "取消 - 取消操作",
                parent=self.root
            )
            
            if result is True:
                return 'yes'
            elif result is False:
                return 'no'
            else:  # result is None (Cancel)
                return 'cancel'
        except Exception as e:
            self.logger.error(f"询问保存数据失败: {e}")
            return 'cancel'
    
    def _save_current_session(self) -> bool:
        """保存当前会话数据"""
        try:
            if self.current_session_id is None:
                # 如果没有当前会话，先创建一个临时会话
                session_name = self.current_session_name or "临时会话"
                self.current_session_id = self.data_manager.create_session(session_name)
                self.logger.info(f"创建临时会话: {session_name} (ID: {self.current_session_id})")
            
            # 获取当前统计数据
            stats = self.data_processor.get_statistics()
            packet_count = stats.get('total_packets', 0)
            total_bytes = stats.get('total_bytes', 0)
            
            # 更新会话统计信息
            self.data_manager.update_session(
                self.current_session_id,
                packet_count,
                total_bytes
            )
            
            self.logger.info(f"会话数据保存成功: ID={self.current_session_id}, "
                           f"数据包={packet_count}, 字节数={total_bytes}")
            
            # 显示保存成功消息
            messagebox.showinfo(
                "保存成功",
                f"会话数据已保存\n数据包数量: {packet_count}\n总字节数: {total_bytes}",
                parent=self.root
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存会话数据失败: {e}")
            messagebox.showerror(
                "保存失败",
                f"保存会话数据时发生错误:\n{str(e)}",
                parent=self.root
            )
            return False
    
    def _reset_gui_components(self) -> None:
        """
        重置GUI组件和状态
        
        清空所有显示组件，重置会话状态，为新会话做准备
        """
        try:
            # 清空数据包列表
            if hasattr(self, 'packet_tree'):
                for item in self.packet_tree.get_children():
                    self.packet_tree.delete(item)
                self.logger.debug("数据包列表已清空")
            
            # 重置统计信息显示
            if hasattr(self, 'stats_text'):
                self.stats_text.config(state=tk.NORMAL)
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, "暂无统计信息")
                self.stats_text.config(state=tk.DISABLED)
                self.logger.debug("统计信息显示已重置")
            
            # 清空详情显示
            if hasattr(self, 'detail_text'):
                self.detail_text.config(state=tk.NORMAL)
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, "请选择数据包查看详情")
                self.detail_text.config(state=tk.DISABLED)
                self.logger.debug("详情显示已清空")
            
            # 更新状态栏
            if hasattr(self, 'status_text'):
                self.status_text.config(text="就绪 - 新会话")
                self.logger.debug("状态栏已更新")
            
            # 重置数据包计数
            if hasattr(self, 'packet_count_label'):
                self.packet_count_label.config(text="数据包: 0")
                self.logger.debug("数据包计数已重置")
            
            # 重置会话相关状态
            self.current_session_id = None
            self.current_session_name = None
            self.logger.debug("会话状态已重置")
            
            # 重置数据处理器统计
            if hasattr(self, 'data_processor') and self.data_processor:
                self.data_processor.reset_statistics()
                self.logger.debug("数据处理器统计已重置")
            
            # 清空数据队列
            while not self.packet_queue.empty():
                try:
                    self.packet_queue.get_nowait()
                except queue.Empty:
                    break
            
            while not self.stats_queue.empty():
                try:
                    self.stats_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("GUI组件重置完成")
            
        except Exception as e:
            error_msg = f"重置GUI组件时发生错误: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("错误", error_msg)

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
        if not selection:
            return
            
        try:
            # 获取选中的数据包项
            item = selection[0]
            packet_values = self.packet_tree.item(item, 'values')
            
            if not packet_values:
                return
            
            # 从数据库获取原始数据包数据
            # 这里需要根据实际的数据存储结构来获取原始数据
            # 暂时使用模拟数据进行演示
            raw_data = self._get_packet_raw_data(item)
            
            if raw_data:
                self._display_packet_details(raw_data)
            else:
                self._clear_packet_details()
                
        except Exception as e:
            self.logger.error(f"显示数据包详情时发生错误: {e}")
            self._clear_packet_details()
    
    def _get_packet_raw_data(self, item_id: str) -> Optional[bytes]:
        """
        获取数据包的原始数据
        
        Args:
            item_id: 数据包项ID
            
        Returns:
            原始数据包字节，如果获取失败则返回None
        """
        try:
            # 这里应该从数据库或缓存中获取原始数据包数据
            # 目前返回模拟数据用于演示
            # 实际实现需要根据数据存储结构来获取
            
            # 模拟以太网帧数据（用于演示）
            demo_data = bytes([
                # 以太网头部
                0x00, 0x11, 0x22, 0x33, 0x44, 0x55,  # 目标MAC
                0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,  # 源MAC
                0x08, 0x00,                          # EtherType (IPv4)
                # IPv4头部
                0x45, 0x00, 0x00, 0x3c,              # 版本、头长、服务类型、总长度
                0x1c, 0x46, 0x40, 0x00,              # 标识、标志、片偏移
                0x40, 0x06, 0x00, 0x00,              # TTL、协议(TCP)、头校验和
                0xc0, 0xa8, 0x01, 0x64,              # 源IP (192.168.1.100)
                0xc0, 0xa8, 0x01, 0x01,              # 目标IP (192.168.1.1)
                # TCP头部
                0x04, 0xd2, 0x00, 0x50,              # 源端口、目标端口
                0x00, 0x00, 0x00, 0x01,              # 序列号
                0x00, 0x00, 0x00, 0x00,              # 确认号
                0x50, 0x02, 0x20, 0x00,              # 头长、标志、窗口大小
                0x00, 0x00, 0x00, 0x00,              # 校验和、紧急指针
            ])
            
            return demo_data
            
        except Exception as e:
            self.logger.error(f"获取数据包原始数据失败: {e}")
            return None
    
    def _display_packet_details(self, raw_data: bytes) -> None:
        """
        显示数据包详细信息
        
        Args:
            raw_data: 原始数据包字节
        """
        try:
            # 首先尝试从缓存获取解析结果
            parsed_packet = packet_cache.get(raw_data)
            
            if parsed_packet is None:
                # 缓存中没有，进行解析
                parsed_packet = self.protocol_parser.parse_packet(raw_data)
                if parsed_packet:
                    # 将解析结果放入缓存
                    packet_cache.put(raw_data, parsed_packet)
            
            if parsed_packet:
                # 显示协议树
                self._display_protocol_tree(parsed_packet)
                
                # 显示十六进制数据
                self._display_hex_data(raw_data)
                
                # 显示原始数据
                self._display_raw_data(raw_data, parsed_packet)
            else:
                self._clear_packet_details()
                
        except Exception as e:
            self.logger.error(f"显示数据包详情失败: {e}")
            self._clear_packet_details()
    
    def _display_protocol_tree(self, parsed_packet) -> None:
        """显示协议层次树"""
        try:
            # 清空现有内容
            for item in self.protocol_tree.get_children():
                self.protocol_tree.delete(item)
            
            # 获取格式化的协议树
            tree_data = self.packet_formatter.format_packet_tree(parsed_packet)
            
            # 递归添加树节点
            self._add_tree_nodes("", tree_data)
            
        except Exception as e:
            self.logger.error(f"显示协议树失败: {e}")
    
    def _add_tree_nodes(self, parent: str, tree_data: dict) -> None:
        """递归添加树节点"""
        for key, value in tree_data.items():
            if isinstance(value, dict):
                # 如果值是字典，创建父节点并递归添加子节点
                node = self.protocol_tree.insert(parent, "end", text=key, values=("",))
                self._add_tree_nodes(node, value)
            else:
                # 如果值不是字典，直接添加叶节点
                self.protocol_tree.insert(parent, "end", text=key, values=(str(value),))
    
    def _display_hex_data(self, raw_data: bytes) -> None:
        """显示十六进制数据"""
        try:
            self.hex_text.config(state=tk.NORMAL)
            self.hex_text.delete(1.0, tk.END)
            
            hex_dump = self.packet_formatter.format_hex_dump(raw_data)
            self.hex_text.insert(tk.END, hex_dump)
            
            self.hex_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"显示十六进制数据失败: {e}")
    
    def _display_raw_data(self, raw_data: bytes, parsed_packet) -> None:
        """显示原始数据和解析摘要"""
        try:
            self.raw_text.config(state=tk.NORMAL)
            self.raw_text.delete(1.0, tk.END)
            
            # 显示数据包摘要
            summary = self.packet_formatter.format_packet_summary(parsed_packet)
            self.raw_text.insert(tk.END, f"数据包摘要:\n{summary}\n\n")
            
            # 显示详细信息
            details = self.packet_formatter.format_packet_details(parsed_packet)
            self.raw_text.insert(tk.END, f"详细信息:\n{details}")
            
            self.raw_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"显示原始数据失败: {e}")
    
    def _clear_packet_details(self) -> None:
        """清空数据包详情显示"""
        try:
            # 清空协议树
            for item in self.protocol_tree.get_children():
                self.protocol_tree.delete(item)
            
            # 清空十六进制视图
            self.hex_text.config(state=tk.NORMAL)
            self.hex_text.delete(1.0, tk.END)
            self.hex_text.insert(tk.END, "请选择数据包以查看十六进制数据")
            self.hex_text.config(state=tk.DISABLED)
            
            # 清空原始数据视图
            self.raw_text.config(state=tk.NORMAL)
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(tk.END, "请选择数据包以查看详细信息")
            self.raw_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"清空数据包详情失败: {e}")
    
    def _on_closing(self) -> None:
        """窗口关闭事件处理"""
        try:
            # 如果正在捕获，先停止捕获
            if self.packet_capture and self.packet_capture.is_capturing:
                self.logger.info("检测到正在捕获，正在停止...")
                self.packet_capture.stop_capture()
                
            # 停止GUI更新定时器
            if hasattr(self, '_update_timer_active'):
                self._update_timer_active = False
                
            # 停止数据处理器的数据库线程
            if hasattr(self, 'data_processor') and self.data_processor:
                self.logger.info("正在停止数据库线程...")
                self.data_processor.shutdown()
                
            # 数据管理器不需要显式关闭，SQLite连接会自动管理
            self.logger.info("应用程序正常退出")
            
        except Exception as e:
            self.logger.error(f"关闭应用程序时发生错误: {e}")
        finally:
            # 销毁窗口
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