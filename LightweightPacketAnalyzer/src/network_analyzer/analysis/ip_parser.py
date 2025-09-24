"""
IP协议解析器

支持IPv4和IPv6协议解析，提取版本、长度、TTL等字段
"""

import struct
import socket
from typing import Dict, Any, Optional
from .base_parser import BaseProtocolParser, ProtocolType


class IPv4Parser(BaseProtocolParser):
    """IPv4协议解析器"""
    
    # IPv4头部最小长度（字节）
    IPV4_MIN_HEADER_LENGTH = 20
    
    # IP协议号
    PROTOCOL_TCP = 6
    PROTOCOL_UDP = 17
    PROTOCOL_ICMP = 1
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.IPV4
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析IPv4数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        if len(data) < offset + self.IPV4_MIN_HEADER_LENGTH:
            return False
        
        # 检查版本号是否为4
        version = (data[offset] >> 4) & 0x0F
        return version == 4
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析IPv4数据包头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据不是有效的IPv4数据包")
        
        # 解析IPv4头部前20字节
        ipv4_header = data[offset:offset + self.IPV4_MIN_HEADER_LENGTH]
        
        # 解包IPv4头部
        version_ihl, tos, total_length, identification, flags_fragment, ttl, protocol, checksum, src_ip, dst_ip = struct.unpack('!BBHHHBBH4s4s', ipv4_header)
        
        # 提取字段
        version = (version_ihl >> 4) & 0x0F
        ihl = version_ihl & 0x0F  # Internet Header Length (4字节为单位)
        header_length = ihl * 4
        
        # 提取标志位和片偏移
        flags = (flags_fragment >> 13) & 0x07
        fragment_offset = flags_fragment & 0x1FFF
        
        # 格式化IP地址
        src_ip_str = socket.inet_ntoa(src_ip)
        dst_ip_str = socket.inet_ntoa(dst_ip)
        
        # 解析协议名称
        protocol_name = self._get_protocol_name(protocol)
        
        fields = {
            'version': version,
            'header_length': header_length,
            'type_of_service': tos,
            'total_length': total_length,
            'identification': identification,
            'flags': flags,
            'fragment_offset': fragment_offset,
            'ttl': ttl,
            'protocol': protocol,
            'protocol_name': protocol_name,
            'checksum': checksum,
            'source_ip': src_ip_str,
            'destination_ip': dst_ip_str
        }
        
        next_offset = offset + header_length
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.IPV4
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """
        根据协议字段确定下一层协议类型
        
        Args:
            fields: IPv4层解析的字段
            
        Returns:
            Optional[ProtocolType]: 下一层协议类型
        """
        protocol = fields.get('protocol')
        
        if protocol == self.PROTOCOL_TCP:
            return ProtocolType.TCP
        elif protocol == self.PROTOCOL_UDP:
            return ProtocolType.UDP
        elif protocol == self.PROTOCOL_ICMP:
            return ProtocolType.ICMP
        
        return None
    
    def _get_protocol_name(self, protocol: int) -> str:
        """
        获取协议名称
        
        Args:
            protocol: 协议号
            
        Returns:
            str: 协议名称
        """
        protocol_names = {
            self.PROTOCOL_ICMP: 'ICMP',
            self.PROTOCOL_TCP: 'TCP',
            self.PROTOCOL_UDP: 'UDP',
            2: 'IGMP',
            4: 'IP-in-IP',
            41: 'IPv6',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
            89: 'OSPF'
        }
        
        return protocol_names.get(protocol, f'Unknown ({protocol})')


class IPv6Parser(BaseProtocolParser):
    """IPv6协议解析器"""
    
    # IPv6头部长度（字节）
    IPV6_HEADER_LENGTH = 40
    
    # IPv6下一个头部协议号（与IPv4相同）
    PROTOCOL_TCP = 6
    PROTOCOL_UDP = 17
    PROTOCOL_ICMP = 58  # ICMPv6
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.IPV6
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析IPv6数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        if len(data) < offset + self.IPV6_HEADER_LENGTH:
            return False
        
        # 检查版本号是否为6
        version = (data[offset] >> 4) & 0x0F
        return version == 6
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析IPv6数据包头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据不是有效的IPv6数据包")
        
        # 解析IPv6头部
        ipv6_header = data[offset:offset + self.IPV6_HEADER_LENGTH]
        
        # 解包IPv6头部
        version_tc_fl, payload_length, next_header, hop_limit = struct.unpack('!IHBB', ipv6_header[:8])
        src_ip = ipv6_header[8:24]
        dst_ip = ipv6_header[24:40]
        
        # 提取字段
        version = (version_tc_fl >> 28) & 0x0F
        traffic_class = (version_tc_fl >> 20) & 0xFF
        flow_label = version_tc_fl & 0xFFFFF
        
        # 格式化IPv6地址
        src_ip_str = socket.inet_ntop(socket.AF_INET6, src_ip)
        dst_ip_str = socket.inet_ntop(socket.AF_INET6, dst_ip)
        
        # 解析下一个头部协议名称
        protocol_name = self._get_protocol_name(next_header)
        
        fields = {
            'version': version,
            'traffic_class': traffic_class,
            'flow_label': flow_label,
            'payload_length': payload_length,
            'next_header': next_header,
            'next_header_name': protocol_name,
            'hop_limit': hop_limit,
            'source_ip': src_ip_str,
            'destination_ip': dst_ip_str,
            'header_length': self.IPV6_HEADER_LENGTH
        }
        
        next_offset = offset + self.IPV6_HEADER_LENGTH
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.IPV6
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """
        根据下一个头部字段确定下一层协议类型
        
        Args:
            fields: IPv6层解析的字段
            
        Returns:
            Optional[ProtocolType]: 下一层协议类型
        """
        next_header = fields.get('next_header')
        
        if next_header == self.PROTOCOL_TCP:
            return ProtocolType.TCP
        elif next_header == self.PROTOCOL_UDP:
            return ProtocolType.UDP
        elif next_header == self.PROTOCOL_ICMP:
            return ProtocolType.ICMP
        
        return None
    
    def _get_protocol_name(self, protocol: int) -> str:
        """
        获取协议名称
        
        Args:
            protocol: 协议号
            
        Returns:
            str: 协议名称
        """
        protocol_names = {
            0: 'Hop-by-Hop Options',
            self.PROTOCOL_TCP: 'TCP',
            self.PROTOCOL_UDP: 'UDP',
            43: 'Routing Header',
            44: 'Fragment Header',
            51: 'Authentication Header',
            self.PROTOCOL_ICMP: 'ICMPv6',
            59: 'No Next Header',
            60: 'Destination Options'
        }
        
        return protocol_names.get(protocol, f'Unknown ({protocol})')


# 注册解析器到工厂
from .base_parser import parser_factory
parser_factory.register_parser(ProtocolType.IPV4, IPv4Parser)
parser_factory.register_parser(ProtocolType.IPV6, IPv6Parser)