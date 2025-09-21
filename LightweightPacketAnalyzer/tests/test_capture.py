"""
数据包捕获模块单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
from datetime import datetime

from src.network_analyzer.capture.packet_capture import PacketCapture
from src.network_analyzer.config.settings import Settings


class TestPacketCapture(unittest.TestCase):
    """PacketCapture类的单元测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.settings = Settings()
        self.capture = PacketCapture(self.settings)
        self.callback_results = []
        
    def tearDown(self):
        """测试后的清理"""
        if self.capture.is_capturing:
            self.capture.stop_capture()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.capture.settings)
        self.assertFalse(self.capture.is_capturing)
        self.assertIsNone(self.capture.capture_thread)
        self.assertIsNone(self.capture.callback)
    
    @patch('scapy.all.get_if_list')
    def test_get_available_interfaces(self, mock_get_if_list):
        """测试获取可用网络接口"""
        # 模拟接口列表
        mock_interfaces = ['eth0', 'lo', 'wlan0']
        mock_get_if_list.return_value = mock_interfaces
        
        interfaces = self.capture.get_available_interfaces()
        
        self.assertEqual(interfaces, mock_interfaces)
        mock_get_if_list.assert_called_once()
    
    @patch('scapy.all.get_if_list')
    def test_get_available_interfaces_exception(self, mock_get_if_list):
        """测试获取接口时的异常处理"""
        mock_get_if_list.side_effect = Exception("Network error")
        
        interfaces = self.capture.get_available_interfaces()
        
        self.assertEqual(interfaces, [])
    
    def test_set_callback(self):
        """测试设置回调函数"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_callback(test_callback)
        self.assertEqual(self.capture.callback, test_callback)
    
    def test_set_callback_none(self):
        """测试设置空回调函数"""
        self.capture.set_callback(None)
        self.assertIsNone(self.capture.callback)
    
    def test_set_callback_invalid(self):
        """测试设置无效回调函数"""
        with self.assertRaises(ValueError):
            self.capture.set_callback("not_a_function")
    
    @patch('scapy.all.sniff')
    def test_start_capture_success(self, mock_sniff):
        """测试成功启动捕获"""
        def test_callback(packet_info):
            self.callback_results.append(packet_info)
        
        self.capture.set_callback(test_callback)
        
        # 模拟sniff函数
        mock_sniff.return_value = None
        
        result = self.capture.start_capture(interface='eth0')
        
        self.assertTrue(result)
        self.assertTrue(self.capture.is_capturing)
        self.assertIsNotNone(self.capture.capture_thread)
        
        # 停止捕获
        self.capture.stop_capture()
    
    def test_start_capture_no_callback(self):
        """测试没有设置回调函数时启动捕获"""
        result = self.capture.start_capture()
        
        self.assertFalse(result)
        self.assertFalse(self.capture.is_capturing)
    
    def test_start_capture_already_capturing(self):
        """测试已经在捕获时再次启动"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_callback(test_callback)
        self.capture.is_capturing = True  # 模拟已在捕获状态
        
        result = self.capture.start_capture()
        
        self.assertFalse(result)
    
    def test_stop_capture_not_capturing(self):
        """测试未在捕获时停止捕获"""
        result = self.capture.stop_capture()
        
        self.assertTrue(result)  # 应该返回True，表示成功停止（即使没有在捕获）
        self.assertFalse(self.capture.is_capturing)
    
    @patch('scapy.all.sniff')
    def test_stop_capture_success(self, mock_sniff):
        """测试成功停止捕获"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_callback(test_callback)
        
        # 启动捕获
        self.capture.start_capture()
        
        # 等待线程启动
        time.sleep(0.1)
        
        # 停止捕获
        result = self.capture.stop_capture()
        
        self.assertTrue(result)
        self.assertFalse(self.capture.is_capturing)
    
    def test_extract_packet_info_ip(self):
        """测试提取IP数据包信息"""
        # 创建模拟的IP数据包
        mock_packet = Mock()
        mock_packet.time = time.time()
        mock_packet.len = 64
        mock_packet.summary.return_value = "IP 192.168.1.1 > 192.168.1.2"
        
        # 模拟IP层
        mock_ip = Mock()
        mock_ip.src = "192.168.1.1"
        mock_ip.dst = "192.168.1.2"
        mock_ip.proto = 6  # TCP
        mock_packet.__getitem__.return_value = mock_ip
        mock_packet.haslayer.return_value = True
        
        # 模拟TCP层
        mock_tcp = Mock()
        mock_tcp.sport = 80
        mock_tcp.dport = 8080
        
        def mock_getitem(layer):
            if layer == 'IP':
                return mock_ip
            elif layer == 'TCP':
                return mock_tcp
            return None
        
        mock_packet.__getitem__.side_effect = mock_getitem
        
        def mock_haslayer(layer):
            return layer in ['IP', 'TCP']
        
        mock_packet.haslayer.side_effect = mock_haslayer
        
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        self.assertIsInstance(packet_info, dict)
        self.assertEqual(packet_info['src_ip'], "192.168.1.1")
        self.assertEqual(packet_info['dst_ip'], "192.168.1.2")
        self.assertEqual(packet_info['protocol'], "TCP")
        self.assertEqual(packet_info['src_port'], 80)
        self.assertEqual(packet_info['dst_port'], 8080)
        self.assertEqual(packet_info['length'], 64)
    
    def test_extract_packet_info_non_ip(self):
        """测试提取非IP数据包信息"""
        mock_packet = Mock()
        mock_packet.time = time.time()
        mock_packet.len = 32
        mock_packet.summary.return_value = "ARP who-has 192.168.1.1"
        mock_packet.haslayer.return_value = False
        
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        self.assertIsInstance(packet_info, dict)
        self.assertEqual(packet_info['src_ip'], '')
        self.assertEqual(packet_info['dst_ip'], '')
        self.assertEqual(packet_info['protocol'], 'Other')
        self.assertEqual(packet_info['src_port'], 0)
        self.assertEqual(packet_info['dst_port'], 0)
        self.assertEqual(packet_info['length'], 32)
    
    def test_extract_packet_info_exception(self):
        """测试提取数据包信息时的异常处理"""
        mock_packet = Mock()
        mock_packet.time = time.time()
        mock_packet.len = 64
        mock_packet.summary.side_effect = Exception("Packet error")
        
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        self.assertIsInstance(packet_info, dict)
        self.assertEqual(packet_info['summary'], 'Unknown packet')
    
    def test_get_protocol_name(self):
        """测试协议名称获取"""
        self.assertEqual(self.capture._get_protocol_name(1), "ICMP")
        self.assertEqual(self.capture._get_protocol_name(6), "TCP")
        self.assertEqual(self.capture._get_protocol_name(17), "UDP")
        self.assertEqual(self.capture._get_protocol_name(999), "Unknown")
    
    @patch('scapy.all.sniff')
    def test_capture_with_filter(self, mock_sniff):
        """测试带过滤器的捕获"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_callback(test_callback)
        
        # 启动带过滤器的捕获
        self.capture.start_capture(interface='eth0', packet_filter='tcp port 80')
        
        # 验证sniff被正确调用
        mock_sniff.assert_called()
        call_args = mock_sniff.call_args
        self.assertEqual(call_args[1]['filter'], 'tcp port 80')
        
        self.capture.stop_capture()
    
    @patch('scapy.all.sniff')
    def test_capture_with_count(self, mock_sniff):
        """测试限制数据包数量的捕获"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_callback(test_callback)
        
        # 启动限制数量的捕获
        self.capture.start_capture(interface='eth0', count=100)
        
        # 验证sniff被正确调用
        mock_sniff.assert_called()
        call_args = mock_sniff.call_args
        self.assertEqual(call_args[1]['count'], 100)
        
        self.capture.stop_capture()
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def test_callback(packet_info):
            self.callback_results.append(packet_info)
        
        self.capture.set_callback(test_callback)
        
        # 测试多次快速启动和停止
        for _ in range(5):
            with patch('scapy.all.sniff'):
                self.capture.start_capture()
                time.sleep(0.01)
                self.capture.stop_capture()
                time.sleep(0.01)
        
        # 确保最终状态正确
        self.assertFalse(self.capture.is_capturing)


class TestPacketCaptureIntegration(unittest.TestCase):
    """PacketCapture集成测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.settings = Settings()
        self.capture = PacketCapture(self.settings)
        self.received_packets = []
    
    def tearDown(self):
        """测试后的清理"""
        if self.capture.is_capturing:
            self.capture.stop_capture()
    
    def packet_handler(self, packet_info):
        """数据包处理回调"""
        self.received_packets.append(packet_info)
    
    @patch('scapy.all.sniff')
    @patch('scapy.all.get_if_list')
    def test_full_capture_workflow(self, mock_get_if_list, mock_sniff):
        """测试完整的捕获工作流程"""
        # 模拟接口列表
        mock_get_if_list.return_value = ['eth0', 'lo']
        
        # 设置回调
        self.capture.set_callback(self.packet_handler)
        
        # 获取接口
        interfaces = self.capture.get_available_interfaces()
        self.assertIn('eth0', interfaces)
        
        # 启动捕获
        result = self.capture.start_capture(interface='eth0')
        self.assertTrue(result)
        
        # 模拟接收数据包
        mock_packet = Mock()
        mock_packet.time = time.time()
        mock_packet.len = 64
        mock_packet.summary.return_value = "Test packet"
        mock_packet.haslayer.return_value = False
        
        # 直接调用数据包处理函数
        self.capture._process_packet(mock_packet)
        
        # 验证数据包被处理
        self.assertEqual(len(self.received_packets), 1)
        
        # 停止捕获
        result = self.capture.stop_capture()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()