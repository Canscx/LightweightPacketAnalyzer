"""
ARP协议解析器

解析ARP请求和响应报文
"""

import struct
from typing import Dict, Any, Optional
from .base_parser import BaseProtocolParser, ProtocolType


class ARPParser(BaseProtocolParser):
    """ARP协议解析器"""
    
    # ARP头部长度（字节）
    ARP_HEADER_LENGTH = 28
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.ARP
    
    def can_parse(self, data: bytes, offset: int = 0) -> bool:
        """
        检查是否可以解析ARP数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            bool: 是否可以解析
        """
        return len(data) >= offset + self.ARP_HEADER_LENGTH
    
    def parse(self, data: bytes, offset: int = 0) -> tuple[Dict[str, Any], int]:
        """
        解析ARP数据包
        
        Args:
            data: 原始数据
            offset: 数据偏移量
            
        Returns:
            tuple: (解析结果字典, 下一层数据偏移量)
        """
        if not self.can_parse(data, offset):
            raise ValueError("数据长度不足，无法解析ARP头部")
        
        # 解析ARP头部
        arp_header = data[offset:offset + self.ARP_HEADER_LENGTH]
        
        # 解包ARP头部
        # 格式：硬件类型(2) + 协议类型(2) + 硬件地址长度(1) + 协议地址长度(1) + 操作码(2) + 
        #      发送方硬件地址(6) + 发送方协议地址(4) + 目标硬件地址(6) + 目标协议地址(4)
        hardware_type, protocol_type, hw_addr_len, proto_addr_len, opcode = struct.unpack('!HHBBH', arp_header[:8])
        
        # 提取地址信息
        sender_hw_addr = arp_header[8:14]
        sender_proto_addr = arp_header[14:18]
        target_hw_addr = arp_header[18:24]
        target_proto_addr = arp_header[24:28]
        
        # 格式化MAC地址
        sender_mac = self._format_mac_address(sender_hw_addr)
        target_mac = self._format_mac_address(target_hw_addr)
        
        # 格式化IP地址
        sender_ip = self._format_ip_address(sender_proto_addr)
        target_ip = self._format_ip_address(target_proto_addr)
        
        # 解析操作类型
        operation_name = self._get_operation_name(opcode)
        
        # 解析硬件类型
        hardware_type_name = self._get_hardware_type_name(hardware_type)
        
        # 解析协议类型
        protocol_type_name = self._get_protocol_type_name(protocol_type)
        
        fields = {
            'hardware_type': hardware_type,
            'hardware_type_name': hardware_type_name,
            'protocol_type': protocol_type,
            'protocol_type_name': protocol_type_name,
            'hardware_address_length': hw_addr_len,
            'protocol_address_length': proto_addr_len,
            'opcode': opcode,
            'operation': operation_name,
            'sender_hardware_address': sender_mac,
            'sender_protocol_address': sender_ip,
            'target_hardware_address': target_mac,
            'target_protocol_address': target_ip,
            'header_length': self.ARP_HEADER_LENGTH
        }
        
        next_offset = offset + self.ARP_HEADER_LENGTH
        
        return fields, next_offset
    
    def get_protocol_type(self) -> ProtocolType:
        """获取协议类型"""
        return ProtocolType.ARP
    
    def get_next_protocol_type(self, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """ARP是网络层协议，通常没有下一层协议"""
        return None
    
    def _format_mac_address(self, mac_bytes: bytes) -> str:
        """
        格式化MAC地址
        
        Args:
            mac_bytes: MAC地址字节
            
        Returns:
            str: 格式化的MAC地址
        """
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    
    def _format_ip_address(self, ip_bytes: bytes) -> str:
        """
        格式化IP地址
        
        Args:
            ip_bytes: IP地址字节
            
        Returns:
            str: 格式化的IP地址
        """
        return '.'.join(str(b) for b in ip_bytes)
    
    def _get_operation_name(self, opcode: int) -> str:
        """
        获取ARP操作名称
        
        Args:
            opcode: 操作码
            
        Returns:
            str: 操作名称
        """
        operations = {
            1: 'ARP Request',
            2: 'ARP Reply',
            3: 'RARP Request',
            4: 'RARP Reply',
            5: 'DRARP Request',
            6: 'DRARP Reply',
            7: 'DRARP Error',
            8: 'InARP Request',
            9: 'InARP Reply'
        }
        
        return operations.get(opcode, f'Unknown Operation ({opcode})')
    
    def _get_hardware_type_name(self, hw_type: int) -> str:
        """
        获取硬件类型名称
        
        Args:
            hw_type: 硬件类型值
            
        Returns:
            str: 硬件类型名称
        """
        hardware_types = {
            1: 'Ethernet',
            2: 'Experimental Ethernet',
            3: 'Amateur Radio AX.25',
            4: 'Proteon ProNET Token Ring',
            5: 'Chaos',
            6: 'IEEE 802 Networks',
            7: 'ARCNET',
            8: 'Hyperchannel',
            9: 'Lanstar',
            10: 'Autonet Short Address',
            11: 'LocalTalk',
            12: 'LocalNet',
            13: 'Ultra link',
            14: 'SMDS',
            15: 'Frame Relay',
            16: 'Asynchronous Transmission Mode (ATM)',
            17: 'HDLC',
            18: 'Fibre Channel',
            19: 'Asynchronous Transmission Mode (ATM)',
            20: 'Serial Line',
            21: 'Asynchronous Transmission Mode (ATM)'
        }
        
        return hardware_types.get(hw_type, f'Unknown Hardware Type ({hw_type})')
    
    def _get_protocol_type_name(self, proto_type: int) -> str:
        """
        获取协议类型名称
        
        Args:
            proto_type: 协议类型值
            
        Returns:
            str: 协议类型名称
        """
        protocol_types = {
            0x0800: 'IPv4',
            0x0806: 'ARP',
            0x0835: 'RARP',
            0x86DD: 'IPv6',
            0x8100: 'VLAN-tagged frame',
            0x8137: 'IPX',
            0x8863: 'PPPoE Discovery Stage',
            0x8864: 'PPPoE Session Stage'
        }
        
        return protocol_types.get(proto_type, f'Unknown Protocol Type (0x{proto_type:04x})')


# 注册解析器到工厂
from .base_parser import parser_factory
parser_factory.register_parser(ProtocolType.ARP, ARPParser)