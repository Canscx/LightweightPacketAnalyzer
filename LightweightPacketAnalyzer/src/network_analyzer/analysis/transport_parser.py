"""
传输层协议解析器

支持TCP、UDP、ICMP协议解析
"""

import struct
from typing import Dict, Any, Optional
from .base_parser import BaseProtocolParser, ProtocolType


class TCPParser(BaseProtocolParser):
    """TCP协议解析器"""
    
    # TCP头部最小长度（字节）
    TCP_MIN_HEADER_LENGTH = 20
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.TCP
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析TCP数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        return len(data) >= offset + self.TCP_MIN_HEADER_LENGTH
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析TCP数据包头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据长度不足，无法解析TCP头部")
        
        # 解析TCP头部前20字节
        tcp_header = data[offset:offset + self.TCP_MIN_HEADER_LENGTH]
        
        # 解包TCP头部
        src_port, dst_port, seq_num, ack_num, offset_flags, window_size, checksum, urgent_ptr = struct.unpack('!HHLLHHHH', tcp_header)
        
        # 提取字段
        header_length = ((offset_flags >> 12) & 0x0F) * 4  # 数据偏移量（4字节为单位）
        flags = offset_flags & 0x01FF
        
        # 解析TCP标志位
        tcp_flags = self._parse_tcp_flags(flags)
        
        fields = {
            'source_port': src_port,
            'destination_port': dst_port,
            'sequence_number': seq_num,
            'acknowledgment_number': ack_num,
            'header_length': header_length,
            'flags': flags,
            'flags_detail': tcp_flags,
            'window_size': window_size,
            'checksum': checksum,
            'urgent_pointer': urgent_ptr
        }
        
        next_offset = offset + header_length
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.TCP
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """TCP是传输层协议，通常没有下一层协议"""
        return None
    
    def _parse_tcp_flags(self, flags: int) -> Dict[str, bool]:
        """
        解析TCP标志位
        
        Args:
            flags: 标志位值
            
        Returns:
            Dict[str, bool]: 标志位详情
        """
        return {
            'FIN': bool(flags & 0x01),
            'SYN': bool(flags & 0x02),
            'RST': bool(flags & 0x04),
            'PSH': bool(flags & 0x08),
            'ACK': bool(flags & 0x10),
            'URG': bool(flags & 0x20),
            'ECE': bool(flags & 0x40),
            'CWR': bool(flags & 0x80),
            'NS': bool(flags & 0x100)
        }


class UDPParser(BaseProtocolParser):
    """UDP协议解析器"""
    
    # UDP头部长度（字节）
    UDP_HEADER_LENGTH = 8
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.UDP
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析UDP数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        return len(data) >= offset + self.UDP_HEADER_LENGTH
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析UDP数据包头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据长度不足，无法解析UDP头部")
        
        # 解析UDP头部
        udp_header = data[offset:offset + self.UDP_HEADER_LENGTH]
        
        # 解包UDP头部
        src_port, dst_port, length, checksum = struct.unpack('!HHHH', udp_header)
        
        fields = {
            'source_port': src_port,
            'destination_port': dst_port,
            'length': length,
            'checksum': checksum,
            'header_length': self.UDP_HEADER_LENGTH
        }
        
        next_offset = offset + self.UDP_HEADER_LENGTH
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.UDP
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """UDP是传输层协议，通常没有下一层协议"""
        return None


class ICMPParser(BaseProtocolParser):
    """ICMP协议解析器"""
    
    # ICMP头部最小长度（字节）
    ICMP_MIN_HEADER_LENGTH = 8
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.ICMP
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析ICMP数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        return len(data) >= offset + self.ICMP_MIN_HEADER_LENGTH
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析ICMP数据包头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据长度不足，无法解析ICMP头部")
        
        # 解析ICMP头部
        icmp_header = data[offset:offset + self.ICMP_MIN_HEADER_LENGTH]
        
        # 解包ICMP头部
        icmp_type, code, checksum, rest = struct.unpack('!BBHL', icmp_header)
        
        # 解析ICMP类型和代码
        type_name = self._get_icmp_type_name(icmp_type)
        code_name = self._get_icmp_code_name(icmp_type, code)
        
        fields = {
            'type': icmp_type,
            'type_name': type_name,
            'code': code,
            'code_name': code_name,
            'checksum': checksum,
            'rest_of_header': rest,
            'header_length': self.ICMP_MIN_HEADER_LENGTH
        }
        
        next_offset = offset + self.ICMP_MIN_HEADER_LENGTH
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.ICMP
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """ICMP是网络层协议，通常没有下一层协议"""
        return None
    
    def _get_icmp_type_name(self, icmp_type: int) -> str:
        """
        获取ICMP类型名称
        
        Args:
            icmp_type: ICMP类型值
            
        Returns:
            str: 类型名称
        """
        type_names = {
            0: 'Echo Reply',
            3: 'Destination Unreachable',
            4: 'Source Quench',
            5: 'Redirect',
            8: 'Echo Request',
            9: 'Router Advertisement',
            10: 'Router Solicitation',
            11: 'Time Exceeded',
            12: 'Parameter Problem',
            13: 'Timestamp Request',
            14: 'Timestamp Reply',
            15: 'Information Request',
            16: 'Information Reply'
        }
        
        return type_names.get(icmp_type, f'Unknown Type ({icmp_type})')
    
    def _get_icmp_code_name(self, icmp_type: int, code: int) -> str:
        """
        获取ICMP代码名称
        
        Args:
            icmp_type: ICMP类型值
            code: 代码值
            
        Returns:
            str: 代码名称
        """
        if icmp_type == 3:  # Destination Unreachable
            code_names = {
                0: 'Network Unreachable',
                1: 'Host Unreachable',
                2: 'Protocol Unreachable',
                3: 'Port Unreachable',
                4: 'Fragmentation Needed',
                5: 'Source Route Failed'
            }
            return code_names.get(code, f'Unknown Code ({code})')
        elif icmp_type == 5:  # Redirect
            code_names = {
                0: 'Redirect for Network',
                1: 'Redirect for Host',
                2: 'Redirect for Type of Service and Network',
                3: 'Redirect for Type of Service and Host'
            }
            return code_names.get(code, f'Unknown Code ({code})')
        elif icmp_type == 11:  # Time Exceeded
            code_names = {
                0: 'TTL Exceeded in Transit',
                1: 'Fragment Reassembly Time Exceeded'
            }
            return code_names.get(code, f'Unknown Code ({code})')
        
        return f'Code {code}'


# 注册解析器到工厂
from .base_parser import parser_factory
parser_factory.register_parser(ProtocolType.TCP, TCPParser)
parser_factory.register_parser(ProtocolType.UDP, UDPParser)
parser_factory.register_parser(ProtocolType.ICMP, ICMPParser)