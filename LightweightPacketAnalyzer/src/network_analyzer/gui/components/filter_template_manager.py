"""
过滤器模板管理器

提供预定义的BPF过滤器模板管理功能。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class FilterTemplate:
    """过滤器模板数据类"""
    name: str
    filter_expression: str
    description: str
    category: str
    is_custom: bool = False
    usage_count: int = 0


class FilterTemplateManager:
    """过滤器模板管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化过滤器模板管理器
        
        Args:
            config_dir: 配置文件目录，默认为data目录
        """
        self.logger = logging.getLogger(__name__)
        self.config_dir = config_dir or Path("data")
        self.config_file = self.config_dir / "filter_templates.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 模板存储
        self._templates: Dict[str, FilterTemplate] = {}
        
        # 加载模板
        self._load_default_templates()
        self._load_custom_templates()
    
    def _load_default_templates(self):
        """加载默认过滤器模板"""
        default_templates = [
            # 协议类型
            FilterTemplate(
                name="HTTP流量",
                filter_expression="tcp port 80 or tcp port 443",
                description="捕获HTTP和HTTPS流量",
                category="协议"
            ),
            FilterTemplate(
                name="DNS查询",
                filter_expression="udp port 53 or tcp port 53",
                description="捕获DNS查询和响应",
                category="协议"
            ),
            FilterTemplate(
                name="SSH连接",
                filter_expression="tcp port 22",
                description="捕获SSH连接流量",
                category="协议"
            ),
            FilterTemplate(
                name="FTP流量",
                filter_expression="tcp port 21 or tcp port 20",
                description="捕获FTP控制和数据连接",
                category="协议"
            ),
            FilterTemplate(
                name="SMTP邮件",
                filter_expression="tcp port 25 or tcp port 587 or tcp port 465",
                description="捕获SMTP邮件流量",
                category="协议"
            ),
            FilterTemplate(
                name="DHCP流量",
                filter_expression="udp port 67 or udp port 68",
                description="捕获DHCP请求和响应",
                category="协议"
            ),
            
            # 网络层协议
            FilterTemplate(
                name="TCP连接",
                filter_expression="tcp",
                description="捕获所有TCP流量",
                category="传输层"
            ),
            FilterTemplate(
                name="UDP数据",
                filter_expression="udp",
                description="捕获所有UDP流量",
                category="传输层"
            ),
            FilterTemplate(
                name="ICMP包",
                filter_expression="icmp",
                description="捕获ICMP协议包",
                category="网络层"
            ),
            FilterTemplate(
                name="ARP协议",
                filter_expression="arp",
                description="捕获ARP协议包",
                category="链路层"
            ),
            
            # 主机和网络
            FilterTemplate(
                name="本地网络",
                filter_expression="net 192.168.0.0/16 or net 10.0.0.0/8 or net 172.16.0.0/12",
                description="捕获私有网络流量",
                category="网络"
            ),
            FilterTemplate(
                name="广播包",
                filter_expression="broadcast",
                description="捕获广播数据包",
                category="网络"
            ),
            FilterTemplate(
                name="组播包",
                filter_expression="multicast",
                description="捕获组播数据包",
                category="网络"
            ),
            
            # 端口范围
            FilterTemplate(
                name="高端口",
                filter_expression="port > 1024",
                description="捕获高端口号流量",
                category="端口"
            ),
            FilterTemplate(
                name="系统端口",
                filter_expression="port < 1024",
                description="捕获系统端口流量",
                category="端口"
            ),
            FilterTemplate(
                name="Web服务",
                filter_expression="port 80 or port 443 or port 8080 or port 8443",
                description="捕获常见Web服务端口",
                category="端口"
            ),
            
            # 数据包大小
            FilterTemplate(
                name="大数据包",
                filter_expression="len > 1000",
                description="捕获大于1000字节的数据包",
                category="大小"
            ),
            FilterTemplate(
                name="小数据包",
                filter_expression="len < 100",
                description="捕获小于100字节的数据包",
                category="大小"
            ),
            
            # 特殊用途
            FilterTemplate(
                name="错误包",
                filter_expression="icmp[icmptype] == 3 or icmp[icmptype] == 11",
                description="捕获ICMP错误消息",
                category="诊断"
            ),
            FilterTemplate(
                name="SYN扫描",
                filter_expression="tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0",
                description="检测TCP SYN扫描",
                category="安全"
            ),
            FilterTemplate(
                name="RST包",
                filter_expression="tcp[tcpflags] & tcp-rst != 0",
                description="捕获TCP重置包",
                category="诊断"
            )
        ]
        
        for template in default_templates:
            self._templates[template.name] = template
        
        self.logger.info(f"加载了 {len(default_templates)} 个默认过滤器模板")
    
    def _load_custom_templates(self):
        """从文件加载自定义模板"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            custom_count = 0
            for template_data in data.get('custom_templates', []):
                template = FilterTemplate(**template_data)
                template.is_custom = True
                self._templates[template.name] = template
                custom_count += 1
            
            self.logger.info(f"加载了 {custom_count} 个自定义过滤器模板")
            
        except Exception as e:
            self.logger.error(f"加载自定义模板失败: {e}")
    
    def _save_custom_templates(self):
        """保存自定义模板到文件"""
        try:
            custom_templates = [
                asdict(template) for template in self._templates.values()
                if template.is_custom
            ]
            
            data = {
                'custom_templates': custom_templates,
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"保存了 {len(custom_templates)} 个自定义模板")
            
        except Exception as e:
            self.logger.error(f"保存自定义模板失败: {e}")
    
    def get_all_templates(self) -> List[FilterTemplate]:
        """获取所有模板"""
        return list(self._templates.values())
    
    def get_templates_by_category(self, category: str) -> List[FilterTemplate]:
        """根据分类获取模板"""
        return [
            template for template in self._templates.values()
            if template.category == category
        ]
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set(template.category for template in self._templates.values())
        return sorted(list(categories))
    
    def get_template(self, name: str) -> Optional[FilterTemplate]:
        """根据名称获取模板"""
        return self._templates.get(name)
    
    def add_template(self, name: str, filter_expression: str, description: str, 
                    category: str) -> bool:
        """
        添加自定义模板
        
        Args:
            name: 模板名称
            filter_expression: BPF过滤表达式
            description: 描述
            category: 分类
            
        Returns:
            是否添加成功
        """
        if name in self._templates:
            self.logger.warning(f"模板 '{name}' 已存在")
            return False
        
        try:
            template = FilterTemplate(
                name=name,
                filter_expression=filter_expression,
                description=description,
                category=category,
                is_custom=True
            )
            
            self._templates[name] = template
            self._save_custom_templates()
            
            self.logger.info(f"添加自定义模板: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加模板失败: {e}")
            return False
    
    def update_template(self, name: str, **kwargs) -> bool:
        """
        更新模板
        
        Args:
            name: 模板名称
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        if name not in self._templates:
            return False
        
        template = self._templates[name]
        if not template.is_custom:
            self.logger.warning(f"无法修改默认模板: {name}")
            return False
        
        try:
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            self._save_custom_templates()
            self.logger.info(f"更新模板: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新模板失败: {e}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """
        删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        if name not in self._templates:
            return False
        
        template = self._templates[name]
        if not template.is_custom:
            self.logger.warning(f"无法删除默认模板: {name}")
            return False
        
        try:
            del self._templates[name]
            self._save_custom_templates()
            
            self.logger.info(f"删除模板: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除模板失败: {e}")
            return False
    
    def increment_usage(self, name: str):
        """增加模板使用次数"""
        if name in self._templates:
            self._templates[name].usage_count += 1
            if self._templates[name].is_custom:
                self._save_custom_templates()
    
    def get_popular_templates(self, limit: int = 5) -> List[FilterTemplate]:
        """获取最常用的模板"""
        templates = list(self._templates.values())
        templates.sort(key=lambda x: x.usage_count, reverse=True)
        return templates[:limit]
    
    def search_templates(self, query: str) -> List[FilterTemplate]:
        """
        搜索模板
        
        Args:
            query: 搜索关键字
            
        Returns:
            匹配的模板列表
        """
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or
                query in template.filter_expression.lower() or
                query in template.category.lower()):
                results.append(template)
        
        return results
    
    def export_templates(self, file_path: Path) -> bool:
        """
        导出模板到文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            templates_data = [asdict(template) for template in self._templates.values()]
            
            export_data = {
                'templates': templates_data,
                'export_time': str(Path().cwd()),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"导出 {len(templates_data)} 个模板到: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出模板失败: {e}")
            return False
    
    def import_templates(self, file_path: Path) -> int:
        """
        从文件导入模板
        
        Args:
            file_path: 导入文件路径
            
        Returns:
            成功导入的模板数量
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for template_data in data.get('templates', []):
                template = FilterTemplate(**template_data)
                template.is_custom = True
                
                # 避免重名
                original_name = template.name
                counter = 1
                while template.name in self._templates:
                    template.name = f"{original_name} ({counter})"
                    counter += 1
                
                self._templates[template.name] = template
                imported_count += 1
            
            if imported_count > 0:
                self._save_custom_templates()
            
            self.logger.info(f"导入了 {imported_count} 个模板")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"导入模板失败: {e}")
            return 0