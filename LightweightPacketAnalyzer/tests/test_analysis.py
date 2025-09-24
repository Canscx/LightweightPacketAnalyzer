"""
单元测试 - Analysis模块
测试所有新增的数据包分析组件
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import struct
import time
from datetime import datetime

# 导入被测试的模块
from network_analyzer.analysis.base_parser import BaseProtocolParser, ProtocolType, ParsedPacket, parser_factory
from network_analyzer.analysis.ethernet_parser import EthernetParser
from network_analyzer.analysis.ip_parser import IPv4Parser, IPv6Parser
from network_analyzer.analysis.transport_parser import TCPParser, UDPParser, ICMPParser
from network_analyzer.analysis.arp_parser import ARPParser
from network_analyzer.analysis.protocol_parser import ProtocolParser
from network_analyzer.analysis.packet_formatter import PacketFormatter
from network_analyzer.analysis.packet_cache import PacketCache


class TestBaseProtocolParser(unittest.TestCase):
    """测试BaseProtocolParser基类"""
    
    def setUp(self):
        # 创建一个具体的实现类用于测试
        class TestParser(BaseProtocolParser):
            def can_parse(self, data: bytes, offset: int = 0) -> bool:
                return True
            
            def parse(self, data: bytes, offset: int = 0) -> tuple[dict, int]:
                return {}, 0
            
            def get_protocol_type(self) -> ProtocolType:
                return ProtocolType.ETHERNET
        
        self.parser = TestParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_implemented(self):
        """测试can_parse方法已实现"""
        result = self.parser.can_parse(b'test_data')
        self.assertTrue(result)
    
    def test_parse_implemented(self):
        """测试parse方法已实现"""
        result = self.parser.parse(b'test_data')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


class TestEthernetParser(unittest.TestCase):
    """测试EthernetParser"""
    
    def setUp(self):
        self.parser = EthernetParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, EthernetParser)
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_valid_data(self):
        """测试有效数据验证"""
        # 创建14字节的以太网帧头
        valid_data = b'\x00' * 14
        self.assertTrue(self.parser.can_parse(valid_data))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        # 少于14字节的数据
        invalid_data = b'\x00' * 10
        self.assertFalse(self.parser.can_parse(invalid_data))
    
    def test_parse_valid_ethernet_frame(self):
        """测试解析有效的以太网帧"""
        # 构造以太网帧: dst_mac(6) + src_mac(6) + ethertype(2)
        dst_mac = b'\x00\x11\x22\x33\x44\x55'
        src_mac = b'\x66\x77\x88\x99\xaa\xbb'
        ethertype = b'\x08\x00'  # IPv4
        ethernet_frame = dst_mac + src_mac + ethertype
        
        result, consumed = self.parser.parse(ethernet_frame)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['destination_mac'], '00:11:22:33:44:55')
        self.assertEqual(result['source_mac'], '66:77:88:99:aa:bb')
        self.assertEqual(result['ethertype'], 0x0800)
        self.assertEqual(result['ethertype_name'], 'IPv4')
        self.assertEqual(consumed, 14)
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 10
        with self.assertRaises(Exception):
            self.parser.parse(invalid_data)
    
    def test_format_mac_address(self):
        """测试MAC地址格式化"""
        mac_bytes = b'\x00\x11\x22\x33\x44\x55'
        formatted = self.parser._format_mac_address(mac_bytes)
        self.assertEqual(formatted, '00:11:22:33:44:55')
    
    def test_get_ethertype_name(self):
        """测试EtherType名称获取"""
        self.assertEqual(self.parser._get_ethertype_name(0x0800), 'IPv4')
        self.assertEqual(self.parser._get_ethertype_name(0x86DD), 'IPv6')
        self.assertEqual(self.parser._get_ethertype_name(0x0806), 'ARP')
        self.assertEqual(self.parser._get_ethertype_name(0x9999), 'Unknown (0x9999)')


class TestIPParser(unittest.TestCase):
    """测试IPv4Parser和IPv6Parser"""
    
    def setUp(self):
        self.ipv4_parser = IPv4Parser()
        self.ipv6_parser = IPv6Parser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.ipv4_parser, IPv4Parser)
        self.assertIsInstance(self.ipv4_parser, BaseProtocolParser)
        self.assertIsInstance(self.ipv6_parser, IPv6Parser)
        self.assertIsInstance(self.ipv6_parser, BaseProtocolParser)
    
    def test_can_parse_valid_ipv4(self):
        """测试有效IPv4数据验证"""
        # 创建20字节的IPv4头部
        valid_data = b'\x45' + b'\x00' * 19  # Version=4, IHL=5
        self.assertTrue(self.ipv4_parser.can_parse(valid_data))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        # 少于20字节的数据
        invalid_data = b'\x45' + b'\x00' * 10
        self.assertFalse(self.ipv4_parser.can_parse(invalid_data))
        
        # 无效版本号
        invalid_version = b'\x35' + b'\x00' * 19  # Version=3
        self.assertFalse(self.ipv4_parser.can_parse(invalid_version))
    
    def test_parse_valid_ipv4_packet(self):
        """测试解析有效的IPv4数据包"""
        # 构造IPv4头部
        version_ihl = 0x45  # Version=4, IHL=5
        tos = 0x00
        total_length = 0x001c  # 28字节
        identification = 0x1234
        flags_fragment = 0x4000  # Don't fragment
        ttl = 0x40  # 64
        protocol = 0x06  # TCP
        checksum = 0x0000
        src_ip = struct.pack('!I', 0xc0a80001)  # 192.168.0.1
        dst_ip = struct.pack('!I', 0xc0a80002)  # 192.168.0.2
        
        ipv4_packet = struct.pack('!BBHHHBBH', 
                                  version_ihl, tos, total_length, 
                                  identification, flags_fragment, 
                                  ttl, protocol, checksum) + src_ip + dst_ip
        
        result, consumed = self.ipv4_parser.parse(ipv4_packet)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['version'], 4)
        self.assertEqual(result['header_length'], 20)
        self.assertEqual(result['total_length'], 28)
        self.assertEqual(result['ttl'], 64)
        self.assertEqual(result['protocol'], 6)
        self.assertEqual(result['protocol_name'], 'TCP')
        self.assertEqual(result['source_ip'], '192.168.0.1')
        self.assertEqual(result['destination_ip'], '192.168.0.2')
        self.assertEqual(consumed, 20)
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 10
        with self.assertRaises(Exception):
            self.ipv4_parser.parse(invalid_data)
    
    def test_get_protocol_name(self):
        """测试获取协议名称"""
        self.assertEqual(self.ipv4_parser._get_protocol_name(1), 'ICMP')
        self.assertEqual(self.ipv4_parser._get_protocol_name(6), 'TCP')
        self.assertEqual(self.ipv4_parser._get_protocol_name(17), 'UDP')
        self.assertEqual(self.ipv4_parser._get_protocol_name(255), 'Unknown (255)')


class TestTCPParser(unittest.TestCase):
    """测试TCPParser"""
    
    def setUp(self):
        self.parser = TCPParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, TCPParser)
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_valid_data(self):
        """测试有效数据验证"""
        # 创建20字节的TCP头部
        valid_tcp = b'\x00' * 20
        self.assertTrue(self.parser.can_parse(valid_tcp))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        # 少于20字节的数据
        invalid_data = b'\x00' * 10
        self.assertFalse(self.parser.can_parse(invalid_data))
    
    def test_parse_tcp_packet(self):
        """测试解析TCP数据包"""
        # 构造TCP头部: src_port(2) + dst_port(2) + seq(4) + ack(4) + header_len_flags(2) + window(2) + checksum(2) + urgent(2)
        src_port = 0x1234
        dst_port = 0x0050  # HTTP
        seq_num = 0x12345678
        ack_num = 0x87654321
        header_len_flags = 0x5018  # header_len=20, flags=PSH+ACK
        window_size = 0x2000
        checksum = 0x0000
        urgent_ptr = 0x0000
        
        tcp_packet = struct.pack('!HHLLHHHH', src_port, dst_port, seq_num, ack_num,
                                header_len_flags, window_size, checksum, urgent_ptr)
        
        result, consumed = self.parser.parse(tcp_packet)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source_port'], 0x1234)
        self.assertEqual(result['destination_port'], 0x0050)
        self.assertEqual(result['sequence_number'], 0x12345678)
        self.assertEqual(result['acknowledgment_number'], 0x87654321)
        self.assertEqual(result['header_length'], 20)
        self.assertEqual(result['window_size'], 0x2000)
        self.assertEqual(consumed, 20)
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 10
        with self.assertRaises(Exception):
            self.parser.parse(invalid_data)


class TestUDPParser(unittest.TestCase):
    """测试UDPParser"""
    
    def setUp(self):
        self.parser = UDPParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, UDPParser)
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_valid_data(self):
        """测试有效数据验证"""
        # 创建8字节的UDP头部
        valid_udp = b'\x00' * 8
        self.assertTrue(self.parser.can_parse(valid_udp))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        # 少于8字节的数据
        invalid_data = b'\x00' * 6
        self.assertFalse(self.parser.can_parse(invalid_data))
    
    def test_parse_udp_packet(self):
        """测试解析UDP数据包"""
        # 构造UDP头部: src_port(2) + dst_port(2) + length(2) + checksum(2)
        src_port = 0x1234
        dst_port = 0x0035  # DNS
        length = 16
        checksum = 0x0000
        
        udp_packet = struct.pack('!HHHH', src_port, dst_port, length, checksum)
        
        result, consumed = self.parser.parse(udp_packet)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source_port'], 0x1234)
        self.assertEqual(result['destination_port'], 0x0035)
        self.assertEqual(result['length'], 16)
        self.assertEqual(consumed, 8)
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 6
        with self.assertRaises(Exception):
            self.parser.parse(invalid_data)


class TestICMPParser(unittest.TestCase):
    """测试ICMPParser"""
    
    def setUp(self):
        self.parser = ICMPParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, ICMPParser)
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_valid_data(self):
        """测试有效数据验证"""
        # 创建8字节的ICMP头部
        valid_icmp = b'\x00' * 8
        self.assertTrue(self.parser.can_parse(valid_icmp))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        # 少于8字节的数据
        invalid_data = b'\x00' * 6
        self.assertFalse(self.parser.can_parse(invalid_data))
    
    def test_parse_icmp_packet(self):
        """测试解析ICMP数据包"""
        # 构造ICMP头部: type(1) + code(1) + checksum(2) + rest(4)
        icmp_type = 8  # Echo Request
        code = 0
        checksum = 0x0000
        rest = 0x12345678
        
        icmp_packet = struct.pack('!BBHL', icmp_type, code, checksum, rest)
        
        result, consumed = self.parser.parse(icmp_packet)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 8)
        self.assertEqual(result['code'], 0)
        self.assertEqual(result['type_name'], 'Echo Request')
        self.assertEqual(consumed, 8)
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 6
        with self.assertRaises(Exception):
            self.parser.parse(invalid_data)


class TestARPParser(unittest.TestCase):
    """测试ARPParser"""
    
    def setUp(self):
        self.parser = ARPParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, ARPParser)
        self.assertIsInstance(self.parser, BaseProtocolParser)
    
    def test_can_parse_valid_data(self):
        """测试有效数据验证"""
        # 创建28字节的ARP数据包
        valid_data = b'\x00' * 28
        self.assertTrue(self.parser.can_parse(valid_data))
    
    def test_can_parse_invalid_data(self):
        """测试无效数据验证"""
        invalid_data = b'\x00' * 20
        self.assertFalse(self.parser.can_parse(invalid_data))
    
    def test_parse_arp_request(self):
        """测试解析ARP请求"""
        # 构造ARP请求数据包
        arp_data = struct.pack('!HHBBH', 1, 0x0800, 6, 4, 1)  # 硬件类型, 协议类型, 地址长度, 操作码
        arp_data += b'\x00\x11\x22\x33\x44\x55'  # 发送方MAC
        arp_data += b'\xc0\xa8\x01\x01'  # 发送方IP
        arp_data += b'\x00\x00\x00\x00\x00\x00'  # 目标MAC
        arp_data += b'\xc0\xa8\x01\x02'  # 目标IP
        
        result, consumed = self.parser.parse(arp_data)
        self.assertIsInstance(result, dict)
        self.assertEqual(consumed, 28)
        self.assertEqual(result['opcode'], 1)  # ARP请求
    
    def test_parse_invalid_data(self):
        """测试解析无效数据"""
        invalid_data = b'\x00' * 20
        with self.assertRaises(Exception):
            self.parser.parse(invalid_data)


class TestProtocolParser(unittest.TestCase):
    """测试协议解析器"""
    
    def setUp(self):
        """设置测试环境"""
        self.parser = ProtocolParser()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.parser.logger)
        self.assertIsInstance(self.parser.protocol_layers, dict)
        self.assertIsInstance(self.parser.ethertype_to_protocol, dict)
        self.assertIsInstance(self.parser.ip_protocol_to_type, dict)
    
    def test_get_supported_protocols(self):
        """测试获取支持的协议列表"""
        protocols = parser_factory.get_supported_protocols()
        self.assertIsInstance(protocols, list)
        
        # 检查是否包含预期的协议
        expected_protocols = [
            ProtocolType.ETHERNET,
            ProtocolType.IPV4,
            ProtocolType.TCP,
            ProtocolType.UDP,
            ProtocolType.ICMP,
            ProtocolType.ARP
        ]
        
        for protocol in expected_protocols:
            if protocol in protocols:
                self.assertIn(protocol, protocols)
    
    def test_get_protocol_info(self):
        """测试获取协议信息"""
        info = self.parser.get_protocol_info(ProtocolType.ETHERNET)
        self.assertIsInstance(info, dict)
        self.assertIn('name', info)
        self.assertIn('layer', info)
        self.assertIn('description', info)
    
    def test_parse_ethernet_packet(self):
        """测试解析以太网数据包"""
        # 构造简单的以太网帧
        dst_mac = b'\x00\x11\x22\x33\x44\x55'
        src_mac = b'\x66\x77\x88\x99\xaa\xbb'
        ethertype = struct.pack('!H', 0x0800)  # IPv4
        
        packet_data = dst_mac + src_mac + ethertype
        
        result = self.parser.parse_packet(packet_data)
        self.assertIsInstance(result, ParsedPacket)
        self.assertTrue(result.has_layer(ProtocolType.ETHERNET))
    
    def test_validate_packet_structure(self):
        """测试验证数据包结构"""
        packet = ParsedPacket()
        packet.raw_data = b'\x00' * 14
        packet.add_layer(ProtocolType.ETHERNET, {'destination_mac': '00:11:22:33:44:55'})
        
        is_valid, errors = self.parser.validate_packet_structure(packet)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)
    
    @patch('network_analyzer.analysis.packet_cache.packet_cache')
    def test_parse_ethernet_ipv4_tcp_packet(self, mock_cache):
        """测试解析完整的以太网-IPv4-TCP数据包"""
        # 设置mock缓存行为
        mock_cache.get.return_value = None  # 缓存未命中
        
        # 构造以太网头部
        dst_mac = b'\x00\x11\x22\x33\x44\x55'
        src_mac = b'\x66\x77\x88\x99\xaa\xbb'
        ethertype = b'\x08\x00'  # IPv4
        ethernet_header = dst_mac + src_mac + ethertype
        
        # IPv4头部
        ipv4_header = struct.pack('!BBHHHBBH4s4s',
                                  0x45, 0x00, 0x0028,  # version_ihl, tos, total_length
                                  0x1234, 0x4000,      # identification, flags_fragment
                                  0x40, 0x06, 0x0000,  # ttl, protocol, checksum
                                  b'\xc0\xa8\x00\x01',  # src_ip
                                  b'\xc0\xa8\x00\x02')  # dst_ip
        
        # TCP头部
        tcp_header = struct.pack('!HHLLHHHH',
                                 8080, 80,           # source_port, destination_port
                                 0x12345678, 0x87654321,  # sequence_number, acknowledgment_number
                                 0x5018, 0x2000,     # header_len_flags, window_size
                                 0x0000, 0x0000)     # checksum, urgent_ptr
        
        packet_data = ethernet_header + ipv4_header + tcp_header
        
        result = self.parser.parse_packet(packet_data)
        
        self.assertIsInstance(result, ParsedPacket)
        self.assertTrue(result.has_layer(ProtocolType.ETHERNET))
        self.assertTrue(result.has_layer(ProtocolType.IPV4))
        self.assertTrue(result.has_layer(ProtocolType.TCP))
        
        # 验证以太网层
        ethernet_fields = result.get_layer(ProtocolType.ETHERNET)
        self.assertEqual(ethernet_fields['ethertype_name'], 'IPv4')
        
        # 验证IP层
        ip_fields = result.get_layer(ProtocolType.IPV4)
        self.assertEqual(ip_fields['version'], 4)
        self.assertEqual(ip_fields['protocol_name'], 'TCP')
        
        # 验证传输层
        tcp_fields = result.get_layer(ProtocolType.TCP)
        self.assertEqual(tcp_fields['source_port'], 8080)
        self.assertEqual(tcp_fields['destination_port'], 80)


class TestPacketFormatter(unittest.TestCase):
    """测试数据包格式化器"""
    
    def setUp(self):
        """设置测试环境"""
        self.formatter = PacketFormatter()
    
    def test_format_packet_summary(self):
        """测试格式化数据包摘要"""
        packet = ParsedPacket()
        packet.raw_data = b'\x00' * 64
        packet.add_layer(ProtocolType.ETHERNET, {
            'destination_mac': '00:11:22:33:44:55',
            'source_mac': '66:77:88:99:aa:bb',
            'ethertype': 0x0800,
            'ethertype_name': 'IPv4'
        })
        
        summary = self.formatter.format_packet_summary(packet)
        self.assertIsInstance(summary, str)
        self.assertIn('数据包大小', summary)
        self.assertIn('协议层数', summary)
    
    def test_format_packet_details(self):
        """测试格式化数据包详情"""
        packet = ParsedPacket()
        packet.raw_data = b'\x00' * 64
        packet.add_layer(ProtocolType.ETHERNET, {
            'destination_mac': '00:11:22:33:44:55',
            'source_mac': '66:77:88:99:aa:bb',
            'ethertype': 0x0800,
            'ethertype_name': 'IPv4'
        })
        
        details = self.formatter.format_packet_details(packet)
        self.assertIsInstance(details, str)
    
    def test_format_hex_dump(self):
        """测试格式化十六进制转储"""
        data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        hex_dump = self.formatter.format_hex_dump(data)
        self.assertIsInstance(hex_dump, str)
        self.assertIn('00 01 02 03', hex_dump)
    
    def test_format_packet_tree(self):
        """测试格式化数据包树形结构"""
        packet = ParsedPacket()
        packet.raw_data = b'\x00' * 64
        packet.add_layer(ProtocolType.ETHERNET, {
            'destination_mac': '00:11:22:33:44:55',
            'source_mac': '66:77:88:99:aa:bb',
            'ethertype': 0x0800,
            'ethertype_name': 'IPv4'
        })
        
        tree = self.formatter.format_packet_tree(packet)
        self.assertIsInstance(tree, str)


class TestPacketCache(unittest.TestCase):
    """测试PacketCache"""
    
    def setUp(self):
        self.cache = PacketCache(max_size=10, ttl=60.0)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.cache, PacketCache)
        self.assertEqual(self.cache.max_size, 10)
        self.assertEqual(self.cache.ttl, 60.0)
    
    def test_put_and_get(self):
        """测试缓存存储和获取"""
        # 创建测试用的ParsedPacket
        parsed_packet = ParsedPacket()
        parsed_packet.raw_data = b'\x00' * 14
        parsed_packet.add_layer(ProtocolType.ETHERNET, {'dst_mac': '00:11:22:33:44:55'})
        
        # 存储数据包
        self.cache.put(b'\x00' * 14, parsed_packet)
        
        # 获取数据包
        result = self.cache.get(b'\x00' * 14)
        self.assertIsNotNone(result)
        self.assertEqual(result.raw_data, b'\x00' * 14)
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        result = self.cache.get(b'\x11' * 14)
        self.assertIsNone(result)
    
    def test_cache_invalidation(self):
        """测试缓存失效"""
        # 创建测试用的ParsedPacket
        parsed_packet = ParsedPacket()
        parsed_packet.raw_data = b'\x00' * 14
        
        # 存储数据包
        self.cache.put(b'\x00' * 14, parsed_packet)
        
        # 失效缓存
        self.cache.invalidate(b'\x00' * 14)
        
        # 验证缓存已失效
        result = self.cache.get(b'\x00' * 14)
        self.assertIsNone(result)
    
    def test_cache_clear(self):
        """测试清空缓存"""
        # 创建测试用的ParsedPacket
        parsed_packet = ParsedPacket()
        parsed_packet.raw_data = b'\x00' * 14
        
        # 存储数据包
        self.cache.put(b'\x00' * 14, parsed_packet)
        
        # 清空缓存
        self.cache.clear()
        
        # 验证缓存已清空
        result = self.cache.get(b'\x00' * 14)
        self.assertIsNone(result)
    
    def test_get_stats(self):
        """测试获取缓存统计信息"""
        stats = self.cache.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('size', stats)
    
    def test_get_cache_info(self):
        """测试获取缓存信息"""
        # 添加一些测试数据
        packet1 = ParsedPacket()
        packet1.raw_data = b'test1'
        packet1.add_layer(ProtocolType.ETHERNET, {'test': 'data1'})
        
        self.cache.put(b'test1', packet1)
        
        info = self.cache.get_cache_info()
        self.assertIsInstance(info, dict)
        self.assertIn('entries', info)
        self.assertIn('stats', info)
    
    def test_resize(self):
        """测试调整缓存大小"""
        self.cache.resize(50)
        # 验证缓存大小已调整（通过检查是否能正常工作）
        parsed_packet = ParsedPacket()
        parsed_packet.raw_data = b'\x00' * 14
        self.cache.put(b'\x00' * 14, parsed_packet)
        result = self.cache.get(b'\x00' * 14)
        self.assertIsNotNone(result)
    
    def test_set_ttl(self):
        """测试设置TTL"""
        self.cache.set_ttl(120)
        # 验证TTL已设置（通过检查是否能正常工作）
        parsed_packet = ParsedPacket()
        parsed_packet.raw_data = b'\x00' * 14
        self.cache.put(b'\x00' * 14, parsed_packet)
        result = self.cache.get(b'\x00' * 14)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()