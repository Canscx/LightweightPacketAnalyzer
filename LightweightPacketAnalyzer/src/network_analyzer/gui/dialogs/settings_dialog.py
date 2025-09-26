"""
设置对话框模块

提供应用程序设置的图形界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any

from ...config.settings import Settings
from .basic_settings_tab import BasicSettingsTab
from .advanced_settings_tab import AdvancedSettingsTab


class SettingsDialog:
    """设置对话框类"""
    
    def __init__(self, parent: tk.Tk, settings: Settings, main_window=None):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            settings: 配置管理器
            main_window: 主窗口引用（用于立即生效）
        """
        self.parent = parent
        self.settings = settings
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # 对话框状态
        self.dialog = None
        self.result = False  # 是否保存了设置
        
        # 配置变量存储
        self.config_vars = {}
        self.original_values = {}
        
        # UI组件引用
        self.notebook = None
        self.basic_tab = None
        self.advanced_tab = None
        self.button_frame = None
        
        # 按钮引用
        self.ok_button = None
        self.cancel_button = None
        self.apply_button = None
        self.reset_button = None
    
    def show(self) -> bool:
        """
        显示设置对话框
        
        Returns:
            bool: 用户是否保存了设置
        """
        try:
            self._create_dialog()
            self._create_ui()
            self._load_current_settings()
            self._setup_bindings()
            
            # 模态显示
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
            
            # 居中显示
            self._center_dialog()
            
            # 等待对话框关闭
            self.dialog.wait_window()
            
            return self.result
            
        except Exception as error:
            self.logger.error(f"显示设置对话框失败: {error}")
            messagebox.showerror("错误", f"显示设置对话框失败: {error}")
            return False
    
    def _create_dialog(self) -> None:
        """创建对话框窗口"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("应用程序设置")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 400)
        
        # 设置图标（如果有的话）
        try:
            if hasattr(self.parent, 'iconbitmap'):
                self.dialog.iconbitmap(self.parent.iconbitmap())
        except:
            pass
        
        # 处理关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_ui(self) -> None:
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建基础设置选项卡
        self._create_basic_tab()
        
        # 创建高级设置选项卡
        self._create_advanced_tab()
        
        # 创建按钮框架
        self._create_button_frame(main_frame)
    
    def _create_basic_tab(self) -> None:
        """创建基础设置选项卡"""
        self.basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_tab, text="基础设置")
        
        # 创建基础设置选项卡内容
        self.basic_settings_tab = BasicSettingsTab(self.basic_tab, self.config_vars, self.settings)
    
    def _create_advanced_tab(self) -> None:
        """创建高级设置选项卡"""
        self.advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="高级设置")
        
        # 创建高级设置选项卡内容
        self.advanced_settings_tab = AdvancedSettingsTab(self.advanced_tab, self.config_vars, self.settings)
    
    def _create_button_frame(self, parent: ttk.Frame) -> None:
        """创建按钮框架"""
        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 右侧按钮组
        right_buttons = ttk.Frame(self.button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        # 确定按钮
        self.ok_button = ttk.Button(
            right_buttons, 
            text="确定", 
            command=self._on_ok,
            width=10
        )
        self.ok_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 取消按钮
        self.cancel_button = ttk.Button(
            right_buttons, 
            text="取消", 
            command=self._on_cancel,
            width=10
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 应用按钮
        self.apply_button = ttk.Button(
            right_buttons, 
            text="应用", 
            command=self._on_apply,
            width=10
        )
        self.apply_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 左侧重置按钮
        self.reset_button = ttk.Button(
            self.button_frame, 
            text="重置到默认值", 
            command=self._on_reset,
            width=15
        )
        self.reset_button.pack(side=tk.LEFT)
    
    def _load_current_settings(self) -> None:
        """加载当前配置到界面"""
        # 保存原始值用于取消操作
        self.original_values = self.settings.to_dict()
        
        # 配置变量初始化将在T3和T4中实现
        self.logger.info("当前配置已加载到设置对话框")
    
    def _setup_bindings(self) -> None:
        """设置键盘绑定"""
        # ESC键取消
        self.dialog.bind('<Escape>', lambda event: self._on_cancel())
        
        # Enter键确定（当焦点不在多行文本框时）
        self.dialog.bind('<Return>', lambda event: self._on_ok())
        
        # Ctrl+S应用设置
        self.dialog.bind('<Control-s>', lambda event: self._on_apply())
        self.dialog.bind('<Control-S>', lambda event: self._on_apply())
    
    def _center_dialog(self) -> None:
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
        
        # 确保对话框在屏幕范围内
        x = max(0, x)
        y = max(0, y)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _validate_all_settings(self) -> tuple[bool, list[str]]:
        """
        验证所有设置
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        settings_dict = self._collect_settings()
        return self.settings.validate_all_settings(settings_dict)
    
    def _collect_settings(self) -> Dict[str, Any]:
        """
        收集界面上的所有设置
        
        Returns:
            Dict: 设置字典
        """
        collected_settings = {}
        
        # 收集所有配置变量的值
        for key, var in self.config_vars.items():
            if isinstance(var, tk.IntVar):
                value = var.get()
                # 特殊处理：将KB转换为字节，MB转换为字节
                if key == 'BUFFER_SIZE':
                    value = value * 1024  # KB转字节
                elif key == 'LOG_MAX_SIZE':
                    value = value * 1024 * 1024  # MB转字节
                elif key == 'CAPTURE_BUFFER_SIZE':
                    value = value * 1024 * 1024  # MB转字节
                collected_settings[key] = value
            elif isinstance(var, tk.StringVar):
                collected_settings[key] = var.get()
            elif isinstance(var, tk.BooleanVar):
                collected_settings[key] = var.get()
        
        return collected_settings
    
    def _apply_settings(self) -> bool:
        """
        应用设置
        
        Returns:
            bool: 是否成功
        """
        try:
            # 验证设置
            is_valid, errors = self._validate_all_settings()
            if not is_valid:
                error_msg = "配置验证失败:\\n" + "\\n".join(errors)
                messagebox.showerror("配置错误", error_msg)
                return False
            
            # 收集设置
            new_settings = self._collect_settings()
            
            # 更新Settings对象
            self.settings.update_from_dict(new_settings)
            
            # 保存到文件
            success = self.settings.save_to_file()
            if not success:
                messagebox.showerror("保存失败", "无法保存配置到文件")
                return False
            
            # 应用立即生效的设置
            self._apply_immediate_settings()
            
            self.logger.info("设置已成功应用")
            return True
            
        except Exception as error:
            self.logger.error(f"应用设置失败: {error}")
            messagebox.showerror("应用失败", f"应用设置时发生错误: {error}")
            return False
    
    def _apply_immediate_settings(self) -> None:
        """应用立即生效的设置"""
        if not self.main_window:
            return
        
        try:
            immediate_settings = self.settings.get_immediate_settings()
            
            # 应用窗口大小
            if 'WINDOW_WIDTH' in immediate_settings and 'WINDOW_HEIGHT' in immediate_settings:
                width = immediate_settings['WINDOW_WIDTH']
                height = immediate_settings['WINDOW_HEIGHT']
                self.main_window.root.geometry(f"{width}x{height}")
            
            # 应用主题（如果支持）
            if 'THEME' in immediate_settings:
                theme = immediate_settings['THEME']
                try:
                    style = ttk.Style()
                    if theme in style.theme_names():
                        style.theme_use(theme)
                except Exception as theme_error:
                    self.logger.warning(f"应用主题失败: {theme_error}")
            
            self.logger.info("立即生效的设置已应用")
            
        except Exception as error:
            self.logger.error(f"应用立即生效设置失败: {error}")
    
    def _reset_to_defaults(self) -> None:
        """重置到默认值"""
        try:
            # 确认操作
            result = messagebox.askyesno(
                "确认重置", 
                "确定要将所有设置重置到默认值吗？\\n此操作无法撤销。",
                icon="warning"
            )
            
            if result:
                # 创建新的Settings实例获取默认值
                default_settings = Settings()
                
                # 更新当前Settings对象
                self.settings.update_from_dict(default_settings.to_dict())
                
                # 重新加载界面
                self._load_current_settings()
                
                messagebox.showinfo("重置完成", "所有设置已重置到默认值")
                self.logger.info("设置已重置到默认值")
                
        except Exception as error:
            self.logger.error(f"重置设置失败: {error}")
            messagebox.showerror("重置失败", f"重置设置时发生错误: {error}")
    
    def _on_ok(self) -> None:
        """确定按钮事件处理"""
        if self._apply_settings():
            self.result = True
            self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """取消按钮事件处理"""
        # 检查是否有未保存的更改
        if self._has_unsaved_changes():
            result = messagebox.askyesnocancel(
                "未保存的更改", 
                "您有未保存的更改，是否要保存？",
                icon="question"
            )
            
            if result is True:  # 保存
                if self._apply_settings():
                    self.result = True
                    self.dialog.destroy()
            elif result is False:  # 不保存
                self.result = False
                self.dialog.destroy()
            # result is None: 取消关闭
        else:
            self.result = False
            self.dialog.destroy()
    
    def _on_apply(self) -> None:
        """应用按钮事件处理"""
        if self._apply_settings():
            # 更新原始值
            self.original_values = self.settings.to_dict()
            messagebox.showinfo("应用成功", "设置已成功应用")
    
    def _on_reset(self) -> None:
        """重置按钮事件处理"""
        self._reset_to_defaults()
    
    def _has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        try:
            current_settings = self._collect_settings()
            
            # 比较当前设置与原始值
            for key, current_value in current_settings.items():
                original_value = self.original_values.get(key)
                
                # 特殊处理布尔值比较
                if isinstance(current_value, bool) and isinstance(original_value, bool):
                    if current_value != original_value:
                        return True
                # 特殊处理数值比较
                elif isinstance(current_value, (int, float)) and isinstance(original_value, (int, float)):
                    if abs(current_value - original_value) > 0.001:  # 允许小的浮点误差
                        return True
                # 字符串比较
                elif str(current_value) != str(original_value):
                    return True
            
            return False
            
        except Exception as error:
            self.logger.warning(f"检查未保存更改时发生错误: {error}")
            return False  # 出错时假设没有更改