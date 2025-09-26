"""
报告生成对话框

提供用户友好的报告生成界面，包括：
- 会话选择
- 格式选择
- 配置选项
- 进度显示
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from ...reports.report_generator import ReportGenerator, ReportConfig, ReportFormat
from ...storage.data_manager import DataManager


logger = logging.getLogger(__name__)


class ReportGenerationDialog:
    """报告生成对话框"""
    
    def __init__(self, parent: tk.Tk, data_manager: DataManager):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            data_manager: 数据管理器
        """
        self.parent = parent
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # 初始化报告生成器
        self.report_generator = ReportGenerator(data_manager)
        
        # 对话框变量
        self.dialog = None
        self.selected_session_id = None
        self.config = ReportConfig()
        
        # 界面变量
        self.format_vars = {}
        self.progress_var = None
        self.status_var = None
        self.generation_thread = None
    
    def show(self):
        """显示对话框"""
        try:
            self._create_dialog()
            self._load_sessions()
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
            self.dialog.focus_set()
            
            # 居中显示
            self._center_dialog()
            
        except Exception as e:
            self.logger.error(f"显示报告生成对话框失败: {e}")
            messagebox.showerror("错误", f"无法打开报告生成对话框: {e}")
    
    def _create_dialog(self):
        """创建对话框界面"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("生成报告")
        self.dialog.geometry("700x650")
        self.dialog.resizable(True, True)
        self.dialog.minsize(650, 600)
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重，使主框架能够响应窗口大小变化
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 会话选择区域
        self._create_session_selection(main_frame)
        
        # 格式选择区域
        self._create_format_selection(main_frame)
        
        # 配置选项区域
        self._create_config_options(main_frame)
        
        # 进度显示区域
        self._create_progress_section(main_frame)
        
        # 按钮区域
        self._create_buttons(main_frame)
    
    def _create_session_selection(self, parent: ttk.Frame):
        """创建会话选择区域"""
        # 会话选择标签框
        session_frame = ttk.LabelFrame(parent, text="选择会话", padding="10")
        session_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 会话列表
        self.session_listbox = tk.Listbox(session_frame, height=6)
        self.session_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        session_scrollbar = ttk.Scrollbar(session_frame, orient="vertical", command=self.session_listbox.yview)
        session_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.session_listbox.configure(yscrollcommand=session_scrollbar.set)
        
        # 会话信息显示
        self.session_info_var = tk.StringVar(value="请选择一个会话")
        session_info_label = ttk.Label(session_frame, textvariable=self.session_info_var, 
                                     foreground="blue")
        session_info_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 绑定选择事件
        self.session_listbox.bind('<<ListboxSelect>>', self._on_session_select)
        
        # 配置列权重
        session_frame.columnconfigure(0, weight=1)
    
    def _create_format_selection(self, parent: ttk.Frame):
        """创建格式选择区域"""
        format_frame = ttk.LabelFrame(parent, text="输出格式", padding="10")
        format_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10), padx=(0, 5))
        
        # 格式选择复选框
        formats = [
            ("PDF报告", ReportFormat.PDF),
            ("HTML报告", ReportFormat.HTML),
            ("CSV数据", ReportFormat.CSV)
        ]
        
        for i, (text, format_type) in enumerate(formats):
            var = tk.BooleanVar(value=(format_type == ReportFormat.PDF))
            self.format_vars[format_type] = var
            
            checkbox = ttk.Checkbutton(format_frame, text=text, variable=var)
            checkbox.grid(row=i, column=0, sticky=tk.W, pady=2)
    
    def _create_config_options(self, parent: ttk.Frame):
        """创建配置选项区域"""
        config_frame = ttk.LabelFrame(parent, text="配置选项", padding="10")
        config_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=(5, 0))
        
        # 包含图表选项
        self.include_charts_var = tk.BooleanVar(value=True)
        charts_checkbox = ttk.Checkbutton(config_frame, text="包含统计图表", 
                                        variable=self.include_charts_var)
        charts_checkbox.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # 包含详细统计选项
        self.include_details_var = tk.BooleanVar(value=True)
        details_checkbox = ttk.Checkbutton(config_frame, text="包含详细统计", 
                                         variable=self.include_details_var)
        details_checkbox.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 输出目录选择
        ttk.Label(config_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        
        dir_frame = ttk.Frame(config_frame)
        dir_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "reports"))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=30)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        dir_button = ttk.Button(dir_frame, text="浏览", command=self._browse_output_dir)
        dir_button.grid(row=0, column=1, padx=(5, 0))
        
        dir_frame.columnconfigure(0, weight=1)
        
        # 配置列权重
        config_frame.columnconfigure(0, weight=1)
    
    def _create_progress_section(self, parent: ttk.Frame):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="生成进度", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                     maximum=100, length=400)
        progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 进度百分比
        self.progress_text_var = tk.StringVar(value="0%")
        progress_text = ttk.Label(progress_frame, textvariable=self.progress_text_var)
        progress_text.grid(row=1, column=1, padx=(10, 0))
        
        progress_frame.columnconfigure(0, weight=1)
    
    def _create_buttons(self, parent: ttk.Frame):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # 生成按钮
        self.generate_button = ttk.Button(button_frame, text="生成报告", 
                                        command=self._start_generation)
        self.generate_button.grid(row=0, column=0, padx=(0, 10))
        
        # 预览按钮
        self.preview_button = ttk.Button(button_frame, text="预览信息", 
                                       command=self._show_preview)
        self.preview_button.grid(row=0, column=1, padx=(0, 10))
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self._close_dialog)
        cancel_button.grid(row=0, column=2)
    
    def _load_sessions(self):
        """加载会话列表"""
        try:
            sessions = self.report_generator.get_available_sessions()
            
            self.session_listbox.delete(0, tk.END)
            self.sessions_data = {}
            
            for session in sessions:
                session_id = session.get('id')
                session_name = session.get('name', f'会话_{session_id}')
                packet_count = session.get('packet_count', 0)
                
                display_text = f"{session_name} ({packet_count:,} 包)"
                self.session_listbox.insert(tk.END, display_text)
                self.sessions_data[len(self.sessions_data)] = session
            
            if not sessions:
                self.session_listbox.insert(tk.END, "没有可用的会话")
                self.generate_button.configure(state="disabled")
                self.preview_button.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"加载会话列表失败: {e}")
            messagebox.showerror("错误", f"加载会话列表失败: {e}")
    
    def _on_session_select(self, event):
        """会话选择事件处理"""
        try:
            selection = self.session_listbox.curselection()
            if selection:
                index = selection[0]
                session = self.sessions_data.get(index)
                
                if session:
                    self.selected_session_id = session.get('id')
                    
                    # 更新会话信息显示
                    info_text = (f"会话ID: {session.get('id')} | "
                               f"数据包: {session.get('packet_count', 0):,} | "
                               f"创建时间: {session.get('created_time', 'N/A')}")
                    self.session_info_var.set(info_text)
                    
                    # 启用按钮
                    self.generate_button.configure(state="normal")
                    self.preview_button.configure(state="normal")
                else:
                    self.selected_session_id = None
                    self.session_info_var.set("请选择一个会话")
                    self.generate_button.configure(state="disabled")
                    self.preview_button.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"处理会话选择失败: {e}")
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        try:
            directory = filedialog.askdirectory(
                title="选择输出目录",
                initialdir=self.output_dir_var.get()
            )
            
            if directory:
                self.output_dir_var.set(directory)
                
        except Exception as e:
            self.logger.error(f"浏览输出目录失败: {e}")
    
    def _show_preview(self):
        """显示报告预览信息"""
        try:
            if not self.selected_session_id:
                messagebox.showwarning("警告", "请先选择一个会话")
                return
            
            # 获取预览信息
            preview = self.report_generator.get_report_preview(self.selected_session_id)
            
            if not preview.get('valid', False):
                messagebox.showerror("错误", f"无法预览报告: {preview.get('error', '未知错误')}")
                return
            
            # 显示预览信息
            preview_text = f"""报告预览信息:

会话名称: {preview.get('session_name', 'N/A')}
数据包数量: {preview.get('packet_count', 0):,}
持续时间: {preview.get('duration', 0):.2f} 秒
协议类型: {preview.get('protocol_count', 0)} 种

预估文件大小:
• PDF: {preview.get('estimated_size', {}).get('pdf', 'N/A')}
• HTML: {preview.get('estimated_size', {}).get('html', 'N/A')}
• CSV: {preview.get('estimated_size', {}).get('csv', 'N/A')}

预估生成时间: {preview.get('estimated_time', 'N/A')}"""
            
            messagebox.showinfo("报告预览", preview_text)
            
        except Exception as e:
            self.logger.error(f"显示预览失败: {e}")
            messagebox.showerror("错误", f"获取预览信息失败: {e}")
    
    def _start_generation(self):
        """开始生成报告"""
        try:
            if not self.selected_session_id:
                messagebox.showwarning("警告", "请先选择一个会话")
                return
            
            # 验证格式选择
            selected_formats = []
            for format_type, var in self.format_vars.items():
                if var.get():
                    selected_formats.append(format_type)
            
            if not selected_formats:
                messagebox.showwarning("警告", "请至少选择一种输出格式")
                return
            
            # 更新配置
            self.config.formats = selected_formats
            self.config.include_charts = self.include_charts_var.get()
            self.config.include_detailed_stats = self.include_details_var.get()
            self.config.output_dir = self.output_dir_var.get()
            
            # 禁用生成按钮
            self.generate_button.configure(state="disabled")
            self.preview_button.configure(state="disabled")
            
            # 设置进度回调
            self.report_generator.set_progress_callback(self._update_progress)
            
            # 在新线程中生成报告
            self.generation_thread = threading.Thread(
                target=self._generate_report_thread,
                daemon=True
            )
            self.generation_thread.start()
            
        except Exception as e:
            self.logger.error(f"启动报告生成失败: {e}")
            messagebox.showerror("错误", f"启动报告生成失败: {e}")
            self._reset_ui()
    
    def _generate_report_thread(self):
        """报告生成线程"""
        try:
            # 生成报告
            result = self.report_generator.generate_report(
                self.selected_session_id, 
                self.config
            )
            
            # 在主线程中显示结果
            self.dialog.after(0, lambda: self._on_generation_complete(result))
            
        except Exception as e:
            self.logger.error(f"报告生成线程失败: {e}")
            # 在主线程中显示错误
            self.dialog.after(0, lambda: self._on_generation_error(str(e)))
    
    def _update_progress(self, message: str, progress: float):
        """更新进度显示"""
        try:
            # 在主线程中更新UI
            self.dialog.after(0, lambda: self._update_progress_ui(message, progress))
        except Exception as e:
            self.logger.error(f"更新进度失败: {e}")
    
    def _update_progress_ui(self, message: str, progress: float):
        """在主线程中更新进度UI"""
        try:
            self.status_var.set(message)
            self.progress_var.set(progress * 100)
            self.progress_text_var.set(f"{progress * 100:.0f}%")
        except Exception as e:
            self.logger.error(f"更新进度UI失败: {e}")
    
    def _on_generation_complete(self, result: Dict[str, Any]):
        """报告生成完成处理"""
        try:
            generated_files = result.get('generated_files', {})
            
            # 构建成功消息
            success_message = "报告生成成功！\\n\\n生成的文件："
            for file_type, file_path in generated_files.items():
                filename = Path(file_path).name
                success_message += f"\\n• {file_type.upper()}: {filename}"
            
            success_message += f"\\n\\n输出目录: {self.config.output_dir}"
            
            messagebox.showinfo("成功", success_message)
            
            # 询问是否打开输出目录
            if messagebox.askyesno("打开目录", "是否打开输出目录查看生成的报告？"):
                self._open_output_directory()
            
            self._close_dialog()
            
        except Exception as e:
            self.logger.error(f"处理生成完成失败: {e}")
            self._on_generation_error(str(e))
    
    def _on_generation_error(self, error_message: str):
        """报告生成错误处理"""
        try:
            messagebox.showerror("生成失败", f"报告生成失败:\\n{error_message}")
            self._reset_ui()
        except Exception as e:
            self.logger.error(f"处理生成错误失败: {e}")
    
    def _reset_ui(self):
        """重置UI状态"""
        try:
            self.generate_button.configure(state="normal")
            self.preview_button.configure(state="normal")
            self.status_var.set("准备就绪")
            self.progress_var.set(0)
            self.progress_text_var.set("0%")
        except Exception as e:
            self.logger.error(f"重置UI失败: {e}")
    
    def _open_output_directory(self):
        """打开输出目录"""
        try:
            import subprocess
            import sys
            
            output_dir = self.config.output_dir
            
            if sys.platform == "win32":
                subprocess.run(["explorer", output_dir])
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
                
        except Exception as e:
            self.logger.error(f"打开输出目录失败: {e}")
    
    def _center_dialog(self):
        """居中显示对话框"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"居中对话框失败: {e}")
    
    def _close_dialog(self):
        """关闭对话框"""
        try:
            if self.generation_thread and self.generation_thread.is_alive():
                # 如果生成线程还在运行，询问是否取消
                if messagebox.askyesno("确认", "报告正在生成中，确定要取消吗？"):
                    self.dialog.destroy()
                return
            
            self.dialog.destroy()
            
        except Exception as e:
            self.logger.error(f"关闭对话框失败: {e}")


def show_report_generation_dialog(parent: tk.Tk, data_manager: DataManager):
    """
    显示报告生成对话框
    
    Args:
        parent: 父窗口
        data_manager: 数据管理器
    """
    try:
        dialog = ReportGenerationDialog(parent, data_manager)
        dialog.show()
    except Exception as e:
        logger.error(f"显示报告生成对话框失败: {e}")
        messagebox.showerror("错误", f"无法打开报告生成对话框: {e}")