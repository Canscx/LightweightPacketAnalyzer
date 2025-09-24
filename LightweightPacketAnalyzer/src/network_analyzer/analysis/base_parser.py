"""
基础协议解析器模块

定义协议解析器的抽象基类和工厂类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from enum import Enum


class ProtocolType(Enum):
    """协议类型枚举"""
    ETHERNET = "ethernet"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ARP = "arp"


class ParsedPacket:
    """解析后的数据包信息"""
    
    def __init__(self):
        self.layers = []  # 协议层次列表
        self.fields = {}  # 字段信息字典
        self.raw_data = b''  # 原始数据
        self.errors = []  # 解析错误列表
        self.payload = b''  # 载荷数据
        self.payload_size = 0  # 载荷大小
    
    def add_layer(self, protocol_type: ProtocolType, fields: Dict[str, Any]):
        """添加协议层"""
        layer = {
            'protocol': protocol_type,
            'fields': fields
        }
        self.layers.append(layer)
        self.fields[protocol_type.value] = fields
    
    def get_layer(self, protocol_type: ProtocolType) -> Optional[Dict[str, Any]]:
        """获取指定协议层的字段"""
        return self.fields.get(protocol_type.value)
    
    def has_layer(self, protocol_type: ProtocolType) -> bool:
        """检查是否包含指定协议层"""
        return protocol_type.value in self.fields
    
    def add_error(self, error_msg: str):
        """添加解析错误"""
        self.errors.append(error_msg)


class BaseProtocolParser(ABC):
    """协议解析器抽象基类"""
    
    def __init__(self):
        self.protocol_type = None
        self.next_parser = None
    
    @abstractmethod
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析指定数据
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        pass
    
    @abstractmethod
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析协议数据
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        pass
    
    @abstractmethod
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        pass
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """
        根据当前层字段确定下一层协议类型
        
        Args:
            fields: 当前层解析的字段
            
        Returns:
            Optional[ProtocolType]: 下一层协议类型，如果无法确定则返回None
        """
        return None


class ProtocolParserFactory:
    """协议解析器工厂类"""
    
    def __init__(self):
        self._parsers: Dict[ProtocolType, Type[BaseProtocolParser]] = {}
        self._instances: Dict[ProtocolType, BaseProtocolParser] = {}
    
    def register_parser(self, protocol_type: ProtocolType, parser_class: Type[BaseProtocolParser]):
        """
        注册协议解析器
        
        Args:
            protocol_type: 协议类型
            parser_class: 解析器类
        """
        self._parsers[protocol_type] = parser_class
    
    def get_parser(self, protocol_type: ProtocolType) -> Optional[BaseProtocolParser]:
        """
        获取协议解析器实例
        
        Args:
            protocol_type: 协议类型
            
        Returns:
            Optional[BaseProtocolParser]: 解析器实例，如果未注册则返回None
        """
        if protocol_type not in self._instances:
            if protocol_type in self._parsers:
                self._instances[protocol_type] = self._parsers[protocol_type]()
            else:
                return None
        
        return self._instances[protocol_type]
    
    def get_supported_protocols(self) -> list[ProtocolType]:
        """获取支持的协议类型列表"""
        return list(self._parsers.keys())
    
    def clear(self):
        """清空所有注册的解析器"""
        self._parsers.clear()
        self._instances.clear()


# 全局工厂实例
parser_factory = ProtocolParserFactory()