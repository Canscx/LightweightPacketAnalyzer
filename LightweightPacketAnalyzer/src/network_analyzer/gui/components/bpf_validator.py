"""
BPF过滤器验证器

提供BPF过滤表达式的语法验证和实时检查功能。
"""

import logging
from typing import Dict, Any, Optional, Tuple
import re

try:
    from scapy.all import compile_filter
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class BPFValidator:
    """BPF过滤器验证器"""
    
    def __init__(self):
        """初始化BPF验证器"""
        self.logger = logging.getLogger(__name__)
        
        # 常见BPF关键字和操作符
        self.keywords = {
            'protocols': ['tcp', 'udp', 'icmp', 'ip', 'ip6', 'arp', 'rarp'],
            'directions': ['src', 'dst', 'host'],
            'operators': ['and', 'or', 'not', '&&', '||', '!'],
            'qualifiers': ['port', 'portrange', 'net', 'len', 'proto']
        }
        
        # 预编译的正则表达式
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译常用的正则表达式模式"""
        # IP地址模式
        self.ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        
        # 端口号模式
        self.port_pattern = re.compile(r'^(?:[1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$')
        
        # MAC地址模式
        self.mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        
        # 网络掩码模式
        self.netmask_pattern = re.compile(r'^/([0-9]|[1-2][0-9]|3[0-2])$')
    
    def validate_filter(self, filter_expression: str) -> Dict[str, Any]:
        """
        验证BPF过滤表达式
        
        Args:
            filter_expression: BPF过滤表达式
            
        Returns:
            验证结果字典，包含is_valid, error_message, suggestions等
        """
        if not filter_expression.strip():
            return {
                'is_valid': True,
                'error_message': None,
                'suggestions': [],
                'warning_message': None
            }
        
        try:
            # 基本语法检查
            syntax_result = self._check_basic_syntax(filter_expression)
            if not syntax_result['is_valid']:
                return syntax_result
            
            # 使用Scapy进行高级验证（如果可用）
            if SCAPY_AVAILABLE:
                scapy_result = self._validate_with_scapy(filter_expression)
                if not scapy_result['is_valid']:
                    return scapy_result
            
            # 生成建议和警告
            suggestions = self._generate_suggestions(filter_expression)
            warnings = self._check_warnings(filter_expression)
            
            return {
                'is_valid': True,
                'error_message': None,
                'suggestions': suggestions,
                'warning_message': warnings
            }
            
        except Exception as e:
            self.logger.error(f"BPF验证异常: {e}")
            return {
                'is_valid': False,
                'error_message': f"验证过程中发生错误: {str(e)}",
                'suggestions': [],
                'warning_message': None
            }
    
    def _check_basic_syntax(self, filter_expression: str) -> Dict[str, Any]:
        """检查基本语法"""
        # 检查括号匹配
        if not self._check_parentheses(filter_expression):
            return {
                'is_valid': False,
                'error_message': "括号不匹配",
                'suggestions': ["检查括号是否正确配对"],
                'warning_message': None
            }
        
        # 检查引号匹配
        if not self._check_quotes(filter_expression):
            return {
                'is_valid': False,
                'error_message': "引号不匹配",
                'suggestions': ["检查引号是否正确配对"],
                'warning_message': None
            }
        
        # 检查不完整的表达式
        if self._is_incomplete_expression(filter_expression):
            return {
                'is_valid': False,
                'error_message': "表达式不完整",
                'suggestions': ["检查表达式是否完整"],
                'warning_message': None
            }
        
        # 检查基本关键字
        tokens = self._tokenize(filter_expression)
        for token in tokens:
            if not self._is_valid_token(token):
                return {
                    'is_valid': False,
                    'error_message': f"未识别的关键字或语法: '{token}'",
                    'suggestions': self._suggest_similar_keywords(token),
                    'warning_message': None
                }
        
        return {'is_valid': True, 'error_message': None, 'suggestions': [], 'warning_message': None}
    
    def _validate_with_scapy(self, filter_expression: str) -> Dict[str, Any]:
        """使用Scapy验证BPF表达式"""
        try:
            # 尝试编译过滤器
            compile_filter(filter_expression)
            return {'is_valid': True, 'error_message': None, 'suggestions': [], 'warning_message': None}
        except Exception as e:
            error_msg = str(e)
            suggestions = []
            
            # 根据错误类型提供建议
            if "syntax error" in error_msg.lower():
                suggestions.append("检查语法是否正确")
            elif "unknown" in error_msg.lower():
                suggestions.append("检查关键字拼写")
            
            return {
                'is_valid': False,
                'error_message': f"BPF语法错误: {error_msg}",
                'suggestions': suggestions,
                'warning_message': None
            }
    
    def _check_parentheses(self, expression: str) -> bool:
        """检查括号是否匹配"""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    def _check_quotes(self, expression: str) -> bool:
        """检查引号匹配"""
        single_quotes = expression.count("'")
        double_quotes = expression.count('"')
        return single_quotes % 2 == 0 and double_quotes % 2 == 0
    
    def _is_incomplete_expression(self, expression: str) -> bool:
        """检查表达式是否不完整"""
        expression = expression.strip()
        
        # 检查以操作符结尾
        if expression.endswith(('and', 'or', 'not', '&&', '||', '!')):
            return True
        
        # 检查常见的不完整模式
        incomplete_patterns = [
            r'\btcp\s+port\s*$',      # "tcp port" 没有端口号
            r'\budp\s+port\s*$',      # "udp port" 没有端口号
            r'\bhost\s*$',            # "host" 没有地址
            r'\bnet\s*$',             # "net" 没有网络地址
            r'\bport\s*$',            # "port" 没有端口号
            r'\bether\s+host\s*$',    # "ether host" 没有MAC地址
        ]
        
        for pattern in incomplete_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return True
        
        return False
    
    def _tokenize(self, expression: str) -> list:
        """将表达式分解为token"""
        # 简单的分词，按空格和常见操作符分割
        import re
        tokens = re.findall(r'\w+|[()&|!]|==|!=|>=|<=|>|<', expression)
        return [token.lower() for token in tokens if token.strip()]
    
    def _is_valid_token(self, token: str) -> bool:
        """检查token是否有效"""
        # 检查是否为关键字
        all_keywords = []
        for keyword_list in self.keywords.values():
            all_keywords.extend(keyword_list)
        
        if token in all_keywords:
            return True
        
        # 检查是否为数字
        if token.isdigit():
            return True
        
        # 检查是否为IP地址
        if self.ip_pattern.match(token):
            return True
        
        # 检查是否为MAC地址
        if self.mac_pattern.match(token):
            return True
        
        # 检查是否为端口号
        if self.port_pattern.match(token):
            return True
        
        # 其他常见模式
        common_patterns = ['0x[0-9a-f]+', r'\d+\.\d+\.\d+\.\d+/\d+']
        for pattern in common_patterns:
            if re.match(pattern, token):
                return True
        
        return False
    
    def _suggest_similar_keywords(self, token: str) -> list:
        """为未识别的token提供相似关键字建议"""
        suggestions = []
        all_keywords = []
        for keyword_list in self.keywords.values():
            all_keywords.extend(keyword_list)
        
        # 简单的相似度匹配
        for keyword in all_keywords:
            if self._calculate_similarity(token, keyword) > 0.6:
                suggestions.append(f"是否想输入 '{keyword}'?")
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        # 简单的Levenshtein距离实现
        if len(str1) < len(str2):
            return self._calculate_similarity(str2, str1)
        
        if len(str2) == 0:
            return 0.0
        
        previous_row = list(range(len(str2) + 1))
        for i, c1 in enumerate(str1):
            current_row = [i + 1]
            for j, c2 in enumerate(str2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return 1.0 - (previous_row[-1] / len(str1))
    
    def _generate_suggestions(self, filter_expression: str) -> list:
        """生成优化建议"""
        suggestions = []
        
        # 检查是否可以简化
        if 'and' in filter_expression and 'or' in filter_expression:
            suggestions.append("复杂表达式可能影响性能，考虑简化")
        
        # 检查是否使用了高效的过滤器
        if 'host' not in filter_expression and ('src' in filter_expression or 'dst' in filter_expression):
            suggestions.append("使用 'host' 关键字可能更高效")
        
        return suggestions
    
    def _check_warnings(self, filter_expression: str) -> Optional[str]:
        """检查潜在的警告"""
        warnings = []
        
        # 检查性能警告
        if len(filter_expression) > 100:
            warnings.append("过滤表达式较长，可能影响捕获性能")
        
        # 检查常见错误模式
        if 'port 0' in filter_expression:
            warnings.append("端口0通常不用于网络通信")
        
        return "; ".join(warnings) if warnings else None
    
    def get_common_filters(self) -> Dict[str, str]:
        """获取常用过滤器模板"""
        return {
            "HTTP流量": "tcp port 80 or tcp port 443",
            "DNS查询": "udp port 53",
            "SSH连接": "tcp port 22", 
            "FTP流量": "tcp port 21 or tcp port 20",
            "ICMP包": "icmp",
            "特定主机": "host 192.168.1.1",
            "TCP连接": "tcp",
            "UDP数据": "udp",
            "ARP协议": "arp",
            "广播包": "broadcast"
        }