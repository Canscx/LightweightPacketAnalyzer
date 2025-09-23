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
    
    def packet_handler(self, packet_info):
        """数据包处理回调"""
        pass
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.capture.settings)
        self.assertFalse(self.capture.is_capturing)
        self.assertIsNone(self.capture._capture_thread)
        self.assertIsNone(self.capture._packet_callback)
    
    @patch('src.network_analyzer.capture.packet_capture.get_if_list')
    def test_get_available_interfaces(self, mock_get_if_list):
        """测试获取可用网络接口"""
        # 模拟Windows系统的接口列表
        mock_interfaces = [
            '\\Device\\NPF_Loopback',
            '\\Device\\NPF_{12345678-1234-1234-1234-123456789ABC}',
            '\\Device\\NPF_{87654321-4321-4321-4321-210987654321}'
        ]
        mock_get_if_list.return_value = mock_interfaces
        
        interfaces = self.capture.get_available_interfaces()
        
        # 验证返回的接口数量和内容
        self.assertEqual(len(interfaces), 3)
        self.assertIsInstance(interfaces, list)
        self.assertIn('\\Device\\NPF_Loopback', interfaces)
        mock_get_if_list.assert_called_once()
    
    @patch('src.network_analyzer.capture.packet_capture.get_if_list')
    def test_get_available_interfaces_exception(self, mock_get_if_list):
        """测试获取网络接口时发生异常"""
        # 模拟get_if_list抛出异常
        mock_get_if_list.side_effect = Exception("Interface error")
        
        interfaces = self.capture.get_available_interfaces()
        
        # 发生异常时应该返回空列表
        self.assertEqual(len(interfaces), 0)
        self.assertIsInstance(interfaces, list)
        mock_get_if_list.assert_called_once()
    
    def test_set_callback(self):
        """测试设置回调函数"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_packet_callback(test_callback)
        self.assertEqual(self.capture._packet_callback, test_callback)
    
    def test_set_callback_none(self):
        """测试设置None回调"""
        self.capture.set_packet_callback(None)
        self.assertIsNone(self.capture._packet_callback)
    
    def test_set_callback_invalid(self):
        """测试设置无效回调函数"""
        # 设置非函数对象作为回调
        invalid_callback = "not a function"
        
        # PacketCapture不会在设置时检查回调函数类型，而是在调用时才会出错
        # 所以这里不会抛出异常
        self.capture.set_packet_callback(invalid_callback)
        self.assertEqual(self.capture._packet_callback, invalid_callback)
    
    @patch('scapy.all.sniff')
    def test_start_capture_success(self, mock_sniff):
        """测试成功启动捕获"""
        def test_callback(packet_info):
            self.callback_results.append(packet_info)
        
        self.capture.set_packet_callback(test_callback)
        
        # 模拟sniff函数
        mock_sniff.return_value = None
        
        result = self.capture.start_capture(interface='eth0')
        
        self.assertTrue(result)
        self.assertTrue(self.capture.is_capturing)
        self.assertIsNotNone(self.capture._capture_thread)
        
        # 停止捕获
        self.capture.stop_capture()
    
    def test_start_capture_no_callback(self):
        """测试没有设置回调函数时启动捕获"""
        # PacketCapture允许没有回调函数的情况下启动捕获
        result = self.capture.start_capture()
        
        self.assertTrue(result)  # 应该能成功启动
        self.assertTrue(self.capture.is_capturing)
        
        # 停止捕获
        self.capture.stop_capture()
    
    def test_start_capture_already_capturing(self):
        """测试已经在捕获时再次启动"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_packet_callback(test_callback)
        self.capture._is_capturing = True  # 模拟已在捕获状态
        
        result = self.capture.start_capture()
        
        self.assertFalse(result)
    
    def test_stop_capture_not_capturing(self):
        """测试未在捕获时停止捕获"""
        result = self.capture.stop_capture()
        
        self.assertFalse(result)  # 应该返回False，表示未在捕获状态
        self.assertFalse(self.capture.is_capturing)
    
    @patch('scapy.all.sniff')
    def test_stop_capture_success(self, mock_sniff):
        """测试成功停止捕获"""
        def test_callback(packet_info):
            pass
        
        self.capture.set_packet_callback(test_callback)
        
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
        mock_packet.__len__ = Mock(return_value=64)
        mock_packet.summary = Mock(return_value="IP / TCP 192.168.1.1:80 > 192.168.1.2:8080")
        mock_packet.haslayer = Mock(side_effect=lambda layer: layer in ['IP', 'TCP'])
        
        # 模拟IP层
        mock_ip_layer = Mock()
        mock_ip_layer.src = "192.168.1.1"
        mock_ip_layer.dst = "192.168.1.2"
        mock_ip_layer.proto = 6  # TCP协议
        
        # 模拟TCP层
        mock_tcp_layer = Mock()
        mock_tcp_layer.sport = 80
        mock_tcp_layer.dport = 8080
        
        # 配置packet的索引访问
        def mock_getitem(key):
            if key == 'IP':
                return mock_ip_layer
            elif key == 'TCP':
                return mock_tcp_layer
            else:
                raise KeyError(f"Layer {key} not found")
        
        mock_packet.__getitem__ = Mock(side_effect=mock_getitem)
        
        # 提取数据包信息
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        # 验证提取的信息
        self.assertEqual(packet_info['length'], 64)
        self.assertEqual(packet_info['protocol'], 'TCP')
        self.assertEqual(packet_info['src_ip'], '192.168.1.1')
        self.assertEqual(packet_info['dst_ip'], '192.168.1.2')
        self.assertEqual(packet_info['src_port'], 80)
        self.assertEqual(packet_info['dst_port'], 8080)
    
    def test_extract_packet_info_non_ip(self):
        """测试提取非IP数据包信息"""
        # 创建模拟的非IP数据包
        mock_packet = Mock()
        mock_packet.__len__ = Mock(return_value=32)
        mock_packet.summary.return_value = "Ethernet frame"
        
        # 配置haslayer方法 - 不包含IP层
        def mock_haslayer(layer):
            return False  # 没有任何协议层
        mock_packet.haslayer = mock_haslayer
        
        # 配置packet的索引访问
        def mock_getitem(key):
            raise KeyError(key)  # 没有任何层
        mock_packet.__getitem__ = mock_getitem
        
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        self.assertIsInstance(packet_info, dict)
        self.assertEqual(packet_info['protocol'], 'Unknown')
        self.assertIsNone(packet_info['src_ip'])
        self.assertIsNone(packet_info['dst_ip'])
        self.assertIsNone(packet_info['src_port'])
        self.assertIsNone(packet_info['dst_port'])
        self.assertEqual(packet_info['length'], 32)
    
    def test_extract_packet_info_exception(self):
        """测试数据包信息提取异常处理"""
        # 创建会在try块内抛出异常的模拟数据包
        mock_packet = Mock()
        mock_packet.__len__ = Mock(return_value=64)
        mock_packet.summary = Mock(return_value="Test packet summary")
        mock_packet.haslayer = Mock(return_value=True)  # 让它认为有IP层
        # 在访问IP层时抛出异常
        mock_packet.__getitem__ = Mock(side_effect=Exception("Layer access error"))
        
        # 提取数据包信息（应该处理异常）
        packet_info = self.capture._extract_packet_info(mock_packet)
        
        # 验证异常被正确处理，返回基本信息
        self.assertIsInstance(packet_info, dict)
        self.assertEqual(packet_info['length'], 64)
        self.assertEqual(packet_info['summary'], 'Test packet summary')
        self.assertEqual(packet_info['protocol'], 'Unknown')  # 由于异常，保持默认值
        self.assertIsNone(packet_info['src_ip'])
        self.assertIsNone(packet_info['dst_ip'])
    
    @patch('src.network_analyzer.capture.packet_capture.sniff')
    def test_capture_with_timeout(self, mock_sniff):
        """测试带超时的捕获"""
        # 设置Mock sniff函数，让它保持运行直到stop_event被设置
        def mock_sniff_func(**kwargs):
            stop_filter = kwargs.get('stop_filter')
            if stop_filter:
                # 模拟sniff函数检查stop_filter
                while not stop_filter(None):
                    time.sleep(0.01)
        
        mock_sniff.side_effect = mock_sniff_func
        
        # 设置回调函数
        self.capture.set_packet_callback(self.packet_handler)
        
        # 启动捕获
        result = self.capture.start_capture(
            interface="eth0",
            timeout=5.0
        )
        
        self.assertTrue(result)
        
        # 等待线程启动并调用sniff
        time.sleep(0.2)
        self.assertTrue(self.capture.is_capturing)
        
        # 验证sniff被调用，并检查超时参数
        mock_sniff.assert_called_once()
        call_args = mock_sniff.call_args
        self.assertEqual(call_args[1]['timeout'], 5.0)
        self.assertEqual(call_args[1]['iface'], "eth0")
        
        # 停止捕获
        self.capture.stop_capture()
        time.sleep(0.1)  # 等待线程结束
        self.assertFalse(self.capture.is_capturing)
    
    @patch('src.network_analyzer.capture.packet_capture.sniff')
    def test_capture_with_filter(self, mock_sniff):
        """测试带过滤器的捕获"""
        # 设置Mock sniff函数，让它保持运行直到stop_event被设置
        def mock_sniff_func(**kwargs):
            stop_filter = kwargs.get('stop_filter')
            if stop_filter:
                # 模拟sniff函数检查stop_filter
                while not stop_filter(None):
                    time.sleep(0.01)
        
        mock_sniff.side_effect = mock_sniff_func
        
        # 设置回调函数
        self.capture.set_packet_callback(self.packet_handler)
        
        # 启动捕获
        result = self.capture.start_capture(
            interface="eth0",
            filter_expression="tcp port 80"
        )
        
        self.assertTrue(result)
        
        # 等待线程启动并调用sniff
        time.sleep(0.2)
        self.assertTrue(self.capture.is_capturing)
        
        # 验证sniff被调用，并检查过滤器参数
        mock_sniff.assert_called_once()
        call_args = mock_sniff.call_args
        self.assertEqual(call_args[1]['filter'], "tcp port 80")
        self.assertEqual(call_args[1]['iface'], "eth0")
        
        # 停止捕获
        self.capture.stop_capture()
        time.sleep(0.1)  # 等待线程结束
        self.assertFalse(self.capture.is_capturing)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def test_callback(packet_info):
            self.callback_results.append(packet_info)
        
        self.capture.set_packet_callback(test_callback)
        
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
    
    @patch('src.network_analyzer.capture.packet_capture.sniff')
    @patch('src.network_analyzer.capture.packet_capture.get_if_list')
    def test_full_capture_workflow(self, mock_get_if_list, mock_sniff):
        """测试完整的捕获工作流程"""
        # 设置Mock sniff函数，让它保持运行直到stop_event被设置
        def mock_sniff_func(**kwargs):
            stop_filter = kwargs.get('stop_filter')
            if stop_filter:
                # 模拟sniff函数检查stop_filter
                while not stop_filter(None):
                    time.sleep(0.01)
        
        mock_sniff.side_effect = mock_sniff_func
        
        # 模拟Windows系统的接口列表
        mock_interfaces = [
            '\\Device\\NPF_Loopback',
            '\\Device\\NPF_{12345678-1234-1234-1234-123456789ABC}'
        ]
        mock_get_if_list.return_value = mock_interfaces
        
        # 获取接口列表
        interfaces = self.capture.get_available_interfaces()
        self.assertGreater(len(interfaces), 0)
        
        # 设置回调函数
        self.capture.set_packet_callback(self.packet_handler)
        
        # 启动捕获
        result = self.capture.start_capture(
            interface=interfaces[0],  # 使用第一个可用接口
            filter_expression="tcp"
        )
        
        self.assertTrue(result)
        
        # 等待线程启动并调用sniff
        time.sleep(0.2)
        self.assertTrue(self.capture.is_capturing)
        
        # 验证sniff被调用
        mock_sniff.assert_called_once()
        
        # 停止捕获
        stop_result = self.capture.stop_capture()
        self.assertTrue(stop_result)
        time.sleep(0.1)  # 等待线程结束
        self.assertFalse(self.capture.is_capturing)


if __name__ == '__main__':
    unittest.main()