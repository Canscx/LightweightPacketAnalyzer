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
from typing import Optional, Dict, Any

from network_analyzer.config.settings import Settings
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.capture.packet_capture import PacketCapture
from network_analyzer.processing.data_processor import DataProcessor


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
        
        # 线程安全的数据传递队列
        self.packet_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        
        # GUI更新标志
        self._gui_update_active = False
        self._update_timer_id = None
        
        # 当前会话管理
        self.current_session_id = None
        self.current_session_name = None
        
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
        if not hasattr(self, '_update_timer_active'):
            self._update_timer_active = True
            self._schedule_gui_update()
    
    def _stop_gui_updates(self) -> None:
        """停止GUI更新定时器"""
        self._update_timer_active = False
    
    def _schedule_gui_update(self) -> None:
        """调度GUI更新"""
        if hasattr(self, '_update_timer_active') and self._update_timer_active:
            self._update_timer_id = self.root.after(100, self._update_gui)  # 每100ms更新一次
    
    def _update_gui(self) -> None:
        """更新GUI显示"""
        try:
            # 处理数据包队列
            packets_processed = 0
            while not self.packet_queue.empty() and packets_processed < 10:  # 限制每次处理的数据包数量
                try:
                    packet_info = self.packet_queue.get_nowait()
                    
                    # 处理数据包
                    self.data_processor.process_packet(packet_info)
                    
                    # 添加到数据包列表显示
                    self._add_packet_to_list(packet_info)
                    
                    packets_processed += 1
                    
                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"处理数据包失败: {e}")
            
            # 更新统计信息
            self._update_statistics()
            
        except Exception as e:
            self.logger.error(f"GUI更新失败: {e}")
        finally:
            # 继续调度下一次更新
            if hasattr(self, '_update_timer_active') and self._update_timer_active:
                self._schedule_gui_update()
    
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
        messagebox.showinfo("提示", "打开会话功能将在后续版本中实现")
    
    def _save_session(self) -> None:
        """保存会话"""
        messagebox.showinfo("提示", "保存会话功能将在后续版本中实现")
    
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
            
            # 停止GUI更新定时器
            self._stop_gui_updates()
            
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
        if selection:
            # 这里可以显示选中数据包的详细信息
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, "数据包详细信息将在后续版本中显示")
            self.detail_text.config(state=tk.DISABLED)
    
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