"""
模板管理器

提供模板的加载、渲染、缓存和管理功能
支持Jinja2模板引擎，提供安全的模板渲染环境
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from jinja2.sandbox import SandboxedEnvironment


logger = logging.getLogger(__name__)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化模板管理器
        
        Args:
            template_dir: 模板目录路径，默认使用当前模块的templates目录
        """
        if template_dir is None:
            # 使用当前模块的templates目录
            current_dir = Path(__file__).parent
            template_dir = current_dir / "html"
        
        self.template_dir = Path(template_dir)
        self.logger = logging.getLogger(__name__)
        
        # 确保模板目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Jinja2环境（使用沙箱环境提高安全性）
        self.env = SandboxedEnvironment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 注册自定义过滤器
        self._register_custom_filters()
        
        # 模板缓存
        self._template_cache: Dict[str, Any] = {}
    
    def _register_custom_filters(self):
        """注册自定义Jinja2过滤器"""
        
        def format_bytes(value: int) -> str:
            """格式化字节数"""
            if value < 1024:
                return f"{value} B"
            elif value < 1024 * 1024:
                return f"{value / 1024:.1f} KB"
            elif value < 1024 * 1024 * 1024:
                return f"{value / (1024 * 1024):.1f} MB"
            else:
                return f"{value / (1024 * 1024 * 1024):.1f} GB"
        
        def format_percentage(value: float) -> str:
            """格式化百分比"""
            return f"{value:.2f}%"
        
        def format_datetime(value: datetime) -> str:
            """格式化日期时间"""
            return value.strftime("%Y-%m-%d %H:%M:%S")
        
        def format_duration(value: float) -> str:
            """格式化持续时间"""
            if value < 60:
                return f"{value:.1f} 秒"
            elif value < 3600:
                return f"{value / 60:.1f} 分钟"
            else:
                return f"{value / 3600:.1f} 小时"
        
        # 注册过滤器
        self.env.filters['format_bytes'] = format_bytes
        self.env.filters['format_percentage'] = format_percentage
        self.env.filters['format_datetime'] = format_datetime
        self.env.filters['format_duration'] = format_duration
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文数据
            
        Returns:
            str: 渲染后的内容
            
        Raises:
            TemplateNotFound: 模板文件不存在
            RuntimeError: 模板渲染失败
        """
        try:
            # 从缓存获取模板
            template = self._get_template(template_name)
            
            # 添加通用上下文
            full_context = self._prepare_context(context)
            
            # 渲染模板
            rendered = template.render(full_context)
            
            self.logger.debug(f"模板 {template_name} 渲染成功")
            return rendered
            
        except TemplateNotFound:
            self.logger.error(f"模板文件不存在: {template_name}")
            raise
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            raise RuntimeError(f"模板渲染失败: {e}")
    
    def _get_template(self, template_name: str):
        """获取模板（带缓存）"""
        if template_name not in self._template_cache:
            try:
                template = self.env.get_template(template_name)
                self._template_cache[template_name] = template
            except TemplateNotFound:
                # 尝试在子目录中查找
                possible_paths = [
                    template_name,
                    f"html/{template_name}",
                    f"pdf/{template_name}",
                ]
                
                for path in possible_paths:
                    try:
                        template = self.env.get_template(path)
                        self._template_cache[template_name] = template
                        break
                    except TemplateNotFound:
                        continue
                else:
                    raise TemplateNotFound(template_name)
        
        return self._template_cache[template_name]
    
    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备模板上下文，添加通用变量"""
        full_context = context.copy()
        
        # 添加通用变量
        full_context.update({
            'current_time': datetime.now(),
            'app_name': '轻量级数据包分析器',
            'app_version': '1.0.0'
        })
        
        return full_context
    
    def list_available_templates(self) -> List[str]:
        """
        列出所有可用的模板
        
        Returns:
            List[str]: 模板文件名列表
        """
        try:
            templates = []
            for root, dirs, files in os.walk(self.template_dir):
                for file in files:
                    if file.endswith(('.html', '.jinja2', '.j2')):
                        # 计算相对路径
                        rel_path = os.path.relpath(
                            os.path.join(root, file), 
                            self.template_dir
                        )
                        templates.append(rel_path.replace('\\', '/'))
            
            return sorted(templates)
            
        except Exception as e:
            self.logger.error(f"列出模板失败: {e}")
            return []
    
    def validate_template(self, template_name: str) -> bool:
        """
        验证模板是否有效
        
        Args:
            template_name: 模板文件名
            
        Returns:
            bool: 模板是否有效
        """
        try:
            template = self._get_template(template_name)
            # 尝试用空上下文渲染，检查语法
            template.render({})
            return True
        except Exception as e:
            self.logger.error(f"模板验证失败: {e}")
            return False
    
    def clear_cache(self):
        """清空模板缓存"""
        self._template_cache.clear()
        self.logger.info("模板缓存已清空")
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        获取模板信息
        
        Args:
            template_name: 模板文件名
            
        Returns:
            Dict: 模板信息
        """
        try:
            template_path = self.template_dir / template_name
            
            if not template_path.exists():
                return {}
            
            stat = template_path.stat()
            
            return {
                'name': template_name,
                'path': str(template_path),
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'is_valid': self.validate_template(template_name)
            }
            
        except Exception as e:
            self.logger.error(f"获取模板信息失败: {e}")
            return {}