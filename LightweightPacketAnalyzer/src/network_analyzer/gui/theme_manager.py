"""
主题管理器模块

统一管理ttkbootstrap主题切换、分组和验证功能
"""

import logging
from typing import Dict, List, Optional, Tuple
import tkinter as tk

try:
    import ttkbootstrap as ttk
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    import tkinter.ttk as ttk


class ThemeValidator:
    """主题验证器 - 验证主题有效性和分类"""
    
    @staticmethod
    def is_ttkbootstrap_theme(theme_name: str) -> bool:
        """检查是否为ttkbootstrap主题"""
        if not TTKBOOTSTRAP_AVAILABLE:
            return False
        
        # 使用已知的ttkbootstrap主题列表进行验证，避免创建窗口
        ttkbootstrap_themes = {
            # Light themes
            'litera', 'flatly', 'cosmo', 'journal', 'lumen', 'minty', 
            'pulse', 'sandstone', 'united', 'yeti', 'morph', 'simplex', 'cerulean',
            # Dark themes  
            'solar', 'superhero', 'darkly', 'cyborg', 'vapor',
            # Colorful themes
            'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark'
        }
        return theme_name in ttkbootstrap_themes
    
    @staticmethod
    def is_tkinter_theme(theme_name: str) -> bool:
        """检查是否为tkinter内置主题"""
        classic_themes = {'default', 'clam', 'alt', 'classic'}
        return theme_name in classic_themes
    
    @staticmethod
    def get_theme_category(theme_name: str) -> str:
        """获取主题分类"""
        if ThemeValidator.is_tkinter_theme(theme_name):
            return 'classic'
        
        # ttkbootstrap主题分类
        light_themes = {
            'litera', 'flatly', 'cosmo', 'journal', 'lumen',
            'minty', 'pulse', 'sandstone', 'united', 'yeti'
        }
        
        dark_themes = {
            'darkly', 'cyborg', 'slate', 'superhero', 'vapor'
        }
        
        colorful_themes = {
            'morph', 'vapor', 'superhero', 'cyborg'
        }
        
        if theme_name in light_themes:
            return 'light'
        elif theme_name in dark_themes:
            return 'dark'
        elif theme_name in colorful_themes:
            return 'colorful'
        else:
            return 'unknown'


class ThemeManager:
    """主题管理器 - 统一管理主题切换和分组"""
    
    # 主题分组定义
    LIGHT_THEMES = [
        'litera', 'flatly', 'cosmo', 'journal', 'lumen',
        'minty', 'pulse', 'sandstone', 'united', 'yeti'
    ]
    
    DARK_THEMES = [
        'darkly', 'cyborg', 'slate', 'superhero', 'vapor'
    ]
    
    COLORFUL_THEMES = [
        'morph', 'vapor', 'superhero', 'cyborg'
    ]
    
    CLASSIC_THEMES = [
        'default', 'clam', 'alt', 'classic'
    ]
    
    DEFAULT_THEME = 'litera'
    
    # 主题迁移映射
    THEME_MIGRATION_MAP = {
        'default': 'litera',
        'clam': 'flatly',
        'alt': 'cosmo',
        'classic': 'journal'
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self.logger = logging.getLogger(__name__)
        self.validator = ThemeValidator()
        self._available_themes = None
        self._theme_groups = None
    
    def get_theme_groups(self) -> Dict[str, List[str]]:
        """
        获取所有主题分组
        
        Returns:
            Dict: 主题分组字典
        """
        if self._theme_groups is None:
            self._theme_groups = {
                'light': self._filter_available_themes(self.LIGHT_THEMES),
                'dark': self._filter_available_themes(self.DARK_THEMES),
                'colorful': self._filter_available_themes(self.COLORFUL_THEMES),
                'classic': self.CLASSIC_THEMES.copy()
            }
        
        return self._theme_groups
    
    def _filter_available_themes(self, theme_list: List[str]) -> List[str]:
        """
        过滤可用的主题
        
        Args:
            theme_list: 主题列表
            
        Returns:
            List: 可用的主题列表
        """
        if not TTKBOOTSTRAP_AVAILABLE:
            return []
        
        available = []
        for theme in theme_list:
            if self.validate_theme(theme):
                available.append(theme)
        
        return available
    
    def get_available_themes(self) -> List[str]:
        """
        获取所有可用主题
        
        Returns:
            List: 可用主题列表
        """
        if self._available_themes is None:
            self._available_themes = []
            
            # 添加ttkbootstrap主题
            if TTKBOOTSTRAP_AVAILABLE:
                try:
                    temp_root = ttk.Window()
                    available_ttk_themes = list(temp_root.style.theme_names())
                    temp_root.destroy()
                    self._available_themes.extend(available_ttk_themes)
                except Exception as e:
                    self.logger.warning(f"获取ttkbootstrap主题失败: {e}")
            
            # 添加经典主题
            self._available_themes.extend(self.CLASSIC_THEMES)
        
        return self._available_themes
    
    def get_colorful_themes(self) -> List[str]:
        """
        获取Colorful主题列表
        
        Returns:
            List: Colorful主题列表
        """
        return self._filter_available_themes(self.COLORFUL_THEMES)
    
    def validate_theme(self, theme_name: str) -> bool:
        """
        验证主题是否有效
        
        Args:
            theme_name: 主题名称
            
        Returns:
            bool: 主题是否有效
        """
        if not theme_name:
            return False
        
        # 检查经典主题
        if self.validator.is_tkinter_theme(theme_name):
            return True
        
        # 检查ttkbootstrap主题
        if TTKBOOTSTRAP_AVAILABLE:
            return self.validator.is_ttkbootstrap_theme(theme_name)
        
        return False
    
    def get_theme_category(self, theme_name: str) -> str:
        """
        获取主题分类
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: 主题分类
        """
        return self.validator.get_theme_category(theme_name)
    
    def apply_theme(self, window, theme_name: str) -> bool:
        """
        应用主题到窗口
        
        Args:
            window: 窗口对象 (tk.Tk 或 ttk.Window)
            theme_name: 主题名称
            
        Returns:
            bool: 是否成功应用主题
        """
        try:
            if not self.validate_theme(theme_name):
                self.logger.warning(f"主题 {theme_name} 无效")
                return False
            
            # 应用ttkbootstrap主题
            if TTKBOOTSTRAP_AVAILABLE and hasattr(window, 'style'):
                if theme_name in self.get_available_themes():
                    window.style.theme_use(theme_name)
                    self.logger.info(f"成功应用主题: {theme_name}")
                    return True
            
            # 应用经典主题
            elif self.validator.is_tkinter_theme(theme_name):
                if hasattr(window, 'tk'):
                    window.tk.call('ttk::setTheme', theme_name)
                    self.logger.info(f"成功应用经典主题: {theme_name}")
                    return True
            
            self.logger.warning(f"无法应用主题: {theme_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"应用主题 {theme_name} 失败: {e}")
            return False
    
    def migrate_legacy_theme(self, old_theme: str) -> str:
        """
        迁移旧主题配置
        
        Args:
            old_theme: 旧主题名称
            
        Returns:
            str: 迁移后的主题名称
        """
        if old_theme in self.THEME_MIGRATION_MAP:
            new_theme = self.THEME_MIGRATION_MAP[old_theme]
            self.logger.info(f"主题迁移: {old_theme} -> {new_theme}")
            return new_theme
        
        # 如果主题仍然有效，保持不变
        if self.validate_theme(old_theme):
            return old_theme
        
        # 否则使用默认主题
        self.logger.warning(f"主题 {old_theme} 无效，使用默认主题")
        return self.DEFAULT_THEME
    
    def get_theme_display_name(self, theme_name: str) -> str:
        """
        获取主题显示名称
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: 显示名称
        """
        display_names = {
            'litera': 'Litera (默认)',
            'flatly': 'Flatly',
            'cosmo': 'Cosmo',
            'journal': 'Journal',
            'lumen': 'Lumen',
            'minty': 'Minty',
            'pulse': 'Pulse',
            'sandstone': 'Sandstone',
            'united': 'United',
            'yeti': 'Yeti',
            'darkly': 'Darkly',
            'cyborg': 'Cyborg',
            'slate': 'Slate',
            'superhero': 'Superhero',
            'vapor': 'Vapor',
            'morph': 'Morph',
            'default': 'Windows默认',
            'clam': 'Windows Clam',
            'alt': 'Windows Alt',
            'classic': 'Windows经典'
        }
        
        return display_names.get(theme_name, theme_name.title())
    
    def get_theme_description(self, theme_name: str) -> str:
        """
        获取主题描述
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: 主题描述
        """
        descriptions = {
            'litera': '现代简洁的浅色主题，适合日常使用',
            'flatly': '扁平化设计风格，简洁明快',
            'cosmo': '宇宙风格，优雅的浅色主题',
            'journal': '期刊风格，专业的阅读体验',
            'darkly': '经典暗色主题，护眼舒适',
            'cyborg': '科技感暗色主题，未来风格',
            'superhero': '超级英雄风格，动感十足',
            'vapor': '蒸汽波风格，复古未来感',
            'morph': '变幻多彩，丰富的色彩搭配',
            'default': 'Windows系统默认主题',
            'classic': 'Windows经典主题风格'
        }
        
        return descriptions.get(theme_name, '主题描述暂无')


# 全局主题管理器实例
theme_manager = ThemeManager()