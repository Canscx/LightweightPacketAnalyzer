"""
高级设置选项卡模块

实现性能、捕获、安全配置的GUI组件
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any


class AdvancedSettingsTab:
    """高级设置选项卡类"""
    
    def __init__(self, parent_frame: ttk.Frame, config_vars: Dict[str, Any], settings):
        """
        初始化高级设置选项卡
        
        Args:
            parent_frame: 父框架
            config_vars: 配置变量字典
            settings: Settings实例
        """
        self.parent_frame = parent_frame
        self.config_vars = config_vars
        self.settings = settings
        
        # 创建滚动框架
        self._create_scrollable_frame()
        
        # 创建各个设置组
        self._create_performance_section()
        self._create_capture_section()
        self._create_security_section()
    
    def _create_scrollable_frame(self):
        """创建可滚动的框架"""
        self.canvas = tk.Canvas(self.parent_frame)
        self.scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _create_performance_section(self):
        """创建性能设置组"""
        # 性能设置组框
        performance_group = ttk.LabelFrame(self.scrollable_frame, text="性能设置", padding="10")
        performance_group.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 缓冲区大小设置
        buffer_frame = ttk.Frame(performance_group)
        buffer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(buffer_frame, text="缓冲区大小:").pack(side=tk.LEFT)
        
        # 将字节转换为KB显示
        buffer_size_kb = self.settings.BUFFER_SIZE // 1024
        self.config_vars['BUFFER_SIZE'] = tk.IntVar(value=buffer_size_kb)
        buffer_spinbox = ttk.Spinbox(
            buffer_frame,
            from_=1, to=1024,  # 1KB到1MB
            textvariable=self.config_vars['BUFFER_SIZE'],
            width=10
        )
        buffer_spinbox.pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(buffer_frame, text="KB").pack(side=tk.LEFT)
        
        # 缓冲区大小说明
        buffer_info = ttk.Label(buffer_frame, text="(建议: 64KB-256KB)", foreground='gray')
        buffer_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # 工作线程数设置
        threads_frame = ttk.Frame(performance_group)
        threads_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(threads_frame, text="工作线程数:").pack(side=tk.LEFT)
        
        self.config_vars['WORKER_THREADS'] = tk.IntVar(value=self.settings.WORKER_THREADS)
        threads_spinbox = ttk.Spinbox(
            threads_frame,
            from_=1, to=16,
            textvariable=self.config_vars['WORKER_THREADS'],
            width=8
        )
        threads_spinbox.pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(threads_frame, text="个").pack(side=tk.LEFT)
        
        # 线程数说明
        threads_info = ttk.Label(threads_frame, text="(建议: CPU核心数的1-2倍)", foreground='gray')
        threads_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # 捕获超时设置
        timeout_frame = ttk.Frame(performance_group)
        timeout_frame.pack(fill=tk.X)
        
        ttk.Label(timeout_frame, text="捕获超时时间:").pack(side=tk.LEFT)
        
        self.config_vars['CAPTURE_TIMEOUT'] = tk.IntVar(value=self.settings.CAPTURE_TIMEOUT)
        timeout_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=1, to=300,
            textvariable=self.config_vars['CAPTURE_TIMEOUT'],
            width=8
        )
        timeout_spinbox.pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(timeout_frame, text="秒").pack(side=tk.LEFT)
    
    def _create_capture_section(self):
        """创建捕获设置组"""
        # 捕获设置组框
        capture_group = ttk.LabelFrame(self.scrollable_frame, text="捕获设置", padding="10")
        capture_group.pack(fill=tk.X, padx=10, pady=5)
        
        # 默认网络接口设置
        interface_frame = ttk.Frame(capture_group)
        interface_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(interface_frame, text="默认网络接口:").pack(side=tk.LEFT)
        
        self.config_vars['CAPTURE_INTERFACE'] = tk.StringVar(value=self.settings.CAPTURE_INTERFACE)
        interface_combo = ttk.Combobox(
            interface_frame,
            textvariable=self.config_vars['CAPTURE_INTERFACE'],
            values=['auto', 'eth0', 'wlan0', 'lo'],  # 常见接口名
            width=20
        )
        interface_combo.pack(side=tk.LEFT, padx=(20, 0))
        
        # 默认过滤器设置
        filter_frame = ttk.Frame(capture_group)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="默认BPF过滤器:").pack(side=tk.LEFT)
        
        self.config_vars['CAPTURE_FILTER'] = tk.StringVar(value=self.settings.CAPTURE_FILTER)
        filter_entry = ttk.Entry(
            filter_frame,
            textvariable=self.config_vars['CAPTURE_FILTER'],
            width=40
        )
        filter_entry.pack(side=tk.LEFT, padx=(20, 5), fill=tk.X, expand=True)
        
        # 过滤器帮助按钮
        def show_filter_help():
            help_text = """常用BPF过滤器示例：
            
• tcp - 只捕获TCP数据包
• udp - 只捕获UDP数据包
• icmp - 只捕获ICMP数据包
• port 80 - 只捕获端口80的数据包
• host 192.168.1.1 - 只捕获指定主机的数据包
• net 192.168.1.0/24 - 只捕获指定网段的数据包
• tcp and port 443 - 捕获HTTPS流量
• not arp - 排除ARP数据包

留空表示捕获所有数据包。"""
            messagebox.showinfo("BPF过滤器帮助", help_text)
        
        ttk.Button(filter_frame, text="帮助", command=show_filter_help, width=6).pack(side=tk.RIGHT)
        
        # 捕获选项设置
        options_frame = ttk.Frame(capture_group)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 混杂模式
        promiscuous_value = self.settings.CAPTURE_OPTIONS.get('promiscuous_mode', True)
        self.config_vars['PROMISCUOUS_MODE'] = tk.BooleanVar(value=promiscuous_value)
        promiscuous_check = ttk.Checkbutton(
            options_frame,
            text="启用混杂模式 (捕获所有网络流量)",
            variable=self.config_vars['PROMISCUOUS_MODE']
        )
        promiscuous_check.pack(anchor=tk.W)
        
        # 验证过滤器
        validate_filters_value = self.settings.CAPTURE_OPTIONS.get('validate_filters', True)
        self.config_vars['VALIDATE_BPF_FILTERS'] = tk.BooleanVar(value=validate_filters_value)
        validate_check = ttk.Checkbutton(
            options_frame,
            text="启用BPF过滤器语法验证",
            variable=self.config_vars['VALIDATE_BPF_FILTERS']
        )
        validate_check.pack(anchor=tk.W, pady=(5, 0))
        
        # 显示接口详情
        show_details_value = self.settings.CAPTURE_OPTIONS.get('show_interface_details', True)
        self.config_vars['SHOW_INTERFACE_DETAILS'] = tk.BooleanVar(value=show_details_value)
        details_check = ttk.Checkbutton(
            options_frame,
            text="显示网络接口详细信息",
            variable=self.config_vars['SHOW_INTERFACE_DETAILS']
        )
        details_check.pack(anchor=tk.W, pady=(5, 0))
        
        # 捕获缓冲区大小
        capture_buffer_frame = ttk.Frame(capture_group)
        capture_buffer_frame.pack(fill=tk.X)
        
        ttk.Label(capture_buffer_frame, text="捕获缓冲区大小:").pack(side=tk.LEFT)
        
        # 将字节转换为MB显示
        capture_buffer_value = self.settings.CAPTURE_OPTIONS.get('buffer_size', 1048576)
        capture_buffer_mb = capture_buffer_value // (1024 * 1024)
        self.config_vars['CAPTURE_BUFFER_SIZE'] = tk.IntVar(value=capture_buffer_mb)
        capture_buffer_spinbox = ttk.Spinbox(
            capture_buffer_frame,
            from_=1, to=64,  # 1MB到64MB
            textvariable=self.config_vars['CAPTURE_BUFFER_SIZE'],
            width=8
        )
        capture_buffer_spinbox.pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(capture_buffer_frame, text="MB").pack(side=tk.LEFT)
    
    def _create_security_section(self):
        """创建安全设置组"""
        # 安全设置组框
        security_group = ttk.LabelFrame(self.scrollable_frame, text="安全设置", padding="10")
        security_group.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # 管理员权限要求
        self.config_vars['REQUIRE_ADMIN'] = tk.BooleanVar(value=self.settings.REQUIRE_ADMIN)
        admin_check = ttk.Checkbutton(
            security_group,
            text="需要管理员权限运行 (推荐)",
            variable=self.config_vars['REQUIRE_ADMIN']
        )
        admin_check.pack(anchor=tk.W, pady=(0, 10))
        
        # 管理员权限说明
        admin_info = ttk.Label(
            security_group, 
            text="启用此选项可以确保程序有足够权限访问网络接口，但需要以管理员身份运行。",
            foreground='gray',
            wraplength=500
        )
        admin_info.pack(anchor=tk.W, pady=(0, 15))
        
        # 混杂模式启用
        self.config_vars['ENABLE_PROMISCUOUS_MODE'] = tk.BooleanVar(value=self.settings.ENABLE_PROMISCUOUS_MODE)
        promiscuous_check = ttk.Checkbutton(
            security_group,
            text="允许启用混杂模式",
            variable=self.config_vars['ENABLE_PROMISCUOUS_MODE']
        )
        promiscuous_check.pack(anchor=tk.W, pady=(0, 10))
        
        # 混杂模式说明
        promiscuous_info = ttk.Label(
            security_group,
            text="混杂模式允许捕获网络上的所有流量，包括不是发送给本机的数据包。\n请确保您有权限监控网络流量。",
            foreground='gray',
            wraplength=500
        )
        promiscuous_info.pack(anchor=tk.W, pady=(0, 15))
        
        # 开发选项
        dev_frame = ttk.LabelFrame(security_group, text="开发选项", padding="5")
        dev_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 调试模式
        self.config_vars['DEBUG'] = tk.BooleanVar(value=self.settings.DEBUG)
        debug_check = ttk.Checkbutton(
            dev_frame,
            text="启用调试模式",
            variable=self.config_vars['DEBUG']
        )
        debug_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 性能分析
        self.config_vars['ENABLE_PROFILING'] = tk.BooleanVar(value=self.settings.ENABLE_PROFILING)
        profiling_check = ttk.Checkbutton(
            dev_frame,
            text="启用性能分析",
            variable=self.config_vars['ENABLE_PROFILING']
        )
        profiling_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 开发选项警告
        dev_warning = ttk.Label(
            dev_frame,
            text="⚠️ 开发选项可能影响性能，仅在开发或调试时启用。",
            foreground='orange',
            font=('Arial', 8)
        )
        dev_warning.pack(anchor=tk.W, pady=(5, 0))