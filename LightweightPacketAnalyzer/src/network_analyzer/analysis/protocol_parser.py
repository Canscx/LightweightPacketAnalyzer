"""
核心协议解析器

整合所有协议解析器，提供统一的数据包解析接口
"""

from typing import Dict, Any, List, Optional, Tuple
from .base_parser import BaseProtocolParser, ProtocolType, ParsedPacket, parser_factory
import logging


class ProtocolParser:
    """
    核心协议解析器
    
    整合所有协议解析器，提供统一的数据包解析接口
    """
    
    def __init__(self):
        """初始化协议解析器"""
        self.logger = logging.getLogger(__name__)
        
        # 确保所有解析器都已注册
        self._ensure_parsers_registered()
        
        # 协议层级映射
        self.protocol_layers = {
            ProtocolType.ETHERNET: 1,  # 数据链路层
            ProtocolType.ARP: 2,       # 网络层
            ProtocolType.IPV4: 2,      # 网络层
            ProtocolType.IPV6: 2,      # 网络层
            ProtocolType.TCP: 3,       # 传输层
            ProtocolType.UDP: 3,       # 传输层
            ProtocolType.ICMP: 3,      # 传输层
        }
        
        # 协议类型到EtherType的映射
        self.ethertype_to_protocol = {
            0x0800: ProtocolType.IPV4,
            0x86DD: ProtocolType.IPV6,
            0x0806: ProtocolType.ARP,
        }
        
        # IP协议号到协议类型的映射
        self.ip_protocol_to_type = {
            1: ProtocolType.ICMP,
            6: ProtocolType.TCP,
            17: ProtocolType.UDP,
        }
    
    def parse_packet(self, raw_data: bytes) -> ParsedPacket:
        """
        解析数据包
        
        Args:
            raw_data: 原始数据包字节
            
        Returns:
            ParsedPacket: 解析结果
        """
        try:
            parsed_packet = ParsedPacket()
            parsed_packet.raw_data = raw_data
            
            # 从以太网层开始解析
            current_offset = 0
            current_protocol = ProtocolType.ETHERNET
            
            while current_protocol and current_offset < len(raw_data):
                # 获取对应的解析器
                parser = parser_factory.get_parser(current_protocol)
                if not parser:
                    self.logger.warning(f"未找到协议 {current_protocol} 的解析器")
                    break
                
                # 检查是否可以解析
                if not parser.can_parse(raw_data, current_offset):
                    self.logger.warning(f"数据不足，无法解析协议 {current_protocol}")
                    break
                
                try:
                    # 解析当前层协议
                    fields, next_offset = parser.parse(raw_data, current_offset)
                    
                    # 添加解析结果到数据包
                    parsed_packet.add_layer(current_protocol, fields)
                    
                    # 确定下一层协议
                    next_protocol = self._determine_next_protocol(current_protocol, fields)
                    
                    # 更新偏移量和协议类型
                    current_offset = next_offset
                    current_protocol = next_protocol
                    
                except Exception as e:
                    self.logger.error(f"解析协议 {current_protocol} 时出错: {e}")
                    break
            
            # 如果还有剩余数据，作为payload保存
            if current_offset < len(raw_data):
                payload = raw_data[current_offset:]
                parsed_packet.payload = payload
                parsed_packet.payload_size = len(payload)
            
            return parsed_packet
            
        except Exception as e:
            self.logger.error(f"解析数据包时出错: {e}")
            # 返回一个包含错误信息的ParsedPacket
            error_packet = ParsedPacket()
            error_packet.raw_data = raw_data
            error_packet.add_error(str(e))
            return error_packet
    
    def _determine_next_protocol(self, current_protocol: ProtocolType, fields: Dict[str, Any]) -> Optional[ProtocolType]:
        """
        根据当前协议和字段确定下一层协议
        
        Args:
            current_protocol: 当前协议类型
            fields: 当前协议解析的字段
            
        Returns:
            Optional[ProtocolType]: 下一层协议类型，如果没有则返回None
        """
        try:
            if current_protocol == ProtocolType.ETHERNET:
                # 以太网层，根据EtherType确定下一层
                ethertype = fields.get('ethertype')
                if ethertype:
                    return self.ethertype_to_protocol.get(ethertype)
            
            elif current_protocol in [ProtocolType.IPV4, ProtocolType.IPV6]:
                # IP层，根据协议号确定下一层
                protocol = fields.get('protocol')
                if protocol:
                    return self.ip_protocol_to_type.get(protocol)
            
            elif current_protocol in [ProtocolType.TCP, ProtocolType.UDP, ProtocolType.ICMP, ProtocolType.ARP]:
                # 传输层或ARP，通常没有下一层
                return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"确定下一层协议时出错: {e}")
            return None
    
    def get_supported_protocols(self) -> List[ProtocolType]:
        """
        获取支持的协议类型列表
        
        Returns:
            List[ProtocolType]: 支持的协议类型
        """
        return list(parser_factory.parsers.keys())
    
    def get_protocol_info(self, protocol_type: ProtocolType) -> Dict[str, Any]:
        """
        获取协议信息
        
        Args:
            protocol_type: 协议类型
            
        Returns:
            Dict[str, Any]: 协议信息
        """
        parser = parser_factory.get_parser(protocol_type)
        if not parser:
            return {}
        
        return {
            'name': protocol_type.value,
            'layer': self.protocol_layers.get(protocol_type, 0),
            'description': self._get_protocol_description(protocol_type)
        }
    
    def _get_protocol_description(self, protocol_type: ProtocolType) -> str:
        """
        获取协议描述
        
        Args:
            protocol_type: 协议类型
            
        Returns:
            str: 协议描述
        """
        descriptions = {
            ProtocolType.ETHERNET: "以太网协议 - 数据链路层协议，定义帧格式和MAC地址",
            ProtocolType.ARP: "地址解析协议 - 将IP地址解析为MAC地址",
            ProtocolType.IPV4: "互联网协议版本4 - 网络层协议，提供数据包路由",
            ProtocolType.IPV6: "互联网协议版本6 - 新一代网络层协议",
            ProtocolType.TCP: "传输控制协议 - 可靠的面向连接的传输层协议",
            ProtocolType.UDP: "用户数据报协议 - 无连接的传输层协议",
            ProtocolType.ICMP: "互联网控制消息协议 - 用于网络诊断和错误报告"
        }
        
        return descriptions.get(protocol_type, "未知协议")
    
    def _ensure_parsers_registered(self):
        """确保所有解析器都已注册"""
        try:
            # 导入所有解析器模块以触发注册
            from . import ethernet_parser
            from . import ip_parser
            from . import transport_parser
            from . import arp_parser
            
            self.logger.info("所有协议解析器已注册")
            
        except ImportError as e:
            self.logger.error(f"导入解析器模块时出错: {e}")
    
    def validate_packet_structure(self, parsed_packet: ParsedPacket) -> Tuple[bool, List[str]]:
        """
        验证数据包结构的合理性
        
        Args:
            parsed_packet: 解析后的数据包
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        try:
            # 检查是否有以太网层
            if ProtocolType.ETHERNET not in parsed_packet.layers:
                errors.append("缺少以太网层")
            
            # 检查协议层级的合理性
            layer_numbers = []
            for protocol_type in parsed_packet.layers.keys():
                layer_num = self.protocol_layers.get(protocol_type, 0)
                if layer_num > 0:
                    layer_numbers.append(layer_num)
            
            # 检查层级是否连续
            if layer_numbers:
                layer_numbers.sort()
                for i in range(len(layer_numbers) - 1):
                    if layer_numbers[i + 1] - layer_numbers[i] > 1:
                        errors.append(f"协议层级不连续: {layer_numbers}")
                        break
            
            # 检查特定协议的字段完整性
            for protocol_type, fields in parsed_packet.layers.items():
                protocol_errors = self._validate_protocol_fields(protocol_type, fields)
                errors.extend(protocol_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"验证过程中出错: {e}")
            return False, errors
    
    def _validate_protocol_fields(self, protocol_type: ProtocolType, fields: Dict[str, Any]) -> List[str]:
        """
        验证特定协议的字段
        
        Args:
            protocol_type: 协议类型
            fields: 协议字段
            
        Returns:
            List[str]: 错误信息列表
        """
        errors = []
        
        try:
            if protocol_type == ProtocolType.ETHERNET:
                required_fields = ['destination_mac', 'source_mac', 'ethertype']
                for field in required_fields:
                    if field not in fields:
                        errors.append(f"以太网协议缺少字段: {field}")
            
            elif protocol_type == ProtocolType.IPV4:
                required_fields = ['version', 'source_ip', 'destination_ip', 'protocol']
                for field in required_fields:
                    if field not in fields:
                        errors.append(f"IPv4协议缺少字段: {field}")
            
            elif protocol_type == ProtocolType.TCP:
                required_fields = ['source_port', 'destination_port', 'sequence_number']
                for field in required_fields:
                    if field not in fields:
                        errors.append(f"TCP协议缺少字段: {field}")
            
            elif protocol_type == ProtocolType.UDP:
                required_fields = ['source_port', 'destination_port', 'length']
                for field in required_fields:
                    if field not in fields:
                        errors.append(f"UDP协议缺少字段: {field}")
            
        except Exception as e:
            errors.append(f"验证协议字段时出错: {e}")
        
        return errors


# 创建全局解析器实例
protocol_parser = ProtocolParser()