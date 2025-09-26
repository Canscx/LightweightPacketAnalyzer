"""
Jinja2模板渲染器

提供安全的Jinja2模板渲染功能，包括：
- 沙箱环境渲染
- 自定义过滤器
- 模板继承支持
- 安全性检查
"""

import logging
from typing import Dict, Any, Optional, List
from jinja2 import Environment, BaseLoader, TemplateError
from jinja2.sandbox import SandboxedEnvironment


logger = logging.getLogger(__name__)


class Jinja2Renderer:
    """Jinja2模板渲染器"""
    
    def __init__(self, use_sandbox: bool = True):
        """
        初始化渲染器
        
        Args:
            use_sandbox: 是否使用沙箱环境（推荐开启以提高安全性）
        """
        self.use_sandbox = use_sandbox
        self.logger = logging.getLogger(__name__)
        
        # 创建Jinja2环境
        if use_sandbox:
            self.env = SandboxedEnvironment(
                loader=BaseLoader(),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.env = Environment(
                loader=BaseLoader(),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        
        # 注册自定义过滤器和函数
        self._register_custom_filters()
        self._register_custom_functions()
    
    def _register_custom_filters(self):
        """注册自定义过滤器"""
        
        def safe_format_number(value: Any, decimal_places: int = 2) -> str:
            """安全的数字格式化"""
            try:
                if isinstance(value, (int, float)):
                    return f"{value:.{decimal_places}f}"
                return str(value)
            except:
                return "N/A"
        
        def safe_format_list(value: Any, separator: str = ", ") -> str:
            """安全的列表格式化"""
            try:
                if isinstance(value, (list, tuple)):
                    return separator.join(str(item) for item in value)
                return str(value)
            except:
                return "N/A"
        
        def truncate_text(value: str, length: int = 50) -> str:
            """截断文本"""
            try:
                if len(value) <= length:
                    return value
                return value[:length] + "..."
            except:
                return "N/A"
        
        # 注册过滤器
        self.env.filters['safe_number'] = safe_format_number
        self.env.filters['safe_list'] = safe_format_list
        self.env.filters['truncate'] = truncate_text
    
    def _register_custom_functions(self):
        """注册自定义函数"""
        
        def get_chart_url(chart_name: str, base_path: str = "charts") -> str:
            """生成图表URL"""
            return f"{base_path}/{chart_name}"
        
        def format_table_data(data: list, headers: list) -> Dict[str, Any]:
            """格式化表格数据"""
            return {
                'headers': headers,
                'rows': data,
                'row_count': len(data)
            }
        
        # 注册全局函数
        self.env.globals['get_chart_url'] = get_chart_url
        self.env.globals['format_table_data'] = format_table_data
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        渲染模板字符串
        
        Args:
            template_string: 模板字符串
            context: 模板上下文
            
        Returns:
            str: 渲染结果
            
        Raises:
            TemplateError: 模板渲染错误
        """
        try:
            # 验证上下文安全性
            safe_context = self._sanitize_context(context)
            
            # 创建模板对象
            template = self.env.from_string(template_string)
            
            # 渲染模板
            result = template.render(safe_context)
            
            self.logger.debug("模板字符串渲染成功")
            return result
            
        except TemplateError as e:
            self.logger.error(f"模板渲染错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            raise TemplateError(f"渲染失败: {e}")
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理和验证模板上下文
        
        Args:
            context: 原始上下文
            
        Returns:
            Dict: 清理后的安全上下文
        """
        safe_context = {}
        
        for key, value in context.items():
            # 检查键名安全性
            if not isinstance(key, str) or not key.isidentifier():
                self.logger.warning(f"跳过不安全的键名: {key}")
                continue
            
            # 检查值的安全性
            safe_value = self._sanitize_value(value)
            safe_context[key] = safe_value
        
        return safe_context
    
    def _sanitize_value(self, value: Any) -> Any:
        """清理单个值"""
        # 基本类型直接返回
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        
        # 列表类型递归清理
        if isinstance(value, (list, tuple)):
            return [self._sanitize_value(item) for item in value]
        
        # 字典类型递归清理
        if isinstance(value, dict):
            return {
                k: self._sanitize_value(v) 
                for k, v in value.items() 
                if isinstance(k, str)
            }
        
        # 其他类型转换为字符串
        try:
            return str(value)
        except:
            return "N/A"
    
    def validate_template_syntax(self, template_string: str) -> bool:
        """
        验证模板语法
        
        Args:
            template_string: 模板字符串
            
        Returns:
            bool: 语法是否正确
        """
        try:
            self.env.from_string(template_string)
            return True
        except TemplateError as e:
            self.logger.error(f"模板语法错误: {e}")
            return False
    
    def get_template_variables(self, template_string: str) -> List[str]:
        """
        获取模板中使用的变量列表
        
        Args:
            template_string: 模板字符串
            
        Returns:
            List[str]: 变量名列表
        """
        try:
            # 解析模板获取AST
            ast = self.env.parse(template_string)
            
            # 提取变量名
            variables = set()
            for node in ast.find_all('Name'):
                if node.ctx == 'load':  # 只获取读取的变量
                    variables.add(node.name)
            
            return sorted(list(variables))
            
        except Exception as e:
            self.logger.error(f"提取模板变量失败: {e}")
            return []
    
    def create_template_from_dict(self, template_config: Dict[str, Any]) -> str:
        """
        从配置字典创建模板
        
        Args:
            template_config: 模板配置
            
        Returns:
            str: 生成的模板字符串
        """
        try:
            # 基础模板结构
            template_parts = []
            
            # 添加头部
            if 'header' in template_config:
                template_parts.append(f"<h1>{template_config['header']}</h1>")
            
            # 添加内容区块
            if 'sections' in template_config:
                for section in template_config['sections']:
                    section_html = self._create_section_template(section)
                    template_parts.append(section_html)
            
            return "\n".join(template_parts)
            
        except Exception as e:
            self.logger.error(f"从配置创建模板失败: {e}")
            raise
    
    def _create_section_template(self, section_config: Dict[str, Any]) -> str:
        """创建区块模板"""
        section_type = section_config.get('type', 'text')
        title = section_config.get('title', '')
        headers = section_config.get('headers', [])
        data_var = section_config.get('data_var', 'data')
        chart_name = section_config.get('chart_name', 'chart')
        content_var = section_config.get('content_var', 'content')
        
        if section_type == 'table':
            headers_str = str(headers)
            return f"""
            <div class="section">
                <h2>{title}</h2>
                <table class="stats-table">
                    <thead>
                        <tr>
                            {{% for header in {headers_str} %}}
                            <th>{{{{ header }}}}</th>
                            {{% endfor %}}
                        </tr>
                    </thead>
                    <tbody>
                        {{% for row in {data_var} %}}
                        <tr>
                            {{% for cell in row %}}
                            <td>{{{{ cell }}}}</td>
                            {{% endfor %}}
                        </tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
            """
        elif section_type == 'chart':
            return f"""
            <div class="section">
                <h2>{title}</h2>
                <div class="chart-container">
                    <img src="{{{{ get_chart_url('{chart_name}') }}}}" 
                         alt="{title}">
                </div>
            </div>
            """
        else:
            return f"""
            <div class="section">
                <h2>{title}</h2>
                <p>{{{{ {content_var} }}}}</p>
            </div>
            """