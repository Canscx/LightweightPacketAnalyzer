"""
基础设置选项卡模块

实现界面、数据、日志配置的GUI组件
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, Any


class BasicSettingsTab:
    """基础设置选项卡类"""
    
    def __init__(self, parent_frame: ttk.Frame, config_vars: Dict[str, Any], settings):
        """
        初始化基础设置选项卡
        
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
        self._create_interface_section()
        self._create_data_section()
        self._create_log_section()
    
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
    
    def _create_interface_section(self):
        """创建界面设置组"""
        # 界面设置组框
        interface_group = ttk.LabelFrame(self.scrollable_frame, text="界面设置", padding="10")
        interface_group.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 窗口大小设置
        size_frame = ttk.Frame(interface_group)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="窗口大小:").pack(side=tk.LEFT)
        
        # 宽度设置
        ttk.Label(size_frame, text="宽度:").pack(side=tk.LEFT, padx=(20, 5))
        self.config_vars['WINDOW_WIDTH'] = tk.IntVar(value=self.settings.WINDOW_WIDTH)
        width_spinbox = ttk.Spinbox(
            size_frame, 
            from_=800, to=1920, 
            textvariable=self.config_vars['WINDOW_WIDTH'],
            width=8
        )
        width_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # 高度设置
        ttk.Label(size_frame, text="高度:").pack(side=tk.LEFT, padx=(10, 5))
        self.config_vars['WINDOW_HEIGHT'] = tk.IntVar(value=self.settings.WINDOW_HEIGHT)
        height_spinbox = ttk.Spinbox(
            size_frame, 
            from_=600, to=1080, 
            textvariable=self.config_vars['WINDOW_HEIGHT'],
            width=8
        )
        height_spinbox.pack(side=tk.LEFT)
        
        # 预设大小按钮
        preset_frame = ttk.Frame(interface_group)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(preset_frame, text="预设大小:").pack(side=tk.LEFT)
        
        def set_preset_size(width, height):
            self.config_vars['WINDOW_WIDTH'].set(width)
            self.config_vars['WINDOW_HEIGHT'].set(height)
        
        ttk.Button(preset_frame, text="1200×800", 
                  command=lambda: set_preset_size(1200, 800), width=10).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(preset_frame, text="1400×900", 
                  command=lambda: set_preset_size(1400, 900), width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="1600×1000", 
                  command=lambda: set_preset_size(1600, 1000), width=10).pack(side=tk.LEFT)
        
        # 主题设置
        theme_frame = ttk.Frame(interface_group)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(theme_frame, text="界面主题:").pack(side=tk.LEFT)
        
        self.config_vars['THEME'] = tk.StringVar(value=self.settings.THEME)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.config_vars['THEME'],
            values=['default', 'clam', 'alt', 'classic'],
            state='readonly',
            width=15
        )
        theme_combo.pack(side=tk.LEFT, padx=(20, 0))
    
    def _create_data_section(self):
        """创建数据管理组"""
        # 数据管理组框
        data_group = ttk.LabelFrame(self.scrollable_frame, text="数据管理", padding="10")
        data_group.pack(fill=tk.X, padx=10, pady=5)
        
        # 数据目录设置
        data_dir_frame = ttk.Frame(data_group)
        data_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(data_dir_frame, text="数据目录:").pack(side=tk.LEFT)
        
        self.config_vars['DATA_DIRECTORY'] = tk.StringVar(value=self.settings.DATA_DIRECTORY)
        data_dir_entry = ttk.Entry(
            data_dir_frame,
            textvariable=self.config_vars['DATA_DIRECTORY'],
            width=40
        )
        data_dir_entry.pack(side=tk.LEFT, padx=(20, 5), fill=tk.X, expand=True)
        
        def browse_data_dir():
            directory = filedialog.askdirectory(
                title="选择数据目录",
                initialdir=self.config_vars['DATA_DIRECTORY'].get()
            )
            if directory:
                self.config_vars['DATA_DIRECTORY'].set(directory)
        
        ttk.Button(data_dir_frame, text="浏览...", command=browse_data_dir, width=8).pack(side=tk.RIGHT)
        
        # 数据库路径设置
        db_path_frame = ttk.Frame(data_group)
        db_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(db_path_frame, text="数据库路径:").pack(side=tk.LEFT)
        
        self.config_vars['DATABASE_PATH'] = tk.StringVar(value=self.settings.DATABASE_PATH)
        db_path_entry = ttk.Entry(
            db_path_frame,
            textvariable=self.config_vars['DATABASE_PATH'],
            width=40
        )
        db_path_entry.pack(side=tk.LEFT, padx=(20, 5), fill=tk.X, expand=True)
        
        def browse_db_path():
            filename = filedialog.asksaveasfilename(
                title="选择数据库文件",
                defaultextension=".db",
                filetypes=[("SQLite数据库", "*.db"), ("所有文件", "*.*")],
                initialfile=self.config_vars['DATABASE_PATH'].get()
            )
            if filename:
                self.config_vars['DATABASE_PATH'].set(filename)
        
        ttk.Button(db_path_frame, text="浏览...", command=browse_db_path, width=8).pack(side=tk.RIGHT)
        
        # 数据保留设置
        retention_frame = ttk.Frame(data_group)
        retention_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(retention_frame, text="数据保留天数:").pack(side=tk.LEFT)
        
        self.config_vars['DATA_RETENTION_DAYS'] = tk.IntVar(value=self.settings.DATA_RETENTION_DAYS)
        retention_spinbox = ttk.Spinbox(
            retention_frame,
            from_=1, to=365,
            textvariable=self.config_vars['DATA_RETENTION_DAYS'],
            width=10
        )
        retention_spinbox.pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(retention_frame, text="天").pack(side=tk.LEFT)
        
        # 自动清理设置
        self.config_vars['AUTO_CLEANUP'] = tk.BooleanVar(value=self.settings.AUTO_CLEANUP)
        auto_cleanup_check = ttk.Checkbutton(
            retention_frame,
            text="启用自动清理过期数据",
            variable=self.config_vars['AUTO_CLEANUP']
        )
        auto_cleanup_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # 最大数据包数设置
        max_packets_frame = ttk.Frame(data_group)
        max_packets_frame.pack(fill=tk.X)
        
        ttk.Label(max_packets_frame, text="最大数据包数:").pack(side=tk.LEFT)
        
        self.config_vars['MAX_PACKET_COUNT'] = tk.IntVar(value=self.settings.MAX_PACKET_COUNT)
        max_packets_spinbox = ttk.Spinbox(
            max_packets_frame,
            from_=100, to=100000,
            textvariable=self.config_vars['MAX_PACKET_COUNT'],
            width=10
        )
        max_packets_spinbox.pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(max_packets_frame, text="个").pack(side=tk.LEFT)
    
    def _create_log_section(self):
        """创建日志设置组"""
        # 日志设置组框
        log_group = ttk.LabelFrame(self.scrollable_frame, text="日志设置", padding="10")
        log_group.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # 日志级别设置
        log_level_frame = ttk.Frame(log_group)
        log_level_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_level_frame, text="日志级别:").pack(side=tk.LEFT)
        
        self.config_vars['LOG_LEVEL'] = tk.StringVar(value=self.settings.LOG_LEVEL)
        log_level_combo = ttk.Combobox(
            log_level_frame,
            textvariable=self.config_vars['LOG_LEVEL'],
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            state='readonly',
            width=15
        )
        log_level_combo.pack(side=tk.LEFT, padx=(20, 0))
        
        # 日志级别说明
        level_info = {
            'DEBUG': '调试信息（最详细）',
            'INFO': '一般信息',
            'WARNING': '警告信息',
            'ERROR': '错误信息',
            'CRITICAL': '严重错误（最少）'
        }
        
        def on_level_change(event=None):
            current_level = self.config_vars['LOG_LEVEL'].get()
            info_text = level_info.get(current_level, '')
            level_info_label.config(text=info_text)
        
        log_level_combo.bind('<<ComboboxSelected>>', on_level_change)
        
        level_info_label = ttk.Label(log_level_frame, text=level_info.get(self.settings.LOG_LEVEL, ''), 
                                   foreground='gray')
        level_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 日志文件路径设置
        log_file_frame = ttk.Frame(log_group)
        log_file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_file_frame, text="日志文件:").pack(side=tk.LEFT)
        
        self.config_vars['LOG_FILE'] = tk.StringVar(value=self.settings.LOG_FILE)
        log_file_entry = ttk.Entry(
            log_file_frame,
            textvariable=self.config_vars['LOG_FILE'],
            width=40
        )
        log_file_entry.pack(side=tk.LEFT, padx=(20, 5), fill=tk.X, expand=True)
        
        def browse_log_file():
            filename = filedialog.asksaveasfilename(
                title="选择日志文件",
                defaultextension=".log",
                filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
                initialfile=self.config_vars['LOG_FILE'].get()
            )
            if filename:
                self.config_vars['LOG_FILE'].set(filename)
        
        ttk.Button(log_file_frame, text="浏览...", command=browse_log_file, width=8).pack(side=tk.RIGHT)
        
        # 日志文件大小限制
        log_size_frame = ttk.Frame(log_group)
        log_size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_size_frame, text="日志文件大小限制:").pack(side=tk.LEFT)
        
        # 将字节转换为MB显示
        log_size_mb = self.settings.LOG_MAX_SIZE // (1024 * 1024)
        self.config_vars['LOG_MAX_SIZE'] = tk.IntVar(value=log_size_mb)
        log_size_spinbox = ttk.Spinbox(
            log_size_frame,
            from_=1, to=100,
            textvariable=self.config_vars['LOG_MAX_SIZE'],
            width=8
        )
        log_size_spinbox.pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(log_size_frame, text="MB").pack(side=tk.LEFT)
        
        # 备份文件数量
        ttk.Label(log_size_frame, text="备份文件数:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.config_vars['LOG_BACKUP_COUNT'] = tk.IntVar(value=self.settings.LOG_BACKUP_COUNT)
        backup_count_spinbox = ttk.Spinbox(
            log_size_frame,
            from_=0, to=10,
            textvariable=self.config_vars['LOG_BACKUP_COUNT'],
            width=8
        )
        backup_count_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(log_size_frame, text="个").pack(side=tk.LEFT)