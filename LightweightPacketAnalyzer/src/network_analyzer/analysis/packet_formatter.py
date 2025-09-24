"""
数据包格式化器

将解析后的数据包格式化为用户友好的文本和十六进制显示
"""

from typing import Dict, Any, List, Optional
from .base_parser import ParsedPacket, ProtocolType
import textwrap


class PacketFormatter:
    """
    数据包格式化器
    
    将解析后的数据包格式化为用户友好的显示格式
    """
    
    def __init__(self):
        """初始化格式化器"""
        self.indent_size = 2
        self.hex_bytes_per_line = 16
        
        # 协议显示名称映射
        self.protocol_display_names = {
            ProtocolType.ETHERNET: "以太网 (Ethernet)",
            ProtocolType.ARP: "地址解析协议 (ARP)",
            ProtocolType.IPV4: "互联网协议版本4 (IPv4)",
            ProtocolType.IPV6: "互联网协议版本6 (IPv6)",
            ProtocolType.TCP: "传输控制协议 (TCP)",
            ProtocolType.UDP: "用户数据报协议 (UDP)",
            ProtocolType.ICMP: "互联网控制消息协议 (ICMP)"
        }
    
    def format_packet_summary(self, parsed_packet: ParsedPacket) -> str:
        """
        格式化数据包摘要信息
        
        Args:
            parsed_packet: 解析后的数据包
            
        Returns:
            str: 格式化的摘要信息
        """
        try:
            summary_parts = []
            
            # 基本信息
            summary_parts.append(f"数据包大小: {len(parsed_packet.raw_data)} 字节")
            summary_parts.append(f"协议层数: {len(parsed_packet.layers)}")
            
            # 协议栈信息
            protocols = " → ".join([
                self.protocol_display_names.get(layer['protocol'], layer['protocol'].value)
                for layer in parsed_packet.layers
            ])
            summary_parts.append(f"协议栈: {protocols}")
            
            # 关键信息提取
            key_info = self._extract_key_info(parsed_packet)
            if key_info:
                summary_parts.extend(key_info)
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"格式化摘要时出错: {e}"
    
    def format_packet_details(self, parsed_packet: ParsedPacket) -> str:
        """
        格式化数据包详细信息
        
        Args:
            parsed_packet: 解析后的数据包
            
        Returns:
            str: 格式化的详细信息
        """
        try:
            details = []
            
            # 标题
            details.append("=" * 60)
            details.append("数据包详细信息")
            details.append("=" * 60)
            details.append("")
            
            # 基本信息
            details.append("基本信息:")
            details.append(f"  数据包大小: {len(parsed_packet.raw_data)} 字节")
            details.append(f"  协议层数: {len(parsed_packet.layers)}")
            if parsed_packet.payload_size > 0:
                details.append(f"  载荷大小: {parsed_packet.payload_size} 字节")
            details.append("")
            
            # 逐层显示协议信息
            for protocol_type, fields in parsed_packet.layers.items():
                protocol_details = self._format_protocol_layer(protocol_type, fields)
                details.extend(protocol_details)
                details.append("")
            
            # 载荷信息
            if parsed_packet.payload and len(parsed_packet.payload) > 0:
                payload_details = self._format_payload(parsed_packet.payload)
                details.extend(payload_details)
                details.append("")
            
            return "\n".join(details)
            
        except Exception as e:
            return f"格式化详细信息时出错: {e}"
    
    def format_hex_dump(self, data: bytes, offset: int = 0) -> str:
        """
        格式化十六进制转储
        
        Args:
            data: 要格式化的数据
            offset: 起始偏移量
            
        Returns:
            str: 格式化的十六进制转储
        """
        try:
            lines = []
            
            for i in range(0, len(data), self.hex_bytes_per_line):
                # 计算当前行的地址
                addr = offset + i
                
                # 获取当前行的数据
                chunk = data[i:i + self.hex_bytes_per_line]
                
                # 格式化十六进制部分
                hex_part = ' '.join(f'{b:02x}' for b in chunk)
                hex_part = hex_part.ljust(self.hex_bytes_per_line * 3 - 1)
                
                # 格式化ASCII部分
                ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                
                # 组合成一行
                line = f"{addr:08x}  {hex_part}  |{ascii_part}|"
                lines.append(line)
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"格式化十六进制转储时出错: {e}"
    
    def format_packet_tree(self, parsed_packet: ParsedPacket) -> str:
        """
        格式化数据包树形结构
        
        Args:
            parsed_packet: 解析后的数据包
            
        Returns:
            str: 格式化的树形结构
        """
        try:
            tree_lines = []
            
            # 根节点
            tree_lines.append("📦 数据包")
            
            # 协议层
            protocol_list = list(parsed_packet.layers.items())
            for i, (protocol_type, fields) in enumerate(protocol_list):
                is_last_protocol = (i == len(protocol_list) - 1)
                
                # 协议节点
                protocol_name = self.protocol_display_names.get(protocol_type, protocol_type.value)
                prefix = "└── " if is_last_protocol else "├── "
                tree_lines.append(f"{prefix}🔗 {protocol_name}")
                
                # 协议字段
                field_items = list(fields.items())
                for j, (key, value) in enumerate(field_items):
                    is_last_field = (j == len(field_items) - 1)
                    
                    # 字段前缀
                    if is_last_protocol:
                        field_prefix = "    └── " if is_last_field else "    ├── "
                    else:
                        field_prefix = "│   └── " if is_last_field else "│   ├── "
                    
                    # 格式化字段值
                    formatted_value = self._format_field_value(key, value)
                    tree_lines.append(f"{field_prefix}{key}: {formatted_value}")
            
            # 载荷
            if parsed_packet.payload and len(parsed_packet.payload) > 0:
                tree_lines.append("└── 📄 载荷数据")
                tree_lines.append(f"    └── 大小: {len(parsed_packet.payload)} 字节")
            
            return "\n".join(tree_lines)
            
        except Exception as e:
            return f"格式化树形结构时出错: {e}"
    
    def _extract_key_info(self, parsed_packet: ParsedPacket) -> List[str]:
        """
        提取关键信息
        
        Args:
            parsed_packet: 解析后的数据包
            
        Returns:
            List[str]: 关键信息列表
        """
        key_info = []
        
        try:
            # 提取源和目标信息
            src_info = []
            dst_info = []
            
            # MAC地址
            if ProtocolType.ETHERNET in parsed_packet.layers:
                eth_fields = parsed_packet.layers[ProtocolType.ETHERNET]
                src_info.append(f"MAC: {eth_fields.get('source_mac', 'N/A')}")
                dst_info.append(f"MAC: {eth_fields.get('destination_mac', 'N/A')}")
            
            # IP地址
            for ip_proto in [ProtocolType.IPV4, ProtocolType.IPV6]:
                if ip_proto in parsed_packet.layers:
                    ip_fields = parsed_packet.layers[ip_proto]
                    src_info.append(f"IP: {ip_fields.get('source_ip', 'N/A')}")
                    dst_info.append(f"IP: {ip_fields.get('destination_ip', 'N/A')}")
                    break
            
            # 端口号
            for transport_proto in [ProtocolType.TCP, ProtocolType.UDP]:
                if transport_proto in parsed_packet.layers:
                    transport_fields = parsed_packet.layers[transport_proto]
                    src_info.append(f"端口: {transport_fields.get('source_port', 'N/A')}")
                    dst_info.append(f"端口: {transport_fields.get('destination_port', 'N/A')}")
                    break
            
            if src_info and dst_info:
                key_info.append(f"源地址: {', '.join(src_info)}")
                key_info.append(f"目标地址: {', '.join(dst_info)}")
            
            # ARP特殊处理
            if ProtocolType.ARP in parsed_packet.layers:
                arp_fields = parsed_packet.layers[ProtocolType.ARP]
                operation = arp_fields.get('operation', 'Unknown')
                key_info.append(f"ARP操作: {operation}")
            
        except Exception as e:
            key_info.append(f"提取关键信息时出错: {e}")
        
        return key_info
    
    def _format_protocol_layer(self, protocol_type: ProtocolType, fields: Dict[str, Any]) -> List[str]:
        """
        格式化协议层信息
        
        Args:
            protocol_type: 协议类型
            fields: 协议字段
            
        Returns:
            List[str]: 格式化的协议层信息
        """
        lines = []
        
        try:
            # 协议标题
            protocol_name = self.protocol_display_names.get(protocol_type, protocol_type.value)
            lines.append(f"{protocol_name}:")
            lines.append("-" * (len(protocol_name) + 1))
            
            # 格式化字段
            for key, value in fields.items():
                formatted_value = self._format_field_value(key, value)
                lines.append(f"  {key}: {formatted_value}")
            
        except Exception as e:
            lines.append(f"  格式化协议层时出错: {e}")
        
        return lines
    
    def _format_field_value(self, key: str, value: Any) -> str:
        """
        格式化字段值
        
        Args:
            key: 字段名
            value: 字段值
            
        Returns:
            str: 格式化的字段值
        """
        try:
            if isinstance(value, dict):
                # 字典类型，如TCP标志位
                if key == 'flags_detail':
                    active_flags = [flag for flag, active in value.items() if active]
                    return f"{', '.join(active_flags)}" if active_flags else "无"
                else:
                    return str(value)
            
            elif isinstance(value, bytes):
                # 字节类型，显示十六进制
                if len(value) <= 8:
                    return ' '.join(f'{b:02x}' for b in value)
                else:
                    return f"{len(value)} 字节数据"
            
            elif isinstance(value, int):
                # 整数类型，根据字段名决定显示格式
                if 'checksum' in key.lower():
                    return f"0x{value:04x}"
                elif 'port' in key.lower():
                    return str(value)
                elif 'length' in key.lower() or 'size' in key.lower():
                    return f"{value} 字节"
                else:
                    return str(value)
            
            else:
                return str(value)
                
        except Exception as e:
            return f"格式化错误: {e}"
    
    def _format_payload(self, payload: bytes) -> List[str]:
        """
        格式化载荷数据
        
        Args:
            payload: 载荷数据
            
        Returns:
            List[str]: 格式化的载荷信息
        """
        lines = []
        
        try:
            lines.append("载荷数据:")
            lines.append("-" * 9)
            lines.append(f"  大小: {len(payload)} 字节")
            
            # 如果载荷较小，显示十六进制转储
            if len(payload) <= 256:
                lines.append("  十六进制转储:")
                hex_dump = self.format_hex_dump(payload)
                for line in hex_dump.split('\n'):
                    lines.append(f"    {line}")
            else:
                lines.append("  载荷过大，仅显示前256字节:")
                hex_dump = self.format_hex_dump(payload[:256])
                for line in hex_dump.split('\n'):
                    lines.append(f"    {line}")
                lines.append(f"    ... (省略 {len(payload) - 256} 字节)")
            
        except Exception as e:
            lines.append(f"  格式化载荷时出错: {e}")
        
        return lines


# 创建全局格式化器实例
packet_formatter = PacketFormatter()