"""
以太网协议解析器

解析以太网帧头部信息，包括目标MAC、源MAC和类型字段
"""

import struct
from typing import Dict, Any, Optional
from .base_parser import BaseProtocolParser, ProtocolType


class EthernetParser(BaseProtocolParser):
    """以太网协议解析器"""
    
    # 以太网帧头部长度（字节）
    ETHERNET_HEADER_LENGTH = 14
    
    # 以太网类型字段值
    ETHERTYPE_IPV4 = 0x0800
    ETHERTYPE_IPV6 = 0x86DD
    ETHERTYPE_ARP = 0x0806
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.ETHERNET
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析以太网帧
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        # 检查数据长度是否足够包含以太网头部
        return len(data) >= offset + self.ETHERNET_HEADER_LENGTH
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析以太网帧头部
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据长度不足，无法解析以太网帧头部")
        
        # 解析以太网帧头部
        # 格式: 目标MAC(6字节) + 源MAC(6字节) + 类型(2字节)
        ethernet_header = data[offset:offset + self.ETHERNET_HEADER_LENGTH]
        
        # 使用struct解包
        dst_mac_bytes, src_mac_bytes, ethertype = struct.unpack('!6s6sH', ethernet_header)
        
        # 格式化MAC地址
        dst_mac = self._format_mac_address(dst_mac_bytes)
        src_mac = self._format_mac_address(src_mac_bytes)
        
        # 解析以太网类型
        ethertype_name = self._get_ethertype_name(ethertype)
        
        fields = {
            'destination_mac': dst_mac,
            'source_mac': src_mac,
            'ethertype': ethertype,
            'ethertype_name': ethertype_name,
            'header_length': self.ETHERNET_HEADER_LENGTH
        }
        
        next_offset = offset + self.ETHERNET_HEADER_LENGTH
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.ETHERNET
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """
        根据以太网类型字段确定下一层协议类型
        
        Args:
            fields: 以太网层解析的字段
            
        Returns:
            Optional[ProtocolType]: 下一层协议类型
        """
        ethertype = fields.get('ethertype')
        
        if ethertype == self.ETHERTYPE_IPV4:
            return ProtocolType.IPV4
        elif ethertype == self.ETHERTYPE_IPV6:
            return ProtocolType.IPV6
        elif ethertype == self.ETHERTYPE_ARP:
            return ProtocolType.ARP
        
        return None
    
    def _format_mac_address(self, mac_bytes: bytes) -> str:
        """
        格式化MAC地址为可读字符串
        
        Args:
            mac_bytes: MAC地址字节数据
            
        Returns:
            str: 格式化的MAC地址 (例: "00:11:22:33:44:55")
        """
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    
    def _get_ethertype_name(self, ethertype: int) -> str:
        """
        获取以太网类型名称
        
        Args:
            ethertype: 以太网类型值
            
        Returns:
            str: 类型名称
        """
        ethertype_names = {
            self.ETHERTYPE_IPV4: 'IPv4',
            self.ETHERTYPE_IPV6: 'IPv6',
            self.ETHERTYPE_ARP: 'ARP',
            0x8100: 'VLAN',
            0x88CC: 'LLDP',
            0x8847: 'MPLS Unicast',
            0x8848: 'MPLS Multicast'
        }
        
        return ethertype_names.get(ethertype, f'Unknown (0x{ethertype:04x})')


# 注册解析器到工厂
from .base_parser import parser_factory
parser_factory.register_parser(ProtocolType.ETHERNET, EthernetParser)