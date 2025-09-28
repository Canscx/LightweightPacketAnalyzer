"""
主题设置选项卡模块

实现主题选择和切换的GUI组件，支持4个主题分组
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional, Callable

try:
    import ttkbootstrap
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False

from ...gui.theme_manager import theme_manager


class ThemeSettingsTab:
    """主题设置选项卡类"""
    
    def __init__(self, parent_frame: ttk.Frame, config_vars: Dict[str, Any], settings, main_window=None):
        """
        初始化主题设置选项卡
        
        Args:
            parent_frame: 父框架
            config_vars: 配置变量字典
            settings: Settings实例
            main_window: 主窗口引用（用于实时预览）
        """
        self.parent_frame = parent_frame
        self.config_vars = config_vars
        self.settings = settings
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # 主题变量
        self.theme_var = tk.StringVar(value=settings.THEME)
        self.category_var = tk.StringVar(value=settings.THEME_CATEGORY)
        
        # 主题分组框架
        self.theme_groups = {}
        self.theme_buttons = {}
        
        # 预览相关
        self.preview_enabled = tk.BooleanVar(value=True)
        self.preview_window = None
        
        # 创建UI
        self._create_scrollable_frame()
        self._create_theme_groups()
        self._create_preview_section()
        self._create_control_section()
        
        # 绑定事件
        self._setup_bindings()
    
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
    
    def _create_theme_groups(self):
        """创建主题分组"""
        # 获取主题分组
        groups = theme_manager.get_theme_groups()
        
        # 分组标题和描述
        group_info = {
            'light': {
                'title': '浅色主题',
                'description': '明亮清新的主题，适合白天使用',
                'color': '#e3f2fd'
            },
            'dark': {
                'title': '暗色主题', 
                'description': '深色护眼的主题，适合夜间使用',
                'color': '#263238'
            },
            'colorful': {
                'title': 'Colorful主题',
                'description': '五彩斑斓的主题，丰富多彩的视觉体验',
                'color': '#f3e5f5'
            },
            'classic': {
                'title': 'Windows经典风格',
                'description': '传统的Windows系统主题风格',
                'color': '#f5f5f5'
            }
        }
        
        # 创建每个主题分组
        for group_name, themes in groups.items():
            if not themes:  # 跳过空分组
                continue
                
            info = group_info.get(group_name, {})
            self._create_theme_group(
                group_name, 
                themes, 
                info.get('title', group_name.title()),
                info.get('description', ''),
                info.get('color', '#ffffff')
            )
    
    def _create_theme_group(self, group_name: str, themes: list, title: str, description: str, bg_color: str):
        """
        创建单个主题分组
        
        Args:
            group_name: 分组名称
            themes: 主题列表
            title: 分组标题
            description: 分组描述
            bg_color: 背景颜色
        """
        # 创建分组框架
        group_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="10")
        group_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 分组描述
        desc_label = ttk.Label(group_frame, text=description, font=("Arial", 9))
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 主题按钮容器
        themes_frame = ttk.Frame(group_frame)
        themes_frame.pack(fill=tk.X)
        
        # 创建主题按钮（每行最多4个）
        self.theme_buttons[group_name] = []
        for i, theme in enumerate(themes):
            row = i // 4
            col = i % 4
            
            # 创建主题按钮框架
            theme_frame = ttk.Frame(themes_frame)
            theme_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # 配置列权重
            themes_frame.columnconfigure(col, weight=1)
            
            # 主题单选按钮
            theme_radio = ttk.Radiobutton(
                theme_frame,
                text=theme_manager.get_theme_display_name(theme),
                variable=self.theme_var,
                value=theme,
                command=lambda t=theme, c=group_name: self._on_theme_change(t, c)
            )
            theme_radio.pack(anchor=tk.W)
            
            # 主题描述
            theme_desc = ttk.Label(
                theme_frame,
                text=theme_manager.get_theme_description(theme),
                font=("Arial", 8),
                foreground="gray"
            )
            theme_desc.pack(anchor=tk.W)
            
            self.theme_buttons[group_name].append(theme_radio)
        
        self.theme_groups[group_name] = group_frame
    
    def _create_preview_section(self):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(self.scrollable_frame, text="主题预览", padding="10")
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 预览控制
        control_frame = ttk.Frame(preview_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 实时预览开关
        preview_check = ttk.Checkbutton(
            control_frame,
            text="启用实时预览",
            variable=self.preview_enabled,
            command=self._toggle_preview
        )
        preview_check.pack(side=tk.LEFT)
        
        # 预览按钮
        preview_btn = ttk.Button(
            control_frame,
            text="预览主题",
            command=self._preview_theme
        )
        preview_btn.pack(side=tk.RIGHT)
        
        # 当前主题信息
        self.current_theme_frame = ttk.Frame(preview_frame)
        self.current_theme_frame.pack(fill=tk.X)
        
        self._update_current_theme_info()
    
    def _create_control_section(self):
        """创建控制区域"""
        control_frame = ttk.LabelFrame(self.scrollable_frame, text="主题控制", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        # 重置按钮
        reset_btn = ttk.Button(
            btn_frame,
            text="重置为默认",
            command=self._reset_to_default
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 应用按钮
        apply_btn = ttk.Button(
            btn_frame,
            text="立即应用",
            command=self._apply_theme
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            btn_frame,
            text="刷新主题",
            command=self._refresh_themes
        )
        refresh_btn.pack(side=tk.RIGHT)
    
    def _setup_bindings(self):
        """设置事件绑定"""
        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # 主题变量变化绑定
        self.theme_var.trace('w', self._on_theme_var_change)
    
    def _on_theme_change(self, theme: str, category: str):
        """
        主题变化回调
        
        Args:
            theme: 主题名称
            category: 主题分类
        """
        try:
            self.logger.info(f"主题变化: {theme} ({category})")
            
            # 更新分类变量
            self.category_var.set(category)
            
            # 更新配置变量
            if 'THEME' in self.config_vars:
                self.config_vars['THEME'].set(theme)
            if 'THEME_CATEGORY' in self.config_vars:
                self.config_vars['THEME_CATEGORY'].set(category)
            
            # 更新当前主题信息
            self._update_current_theme_info()
            
            # 实时预览
            if self.preview_enabled.get():
                self._preview_theme()
                
        except Exception as e:
            self.logger.error(f"主题变化处理失败: {e}")
    
    def _on_theme_var_change(self, *args):
        """主题变量变化回调"""
        theme = self.theme_var.get()
        if theme:
            category = theme_manager.get_theme_category(theme)
            self._on_theme_change(theme, category)
    
    def _update_current_theme_info(self):
        """更新当前主题信息显示"""
        try:
            # 清空现有信息
            for widget in self.current_theme_frame.winfo_children():
                widget.destroy()
            
            theme = self.theme_var.get()
            if not theme:
                return
            
            # 主题信息
            info_frame = ttk.Frame(self.current_theme_frame)
            info_frame.pack(fill=tk.X, pady=5)
            
            # 当前主题标签
            current_label = ttk.Label(
                info_frame,
                text=f"当前选择: {theme_manager.get_theme_display_name(theme)}",
                font=("Arial", 10, "bold")
            )
            current_label.pack(side=tk.LEFT)
            
            # 主题分类标签
            category = theme_manager.get_theme_category(theme)
            category_label = ttk.Label(
                info_frame,
                text=f"分类: {category}",
                font=("Arial", 9)
            )
            category_label.pack(side=tk.RIGHT)
            
            # 主题描述
            desc_label = ttk.Label(
                self.current_theme_frame,
                text=theme_manager.get_theme_description(theme),
                font=("Arial", 9),
                foreground="gray"
            )
            desc_label.pack(anchor=tk.W)
            
        except Exception as e:
            self.logger.error(f"更新主题信息失败: {e}")
    
    def _toggle_preview(self):
        """切换预览模式"""
        if self.preview_enabled.get():
            self.logger.info("启用实时预览")
            self._preview_theme()
        else:
            self.logger.info("禁用实时预览")
            self._close_preview()
    
    def _preview_theme(self):
        """预览主题"""
        try:
            theme = self.theme_var.get()
            if not theme:
                return
            
            if self.main_window and hasattr(self.main_window, 'apply_theme'):
                # 在主窗口中预览
                self.main_window.apply_theme(theme)
                self.logger.info(f"在主窗口预览主题: {theme}")
            else:
                # 创建预览窗口
                self._create_preview_window(theme)
                
        except Exception as e:
            self.logger.error(f"预览主题失败: {e}")
            messagebox.showerror("预览失败", f"预览主题失败: {e}")
    
    def _create_preview_window(self, theme: str):
        """
        创建预览窗口
        
        Args:
            theme: 要预览的主题
        """
        try:
            # 关闭现有预览窗口
            self._close_preview()
            
            if not TTKBOOTSTRAP_AVAILABLE:
                messagebox.showwarning("预览不可用", "ttkbootstrap不可用，无法创建预览窗口")
                return
            
            # 创建预览窗口
            import ttkbootstrap as ttk_bs
            self.preview_window = ttk_bs.Window(themename=theme)
            self.preview_window.title(f"主题预览 - {theme_manager.get_theme_display_name(theme)}")
            self.preview_window.geometry("400x300")
            
            # 添加示例组件
            self._add_preview_components()
            
            # 设置窗口关闭事件
            self.preview_window.protocol("WM_DELETE_WINDOW", self._close_preview)
            
        except Exception as e:
            self.logger.error(f"创建预览窗口失败: {e}")
    
    def _add_preview_components(self):
        """添加预览组件"""
        if not self.preview_window:
            return
        
        try:
            # 主框架
            main_frame = ttk.Frame(self.preview_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = ttk.Label(
                main_frame,
                text="主题预览",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 20))
            
            # 按钮组
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(btn_frame, text="Primary", bootstyle="primary").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Secondary", bootstyle="secondary").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Success", bootstyle="success").pack(side=tk.LEFT, padx=5)
            
            # 输入组件
            input_frame = ttk.Frame(main_frame)
            input_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(input_frame, text="输入框:").pack(anchor=tk.W)
            entry = ttk.Entry(input_frame)
            entry.pack(fill=tk.X, pady=5)
            entry.insert(0, "示例文本")
            
            # 进度条
            ttk.Label(main_frame, text="进度条:").pack(anchor=tk.W, pady=(10, 5))
            progress = ttk.Progressbar(main_frame, value=60)
            progress.pack(fill=tk.X)
            
        except Exception as e:
            self.logger.error(f"添加预览组件失败: {e}")
    
    def _close_preview(self):
        """关闭预览窗口"""
        if self.preview_window:
            try:
                self.preview_window.destroy()
                self.preview_window = None
            except:
                pass
    
    def _apply_theme(self):
        """立即应用主题"""
        try:
            theme = self.theme_var.get()
            category = self.category_var.get()
            
            if not theme:
                messagebox.showwarning("警告", "请先选择一个主题")
                return
            
            # 验证主题
            if not theme_manager.validate_theme(theme):
                messagebox.showerror("错误", f"主题 {theme} 无效")
                return
            
            # 保存配置
            success = self.settings.save_theme_config(theme, category)
            if not success:
                messagebox.showerror("错误", "保存主题配置失败")
                return
            
            # 应用到主窗口
            if self.main_window and hasattr(self.main_window, 'apply_theme'):
                self.main_window.apply_theme(theme)
            
            messagebox.showinfo("成功", f"主题 {theme_manager.get_theme_display_name(theme)} 已应用")
            self.logger.info(f"主题已应用: {theme}")
            
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
            messagebox.showerror("错误", f"应用主题失败: {e}")
    
    def _reset_to_default(self):
        """重置为默认主题"""
        try:
            default_theme = theme_manager.DEFAULT_THEME
            default_category = theme_manager.get_theme_category(default_theme)
            
            self.theme_var.set(default_theme)
            self.category_var.set(default_category)
            
            self.logger.info(f"已重置为默认主题: {default_theme}")
            
        except Exception as e:
            self.logger.error(f"重置主题失败: {e}")
    
    def _refresh_themes(self):
        """刷新主题列表"""
        try:
            # 重新创建主题分组
            for group_frame in self.theme_groups.values():
                group_frame.destroy()
            
            self.theme_groups.clear()
            self.theme_buttons.clear()
            
            # 重新创建
            self._create_theme_groups()
            
            # 更新当前选择
            current_theme = self.theme_var.get()
            if current_theme and theme_manager.validate_theme(current_theme):
                self.theme_var.set(current_theme)
            else:
                self.theme_var.set(theme_manager.DEFAULT_THEME)
            
            self.logger.info("主题列表已刷新")
            
        except Exception as e:
            self.logger.error(f"刷新主题失败: {e}")
    
    def get_current_config(self) -> Dict[str, str]:
        """
        获取当前配置
        
        Returns:
            Dict: 当前主题配置
        """
        return {
            'theme': self.theme_var.get(),
            'category': self.category_var.get()
        }
    
    def load_config(self, config: Dict[str, str]):
        """
        加载配置
        
        Args:
            config: 主题配置
        """
        try:
            theme = config.get('theme', theme_manager.DEFAULT_THEME)
            category = config.get('category', 'light')
            
            if theme_manager.validate_theme(theme):
                self.theme_var.set(theme)
                self.category_var.set(category)
            else:
                self.logger.warning(f"无效主题 {theme}，使用默认主题")
                self.theme_var.set(theme_manager.DEFAULT_THEME)
                self.category_var.set('light')
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self._close_preview()
        except:
            pass