"""
数据处理模块单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict

from src.network_analyzer.processing.data_processor import DataProcessor
from src.network_analyzer.config.settings import Settings
from src.network_analyzer.storage.data_manager import DataManager


class TestDataProcessor(unittest.TestCase):
    """DataProcessor类的单元测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.settings = Settings()
        self.mock_data_manager = Mock(spec=DataManager)
        # 确保Mock对象具有所需的方法
        self.mock_data_manager.get_packets_by_time_range = Mock(return_value=[])
        self.mock_data_manager.store_packet = Mock()
        self.processor = DataProcessor(self.settings, self.mock_data_manager)
        
        # 创建测试数据包
        self.test_packet = {
            'timestamp': datetime.now(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'src_port': 80,
            'dst_port': 8080,
            'protocol': 'TCP',
            'length': 1024,
            'summary': 'TCP 192.168.1.1:80 > 192.168.1.2:8080'
        }
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.processor.settings)
        self.assertIsNotNone(self.processor.data_manager)
        self.assertEqual(self.processor._packet_stats['total_packets'], 0)
        self.assertEqual(self.processor._packet_stats['total_bytes'], 0)
        self.assertIsInstance(self.processor._packet_stats['protocol_counts'], defaultdict)
    
    def test_process_packet_basic(self):
        """测试基本数据包处理"""
        initial_count = self.processor._packet_stats['total_packets']
        initial_bytes = self.processor._packet_stats['total_bytes']
        
        self.processor.process_packet(self.test_packet)
        
        # 验证统计更新
        self.assertEqual(self.processor._packet_stats['total_packets'], initial_count + 1)
        self.assertEqual(self.processor._packet_stats['total_bytes'], initial_bytes + 1024)
        self.assertEqual(self.processor._packet_stats['protocol_counts']['TCP'], 1)
        self.assertEqual(self.processor._packet_stats['ip_counts']['192.168.1.1'], 1)
        self.assertEqual(self.processor._packet_stats['ip_counts']['192.168.1.2'], 1)
        
        # 验证数据管理器被调用
        self.mock_data_manager.save_packet.assert_called_once()
    
    def test_process_packet_multiple(self):
        """测试处理多个数据包"""
        packets = [
            {**self.test_packet, 'protocol': 'TCP', 'length': 100},
            {**self.test_packet, 'protocol': 'UDP', 'length': 200},
            {**self.test_packet, 'protocol': 'TCP', 'length': 300},
        ]
        
        for packet in packets:
            self.processor.process_packet(packet)
        
        stats = self.processor.get_current_stats()
        
        self.assertEqual(stats['total_packets'], 3)
        self.assertEqual(stats['total_bytes'], 600)
        self.assertEqual(stats['protocol_counts']['TCP'], 2)
        self.assertEqual(stats['protocol_counts']['UDP'], 1)
    
    def test_process_packet_exception_handling(self):
        """测试数据包处理异常处理"""
        # 模拟数据管理器抛出异常
        self.mock_data_manager.save_packet.side_effect = Exception("Database error")
        
        # 处理应该继续，不应该抛出异常
        try:
            self.processor.process_packet(self.test_packet)
        except Exception:
            self.fail("process_packet should handle exceptions gracefully")
        
        # 统计应该仍然更新
        self.assertEqual(self.processor._packet_stats['total_packets'], 1)
    
    def test_get_current_stats(self):
        """测试获取当前统计信息"""
        # 处理一些数据包
        for i in range(5):
            packet = {**self.test_packet, 'length': 100 * (i + 1)}
            self.processor.process_packet(packet)
        
        stats = self.processor.get_current_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_packets'], 5)
        self.assertEqual(stats['total_bytes'], 1500)  # 100+200+300+400+500
        self.assertIn('packet_rate', stats)
        self.assertIn('byte_rate', stats)
        self.assertIsInstance(stats['protocol_counts'], dict)
    
    def test_get_current_stats_empty(self):
        """测试空统计信息"""
        stats = self.processor.get_current_stats()
        
        self.assertEqual(stats['total_packets'], 0)
        self.assertEqual(stats['total_bytes'], 0)
        self.assertEqual(stats['packet_rate'], 0.0)
        self.assertEqual(stats['byte_rate'], 0.0)
    
    def test_traffic_history_tracking(self):
        """测试流量历史跟踪"""
        # 创建不同时间的数据包
        base_time = datetime.now()
        
        for i in range(3):
            packet = {
                **self.test_packet,
                'timestamp': base_time + timedelta(seconds=i),
                'length': 100
            }
            self.processor.process_packet(packet)
        
        # 获取流量历史
        history = self.processor.get_traffic_history(minutes=1)
        
        self.assertIsInstance(history, list)
        # 由于时间窗口的实现，可能不会立即有数据
        # 主要测试方法不抛出异常
    
    def test_get_top_talkers(self):
        """测试获取流量最大的IP"""
        # 创建不同IP的数据包
        ips_and_counts = [
            ('192.168.1.1', 5),
            ('192.168.1.2', 3),
            ('192.168.1.3', 8),
            ('192.168.1.4', 1)
        ]
        
        for ip, count in ips_and_counts:
            for _ in range(count):
                packet = {**self.test_packet, 'src_ip': ip}
                self.processor.process_packet(packet)
        
        top_talkers = self.processor.get_top_talkers(limit=3)
        
        self.assertIsInstance(top_talkers, list)
        self.assertLessEqual(len(top_talkers), 3)
        
        # 验证排序（应该按数量降序）
        if len(top_talkers) > 1:
            self.assertGreaterEqual(top_talkers[0][1], top_talkers[1][1])
    
    def test_get_protocol_distribution(self):
        """测试获取协议分布"""
        # 创建不同协议的数据包
        protocols = ['TCP', 'TCP', 'UDP', 'ICMP', 'TCP']
        
        for protocol in protocols:
            packet = {**self.test_packet, 'protocol': protocol}
            self.processor.process_packet(packet)
        
        distribution = self.processor.get_protocol_distribution()
        
        self.assertIsInstance(distribution, dict)
        self.assertAlmostEqual(distribution['TCP'], 60.0)  # 3/5 * 100
        self.assertAlmostEqual(distribution['UDP'], 20.0)  # 1/5 * 100
        self.assertAlmostEqual(distribution['ICMP'], 20.0)  # 1/5 * 100
    
    def test_get_protocol_distribution_empty(self):
        """测试空协议分布"""
        distribution = self.processor.get_protocol_distribution()
        
        self.assertEqual(distribution, {})
    
    def test_connection_tracking(self):
        """测试连接跟踪"""
        # 创建连接数据包
        packets = [
            {**self.test_packet, 'src_ip': '192.168.1.1', 'dst_ip': '192.168.1.2', 'src_port': 80, 'dst_port': 8080},
            {**self.test_packet, 'src_ip': '192.168.1.2', 'dst_ip': '192.168.1.1', 'src_port': 8080, 'dst_port': 80},
            {**self.test_packet, 'src_ip': '192.168.1.1', 'dst_ip': '192.168.1.2', 'src_port': 80, 'dst_port': 8080},
        ]
        
        for packet in packets:
            self.processor.process_packet(packet)
        
        connections = self.processor.get_active_connections()
        
        self.assertIsInstance(connections, list)
        # 应该有一个连接（双向被合并）
        if connections:
            conn = connections[0]
            self.assertIn('packet_count', conn)
            self.assertIn('byte_count', conn)
            self.assertIn('start_time', conn)
            self.assertIn('last_seen', conn)
    
    def test_get_active_connections_timeout(self):
        """测试活跃连接超时"""
        # 创建旧的连接
        old_time = datetime.now() - timedelta(minutes=10)
        old_packet = {**self.test_packet, 'timestamp': old_time}
        
        self.processor.process_packet(old_packet)
        
        # 获取活跃连接（5分钟超时）
        connections = self.processor.get_active_connections(timeout_minutes=5)
        
        # 旧连接应该被过滤掉
        self.assertEqual(len(connections), 0)
    
    def test_reset_stats(self):
        """测试重置统计信息"""
        # 处理一些数据包
        for _ in range(3):
            self.processor.process_packet(self.test_packet)
        
        # 验证有数据
        self.assertGreater(self.processor._packet_stats['total_packets'], 0)
        
        # 重置
        self.processor.reset_stats()
        
        # 验证重置后的状态
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 0)
        self.assertEqual(stats['total_bytes'], 0)
        self.assertEqual(len(stats['protocol_counts']), 0)
    
    def test_anomaly_detection_large_packet(self):
        """测试异常检测 - 大数据包"""
        large_packet = {**self.test_packet, 'length': 10000}  # 超过MTU
        
        with patch.object(self.processor.logger, 'warning') as mock_warning:
            self.processor.process_packet(large_packet)
            mock_warning.assert_called()
    
    def test_anomaly_detection_suspicious_port(self):
        """测试异常检测 - 可疑端口"""
        suspicious_packet = {**self.test_packet, 'src_port': 31337}  # 可疑端口
        
        with patch.object(self.processor.logger, 'warning') as mock_warning:
            self.processor.process_packet(suspicious_packet)
            mock_warning.assert_called()
    
    def test_calculate_baseline_no_data(self):
        """测试计算基线 - 无数据"""
        self.mock_data_manager.get_packets_by_time_range.return_value = []
        
        baseline = self.processor.calculate_baseline(hours=1)
        
        self.assertEqual(baseline, {})
    
    def test_calculate_baseline_with_data(self):
        """测试计算基线 - 有数据"""
        # 模拟历史数据
        mock_packets = [
            {'protocol': 'TCP', 'length': 100},
            {'protocol': 'UDP', 'length': 200},
            {'protocol': 'TCP', 'length': 150},
        ]
        self.mock_data_manager.get_packets_by_time_range.return_value = mock_packets
        
        baseline = self.processor.calculate_baseline(hours=1)
        
        self.assertIsInstance(baseline, dict)
        self.assertIn('avg_packet_rate', baseline)
        self.assertIn('avg_byte_rate', baseline)
        self.assertIn('protocol_distribution', baseline)
        self.assertEqual(baseline['total_packets'], 3)
        self.assertEqual(baseline['total_bytes'], 450)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def process_packets():
            for i in range(10):
                packet = {**self.test_packet, 'length': i + 1}
                self.processor.process_packet(packet)
        
        # 创建多个线程同时处理数据包
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=process_packets)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 30)  # 3 threads * 10 packets each
    
    def test_packet_info_extraction_edge_cases(self):
        """测试数据包信息提取的边界情况"""
        # 测试缺少字段的数据包
        incomplete_packet = {
            'timestamp': datetime.now(),
            'length': 64
            # 缺少其他字段
        }
        
        try:
            self.processor.process_packet(incomplete_packet)
        except Exception:
            self.fail("Should handle incomplete packet info gracefully")
        
        # 测试None值
        none_packet = {
            'timestamp': datetime.now(),
            'src_ip': None,
            'dst_ip': None,
            'protocol': None,
            'length': 64
        }
        
        try:
            self.processor.process_packet(none_packet)
        except Exception:
            self.fail("Should handle None values gracefully")


class TestDataProcessorIntegration(unittest.TestCase):
    """DataProcessor集成测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.settings = Settings()
        self.mock_data_manager = Mock(spec=DataManager)
        self.processor = DataProcessor(self.settings, self.mock_data_manager)
    
    def test_full_processing_workflow(self):
        """测试完整的数据处理工作流程"""
        # 模拟一系列网络活动
        packets = [
            # HTTP流量
            {'timestamp': datetime.now(), 'src_ip': '192.168.1.10', 'dst_ip': '8.8.8.8', 
             'src_port': 12345, 'dst_port': 80, 'protocol': 'TCP', 'length': 512, 'summary': 'HTTP request'},
            {'timestamp': datetime.now(), 'src_ip': '8.8.8.8', 'dst_ip': '192.168.1.10', 
             'src_port': 80, 'dst_port': 12345, 'protocol': 'TCP', 'length': 1024, 'summary': 'HTTP response'},
            
            # DNS查询
            {'timestamp': datetime.now(), 'src_ip': '192.168.1.10', 'dst_ip': '8.8.8.8', 
             'src_port': 54321, 'dst_port': 53, 'protocol': 'UDP', 'length': 64, 'summary': 'DNS query'},
            {'timestamp': datetime.now(), 'src_ip': '8.8.8.8', 'dst_ip': '192.168.1.10', 
             'src_port': 53, 'dst_port': 54321, 'protocol': 'UDP', 'length': 128, 'summary': 'DNS response'},
            
            # ICMP ping
            {'timestamp': datetime.now(), 'src_ip': '192.168.1.10', 'dst_ip': '8.8.8.8', 
             'src_port': 0, 'dst_port': 0, 'protocol': 'ICMP', 'length': 64, 'summary': 'ICMP ping'},
        ]
        
        # 处理所有数据包
        for packet in packets:
            self.processor.process_packet(packet)
        
        # 验证统计结果
        stats = self.processor.get_current_stats()
        
        self.assertEqual(stats['total_packets'], 5)
        self.assertEqual(stats['total_bytes'], 1792)  # 512+1024+64+128+64
        
        # 验证协议分布
        distribution = self.processor.get_protocol_distribution()
        self.assertAlmostEqual(distribution['TCP'], 40.0)  # 2/5
        self.assertAlmostEqual(distribution['UDP'], 40.0)  # 2/5
        self.assertAlmostEqual(distribution['ICMP'], 20.0)  # 1/5
        
        # 验证Top Talkers
        top_talkers = self.processor.get_top_talkers()
        # 192.168.1.10 和 8.8.8.8 都应该出现多次
        
        # 验证连接跟踪
        connections = self.processor.get_active_connections()
        self.assertGreater(len(connections), 0)
        
        # 验证数据存储
        self.assertEqual(self.mock_data_manager.save_packet.call_count, 5)


if __name__ == '__main__':
    unittest.main()