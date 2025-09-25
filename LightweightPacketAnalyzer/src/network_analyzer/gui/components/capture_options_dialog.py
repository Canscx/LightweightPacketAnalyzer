"""
捕获选项对话框

提供网络数据包捕获的配置界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict

from .bpf_validator import BPFValidator
from .filter_template_manager import FilterTemplateManager
from .interface_info_provider import InterfaceInfoProvider, InterfaceInfo
from ...config.settings import Settings


@dataclass
class CaptureOptions:
    """捕获选项数据类"""
    interface: str = ""
    filter_expression: str = ""
    packet_count: int = 1000
    timeout: int = 60
    promiscuous_mode: bool = True
    buffer_size: int = 1048576
    save_to_file: bool = False
    output_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaptureOptions':
        """从字典创建"""
        return cls(**data)


class CaptureOptionsDialog:
    """捕获选项对话框"""
    
    def __init__(self, parent: tk.Tk, settings: Settings, 
                 initial_options: Optional[CaptureOptions] = None):
        """
        初始化捕获选项对话框
        
        Args:
            parent: 父窗口
            settings: 应用设置
            initial_options: 初始选项
        """
        self.parent = parent
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.bpf_validator = BPFValidator()
        self.filter_manager = FilterTemplateManager(settings.get_data_dir())
        self.interface_provider = InterfaceInfoProvider()
        
        # 对话框状态
        self.result = None
        self.dialog = None
        
        # 初始化选项
        if initial_options:
            self.options = initial_options
        else:
            self.options = self._create_default_options()
        
        # UI组件引用
        self.interface_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        self.packet_count_var = tk.IntVar()
        self.timeout_var = tk.IntVar()
        self.promiscuous_var = tk.BooleanVar()
        self.buffer_size_var = tk.IntVar()
        self.save_file_var = tk.BooleanVar()
        self.output_file_var = tk.StringVar()
        
        # 界面组件
        self.interface_combo = None
        self.filter_entry = None
        self.filter_combo = None
        self.validation_label = None
        self.interface_info_text = None
        
        # 回调函数
        self.on_interface_change: Optional[Callable[[str], None]] = None
        self.on_filter_change: Optional[Callable[[str], None]] = None
    
    def _create_default_options(self) -> CaptureOptions:
        """创建默认捕获选项"""
        capture_config = self.settings.CAPTURE_OPTIONS
        
        return CaptureOptions(
            interface=capture_config.get('default_interface', ''),
            filter_expression=capture_config.get('default_filter', ''),
            packet_count=capture_config.get('default_packet_count', 1000),
            timeout=capture_config.get('default_timeout', 60),
            promiscuous_mode=capture_config.get('promiscuous_mode', True),
            buffer_size=capture_config.get('buffer_size', 1048576),
            save_to_file=False,
            output_file=""
        )
    
    def show_dialog(self) -> Optional[CaptureOptions]:
        """
        显示对话框
        
        Returns:
            用户选择的捕获选项，如果取消则返回None
        """
        self._create_dialog()
        self._setup_ui()
        self._load_initial_values()
        self._setup_bindings()
        
        # 模态显示
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_dialog()
        
        # 等待对话框关闭
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def _create_dialog(self):
        """创建对话框窗口"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("捕获选项")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # 设置图标（如果有的话）
        try:
            self.dialog.iconbitmap(self.parent.iconbitmap())
        except:
            pass
        
        # 处理关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(0, weight=1)
        
        # 基本选项选项卡
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本选项")
        self._create_basic_options(basic_frame)
        
        # 高级选项选项卡
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="高级选项")
        self._create_advanced_options(advanced_frame)
        
        # 过滤器选项卡
        filter_frame = ttk.Frame(notebook, padding="10")
        notebook.add(filter_frame, text="过滤器")
        self._create_filter_options(filter_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        
        # 按钮
        ttk.Button(button_frame, text="确定", command=self._on_ok).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self._on_cancel).grid(row=0, column=2, padx=(5, 0))
        ttk.Button(button_frame, text="重置", command=self._on_reset).grid(row=0, column=3, padx=(5, 0))
    
    def _create_basic_options(self, parent: ttk.Frame):
        """创建基本选项界面"""
        # 网络接口选择
        ttk.Label(parent, text="网络接口:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        interface_frame = ttk.Frame(parent)
        interface_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        interface_frame.columnconfigure(0, weight=1)
        
        self.interface_combo = ttk.Combobox(interface_frame, textvariable=self.interface_var, 
                                          state="readonly", width=40)
        self.interface_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(interface_frame, text="刷新", 
                  command=self._refresh_interfaces).grid(row=0, column=1)
        
        # 接口信息显示
        ttk.Label(parent, text="接口信息:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
        
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        self.interface_info_text = tk.Text(info_frame, height=6, width=50, 
                                         wrap=tk.WORD, state=tk.DISABLED)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, 
                                     command=self.interface_info_text.yview)
        self.interface_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.interface_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 数据包数量
        ttk.Label(parent, text="数据包数量:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        count_frame = ttk.Frame(parent)
        count_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        count_spinbox = ttk.Spinbox(count_frame, from_=1, to=100000, 
                                   textvariable=self.packet_count_var, width=10)
        count_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(count_frame, text="(0 = 无限制)").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 超时时间
        ttk.Label(parent, text="超时时间:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        timeout_frame = ttk.Frame(parent)
        timeout_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        timeout_spinbox = ttk.Spinbox(timeout_frame, from_=0, to=3600, 
                                     textvariable=self.timeout_var, width=10)
        timeout_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(timeout_frame, text="秒 (0 = 无限制)").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 配置网格权重
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)
    
    def _create_advanced_options(self, parent: ttk.Frame):
        """创建高级选项界面"""
        # 混杂模式
        ttk.Checkbutton(parent, text="启用混杂模式", 
                       variable=self.promiscuous_var).grid(row=0, column=0, columnspan=2, 
                                                          sticky=tk.W, pady=(0, 10))
        
        # 缓冲区大小
        ttk.Label(parent, text="缓冲区大小:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        buffer_frame = ttk.Frame(parent)
        buffer_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        buffer_spinbox = ttk.Spinbox(buffer_frame, from_=65536, to=16777216, 
                                    increment=65536, textvariable=self.buffer_size_var, width=15)
        buffer_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(buffer_frame, text="字节").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 保存到文件
        ttk.Checkbutton(parent, text="保存到文件", 
                       variable=self.save_file_var,
                       command=self._on_save_file_toggle).grid(row=2, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=(10, 5))
        
        # 输出文件路径
        ttk.Label(parent, text="输出文件:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        file_frame.columnconfigure(0, weight=1)
        
        self.output_file_entry = ttk.Entry(file_frame, textvariable=self.output_file_var, 
                                          state=tk.DISABLED)
        self.output_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_button = ttk.Button(file_frame, text="浏览...", 
                                       command=self._browse_output_file, state=tk.DISABLED)
        self.browse_button.grid(row=0, column=1)
        
        # 配置网格权重
        parent.columnconfigure(1, weight=1)
    
    def _create_filter_options(self, parent: ttk.Frame):
        """创建过滤器选项界面"""
        # 过滤器模板
        ttk.Label(parent, text="过滤器模板:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        template_frame = ttk.Frame(parent)
        template_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        template_frame.columnconfigure(0, weight=1)
        
        self.filter_combo = ttk.Combobox(template_frame, state="readonly", width=40)
        self.filter_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(template_frame, text="应用", 
                  command=self._apply_filter_template).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(template_frame, text="管理", 
                  command=self._manage_filter_templates).grid(row=0, column=2)
        
        # 过滤器表达式
        ttk.Label(parent, text="BPF过滤器:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
        
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 5))
        filter_frame.columnconfigure(0, weight=1)
        filter_frame.rowconfigure(0, weight=1)
        
        self.filter_entry = tk.Text(filter_frame, height=4, width=50, wrap=tk.WORD)
        filter_scrollbar = ttk.Scrollbar(filter_frame, orient=tk.VERTICAL, 
                                       command=self.filter_entry.yview)
        self.filter_entry.configure(yscrollcommand=filter_scrollbar.set)
        
        self.filter_entry.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        filter_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 验证结果
        ttk.Label(parent, text="验证结果:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        self.validation_label = ttk.Label(parent, text="", foreground="green")
        self.validation_label.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # 过滤器帮助
        help_frame = ttk.LabelFrame(parent, text="常用过滤器示例", padding="5")
        help_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        help_frame.columnconfigure(0, weight=1)
        
        help_text = tk.Text(help_frame, height=8, width=70, wrap=tk.WORD, state=tk.DISABLED)
        help_scrollbar = ttk.Scrollbar(help_frame, orient=tk.VERTICAL, command=help_text.yview)
        help_text.configure(yscrollcommand=help_scrollbar.set)
        
        help_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        help_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 添加帮助内容
        help_content = """常用BPF过滤器示例:

• host 192.168.1.1          - 捕获与指定主机的通信
• net 192.168.1.0/24        - 捕获指定网络的流量
• port 80                   - 捕获HTTP流量
• tcp port 443              - 捕获HTTPS流量
• udp port 53               - 捕获DNS流量
• icmp                      - 捕获ICMP流量
• arp                       - 捕获ARP流量
• tcp and port 22           - 捕获SSH流量
• not port 22               - 排除SSH流量
• src host 192.168.1.1      - 仅捕获来自指定主机的流量
• dst port 80 or dst port 443 - 捕获HTTP或HTTPS响应"""
        
        help_text.config(state=tk.NORMAL)
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        # 配置网格权重
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def _load_initial_values(self):
        """加载初始值"""
        # 加载网络接口
        self._refresh_interfaces()
        
        # 加载过滤器模板
        self._load_filter_templates()
        
        # 设置初始值
        self.interface_var.set(self.options.interface)
        self.filter_var.set(self.options.filter_expression)
        self.packet_count_var.set(self.options.packet_count)
        self.timeout_var.set(self.options.timeout)
        self.promiscuous_var.set(self.options.promiscuous_mode)
        self.buffer_size_var.set(self.options.buffer_size)
        self.save_file_var.set(self.options.save_to_file)
        self.output_file_var.set(self.options.output_file)
        
        # 设置过滤器文本
        if self.filter_entry:
            self.filter_entry.delete(1.0, tk.END)
            self.filter_entry.insert(1.0, self.options.filter_expression)
        
        # 更新接口信息
        self._update_interface_info()
        
        # 更新文件保存状态
        self._on_save_file_toggle()
    
    def _setup_bindings(self):
        """设置事件绑定"""
        # 接口选择变化
        self.interface_var.trace('w', lambda *args: self._on_interface_changed())
        
        # 过滤器文本变化
        if self.filter_entry:
            self.filter_entry.bind('<KeyRelease>', self._on_filter_changed)
            self.filter_entry.bind('<FocusOut>', self._on_filter_changed)
    
    def _refresh_interfaces(self):
        """刷新网络接口列表"""
        try:
            interfaces = self.interface_provider.get_capture_suitable_interfaces()
            
            interface_list = []
            for iface in interfaces:
                display_text = f"{iface.display_name} ({iface.name})"
                if iface.ip_address:
                    display_text += f" - {iface.ip_address}"
                interface_list.append((display_text, iface.name))
            
            # 更新下拉列表
            if self.interface_combo:
                self.interface_combo['values'] = [item[0] for item in interface_list]
                
                # 如果当前选择的接口不在列表中，选择第一个
                current = self.interface_var.get()
                if current and not any(item[1] == current for item in interface_list):
                    if interface_list:
                        self.interface_var.set(interface_list[0][1])
                elif not current and interface_list:
                    self.interface_var.set(interface_list[0][1])
            
            self.logger.info(f"刷新了 {len(interfaces)} 个网络接口")
            
        except Exception as e:
            self.logger.error(f"刷新网络接口失败: {e}")
            messagebox.showerror("错误", f"刷新网络接口失败: {e}")
    
    def _load_filter_templates(self):
        """加载过滤器模板"""
        try:
            templates = self.filter_manager.get_all_templates()
            
            template_list = ["选择模板..."]
            for template in templates:
                display_text = f"{template.name} - {template.description}"
                template_list.append(display_text)
            
            if self.filter_combo:
                self.filter_combo['values'] = template_list
                self.filter_combo.current(0)
            
        except Exception as e:
            self.logger.error(f"加载过滤器模板失败: {e}")
    
    def _on_interface_changed(self):
        """接口选择变化处理"""
        self._update_interface_info()
        
        if self.on_interface_change:
            self.on_interface_change(self.interface_var.get())
    
    def _update_interface_info(self):
        """更新接口信息显示"""
        interface_name = self.interface_var.get()
        
        if not interface_name or not self.interface_info_text:
            return
        
        try:
            # 从显示文本中提取接口名称
            if " (" in interface_name and ")" in interface_name:
                actual_name = interface_name.split(" (")[1].split(")")[0]
            else:
                actual_name = interface_name
            
            info = self.interface_provider.get_interface_by_name(actual_name)
            
            self.interface_info_text.config(state=tk.NORMAL)
            self.interface_info_text.delete(1.0, tk.END)
            
            if info:
                formatted_info = self.interface_provider.format_interface_info(info)
                self.interface_info_text.insert(1.0, formatted_info)
            else:
                self.interface_info_text.insert(1.0, "无法获取接口信息")
            
            self.interface_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"更新接口信息失败: {e}")
    
    def _on_filter_changed(self, event=None):
        """过滤器文本变化处理"""
        if not self.filter_entry or not self.validation_label:
            return
        
        filter_text = self.filter_entry.get(1.0, tk.END).strip()
        
        # 验证过滤器
        if filter_text:
            is_valid, message = self.bpf_validator.validate_filter(filter_text)
            
            if is_valid:
                self.validation_label.config(text="✓ 过滤器语法正确", foreground="green")
            else:
                self.validation_label.config(text=f"✗ {message}", foreground="red")
        else:
            self.validation_label.config(text="", foreground="black")
        
        if self.on_filter_change:
            self.on_filter_change(filter_text)
    
    def _apply_filter_template(self):
        """应用过滤器模板"""
        if not self.filter_combo or not self.filter_entry:
            return
        
        selection = self.filter_combo.get()
        if not selection or selection == "选择模板...":
            return
        
        try:
            # 解析模板名称
            template_name = selection.split(" - ")[0]
            template = self.filter_manager.get_template_by_name(template_name)
            
            if template:
                self.filter_entry.delete(1.0, tk.END)
                self.filter_entry.insert(1.0, template.filter_expression)
                
                # 增加使用次数
                self.filter_manager.increment_usage(template_name)
                
                # 触发验证
                self._on_filter_changed()
            
        except Exception as e:
            self.logger.error(f"应用过滤器模板失败: {e}")
            messagebox.showerror("错误", f"应用过滤器模板失败: {e}")
    
    def _manage_filter_templates(self):
        """管理过滤器模板"""
        # TODO: 实现模板管理对话框
        messagebox.showinfo("提示", "过滤器模板管理功能将在后续版本中实现")
    
    def _on_save_file_toggle(self):
        """保存文件选项切换处理"""
        enabled = self.save_file_var.get()
        
        if hasattr(self, 'output_file_entry'):
            self.output_file_entry.config(state=tk.NORMAL if enabled else tk.DISABLED)
        
        if hasattr(self, 'browse_button'):
            self.browse_button.config(state=tk.NORMAL if enabled else tk.DISABLED)
    
    def _browse_output_file(self):
        """浏览输出文件"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".pcap",
            filetypes=[
                ("PCAP文件", "*.pcap"),
                ("PCAPNG文件", "*.pcapng"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            self.output_file_var.set(filename)
    
    def _center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        
        # 获取对话框尺寸
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 获取父窗口位置和尺寸
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _validate_options(self) -> bool:
        """验证选项设置"""
        # 检查接口
        if not self.interface_var.get():
            messagebox.showerror("错误", "请选择网络接口")
            return False
        
        # 检查数据包数量
        if self.packet_count_var.get() < 0:
            messagebox.showerror("错误", "数据包数量不能为负数")
            return False
        
        # 检查超时时间
        if self.timeout_var.get() < 0:
            messagebox.showerror("错误", "超时时间不能为负数")
            return False
        
        # 检查缓冲区大小
        if self.buffer_size_var.get() < 1024:
            messagebox.showerror("错误", "缓冲区大小不能小于1024字节")
            return False
        
        # 检查过滤器
        if self.filter_entry:
            filter_text = self.filter_entry.get(1.0, tk.END).strip()
            if filter_text:
                is_valid, message = self.bpf_validator.validate_filter(filter_text)
                if not is_valid:
                    messagebox.showerror("错误", f"BPF过滤器无效: {message}")
                    return False
        
        # 检查输出文件
        if self.save_file_var.get():
            output_file = self.output_file_var.get().strip()
            if not output_file:
                messagebox.showerror("错误", "请指定输出文件路径")
                return False
        
        return True
    
    def _collect_options(self) -> CaptureOptions:
        """收集用户选择的选项"""
        # 获取实际的接口名称
        interface_display = self.interface_var.get()
        if " (" in interface_display and ")" in interface_display:
            interface_name = interface_display.split(" (")[1].split(")")[0]
        else:
            interface_name = interface_display
        
        # 获取过滤器表达式
        filter_expression = ""
        if self.filter_entry:
            filter_expression = self.filter_entry.get(1.0, tk.END).strip()
        
        return CaptureOptions(
            interface=interface_name,
            filter_expression=filter_expression,
            packet_count=self.packet_count_var.get(),
            timeout=self.timeout_var.get(),
            promiscuous_mode=self.promiscuous_var.get(),
            buffer_size=self.buffer_size_var.get(),
            save_to_file=self.save_file_var.get(),
            output_file=self.output_file_var.get().strip()
        )
    
    def _on_ok(self):
        """确定按钮处理"""
        if self._validate_options():
            self.result = self._collect_options()
            self.dialog.destroy()
    
    def _on_cancel(self):
        """取消按钮处理"""
        self.result = None
        self.dialog.destroy()
    
    def _on_reset(self):
        """重置按钮处理"""
        # 重置为默认选项
        default_options = self._create_default_options()
        
        self.interface_var.set(default_options.interface)
        self.packet_count_var.set(default_options.packet_count)
        self.timeout_var.set(default_options.timeout)
        self.promiscuous_var.set(default_options.promiscuous_mode)
        self.buffer_size_var.set(default_options.buffer_size)
        self.save_file_var.set(default_options.save_to_file)
        self.output_file_var.set(default_options.output_file)
        
        if self.filter_entry:
            self.filter_entry.delete(1.0, tk.END)
            self.filter_entry.insert(1.0, default_options.filter_expression)
        
        # 更新界面状态
        self._update_interface_info()
        self._on_save_file_toggle()
        self._on_filter_changed()


def show_capture_options_dialog(parent: tk.Tk, settings: Settings, 
                               initial_options: Optional[CaptureOptions] = None) -> Optional[CaptureOptions]:
    """
    显示捕获选项对话框的便捷函数
    
    Args:
        parent: 父窗口
        settings: 应用设置
        initial_options: 初始选项
        
    Returns:
        用户选择的捕获选项，如果取消则返回None
    """
    dialog = CaptureOptionsDialog(parent, settings, initial_options)
    return dialog.show_dialog()