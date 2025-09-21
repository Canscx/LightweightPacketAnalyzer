"""
网络流量分析器集成测试

测试各模块间的协作和完整的工作流程
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
import tempfile
import os
from datetime import datetime, timedelta

from src.network_analyzer.config.settings import Settings
from src.network_analyzer.storage.data_manager import DataManager
from src.network_analyzer.capture.packet_capture import PacketCapture
from src.network_analyzer.processing.data_processor import DataProcessor


class TestNetworkAnalyzerIntegration(unittest.TestCase):
    """网络分析器集成测试"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # 创建设置对象
        self.settings = Settings()
        self.settings.database_path = self.temp_db.name
        
        # 创建组件
        self.data_manager = DataManager(self.settings.database_path)
        self.processor = DataProcessor(self.settings, self.data_manager)
        self.capture = PacketCapture(self.settings)
        
        # 测试数据收集
        self.processed_packets = []
        self.capture_errors = []
    
    def tearDown(self):
        """测试后的清理"""
        # 停止捕获
        if self.capture.is_capturing:
            self.capture.stop_capture()
        
        # 关闭数据库连接
        if hasattr(self.data_manager, 'close'):
            self.data_manager.close()
        
        # 删除临时文件
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass
    
    def packet_callback(self, packet_info):
        """数据包处理回调"""
        try:
            # 使用处理器处理数据包
            self.processor.process_packet(packet_info)
            self.processed_packets.append(packet_info)
        except Exception as e:
            self.capture_errors.append(str(e))
    
    def test_capture_to_storage_workflow(self):
        """测试从捕获到存储的完整工作流程"""
        # 设置回调
        self.capture.set_packet_callback(self.packet_callback)
        
        # 创建模拟数据包
        mock_packets = [
            {
                'timestamp': datetime.now(),
                'src_ip': '192.168.1.1',
                'dst_ip': '192.168.1.2',
                'src_port': 80,
                'dst_port': 8080,
                'protocol': 'TCP',
                'length': 1024,
                'summary': 'TCP packet 1'
            },
            {
                'timestamp': datetime.now(),
                'src_ip': '192.168.1.2',
                'dst_ip': '192.168.1.1',
                'src_port': 8080,
                'dst_port': 80,
                'protocol': 'TCP',
                'length': 512,
                'summary': 'TCP packet 2'
            },
            {
                'timestamp': datetime.now(),
                'src_ip': '192.168.1.1',
                'dst_ip': '8.8.8.8',
                'src_port': 12345,
                'dst_port': 53,
                'protocol': 'UDP',
                'length': 64,
                'summary': 'DNS query'
            }
        ]
        
        # 模拟数据包处理
        for packet_info in mock_packets:
            self.packet_callback(packet_info)
        
        # 验证处理结果
        self.assertEqual(len(self.processed_packets), 3)
        self.assertEqual(len(self.capture_errors), 0)
        
        # 验证统计信息
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 3)
        self.assertEqual(stats['total_bytes'], 1600)  # 1024+512+64
        self.assertEqual(stats['protocol_counts']['TCP'], 2)
        self.assertEqual(stats['protocol_counts']['UDP'], 1)
        
        # 验证数据存储
        # 从数据库查询数据包
        stored_packets = self.data_manager.get_packets(limit=10)
        self.assertEqual(len(stored_packets), 3)
    
    def test_real_time_processing(self):
        """测试实时处理能力"""
        # 设置回调
        self.capture.set_packet_callback(self.packet_callback)
        
        # 直接模拟数据包处理，绕过sniff的复杂性
        for i in range(5):
            # 创建模拟的scapy数据包
            mock_packet = Mock()
            mock_packet.time = time.time()
            
            # 模拟len()函数
            mock_packet.__len__ = Mock(return_value=100 + i * 10)
            mock_packet.summary.return_value = f"Test packet {i}"
            
            # 模拟IP层
            mock_ip = Mock()
            mock_ip.src = f"192.168.1.{i+1}"
            mock_ip.dst = "192.168.1.100"
            mock_ip.proto = 6  # TCP
            
            # 模拟TCP层
            mock_tcp = Mock()
            mock_tcp.sport = 80 + i
            mock_tcp.dport = 8080
            
            # 模拟haslayer方法
            def mock_haslayer(layer):
                return layer in ['IP', 'TCP']
            
            mock_packet.haslayer = Mock(side_effect=mock_haslayer)
            
            # 模拟__getitem__方法
            def mock_getitem(layer):
                if layer == 'IP':
                    return mock_ip
                elif layer == 'TCP':
                    return mock_tcp
                raise KeyError(f"Layer {layer} not found")
            
            mock_packet.__getitem__ = Mock(side_effect=mock_getitem)
            
            # 直接调用数据包处理方法
            self.capture._process_packet(mock_packet)
            time.sleep(0.01)  # 模拟处理延迟
        
        # 等待处理完成
        time.sleep(0.1)
        
        # 验证结果
        print(f"处理的数据包数量: {len(self.processed_packets)}")
        print(f"捕获错误: {self.capture_errors}")
        
        # 验证至少处理了一些数据包
        self.assertGreater(len(self.processed_packets), 0, "应该处理了至少一个数据包")
        
        # 验证统计信息更新
        stats = self.processor.get_current_stats()
        print(f"统计信息: {stats}")
        self.assertGreater(stats['total_packets'], 0, "统计信息应该显示处理了数据包")
    
    def test_concurrent_processing(self):
        """测试并发处理能力"""
        # 创建多个线程同时处理数据包
        def process_batch(batch_id):
            for i in range(10):
                packet_info = {
                    'timestamp': datetime.now(),
                    'src_ip': f'192.168.{batch_id}.{i}',
                    'dst_ip': '192.168.1.100',
                    'src_port': 8000 + i,
                    'dst_port': 80,
                    'protocol': 'TCP',
                    'length': 100 + i,
                    'summary': f'Batch {batch_id} packet {i}'
                }
                self.processor.process_packet(packet_info)
        
        # 启动多个线程
        threads = []
        for batch_id in range(1, 4):  # 3个批次
            thread = threading.Thread(target=process_batch, args=(batch_id,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 30)  # 3 batches * 10 packets
        
        # 验证数据完整性
        stored_packets = self.data_manager.get_packets(limit=50)
        self.assertEqual(len(stored_packets), 30)
    
    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复能力"""
        # 测试数据库错误恢复
        original_save = self.data_manager.save_packet
        
        # 模拟数据库错误
        error_count = 0
        def failing_save(packet_data):
            nonlocal error_count
            error_count += 1
            if error_count <= 2:  # 前两次失败
                raise Exception("Database connection error")
            return original_save(packet_data)  # 第三次成功
        
        self.data_manager.save_packet = failing_save
        
        # 处理数据包
        packet_info = {
            'timestamp': datetime.now(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'protocol': 'TCP',
            'length': 100,
            'summary': 'Test packet'
        }
        
        # 应该能够处理错误并继续
        for i in range(5):
            try:
                self.processor.process_packet(packet_info)
            except Exception:
                pass  # 忽略预期的错误
        
        # 验证统计信息仍然更新（即使存储失败）
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 5)
        
        # 恢复原始方法
        self.data_manager.save_packet = original_save
    
    def test_performance_under_load(self):
        """测试高负载下的性能"""
        start_time = time.time()
        
        # 处理大量数据包
        packet_count = 1000
        for i in range(packet_count):
            packet_info = {
                'timestamp': datetime.now(),
                'src_ip': f'192.168.{i % 256}.{(i // 256) % 256}',
                'dst_ip': '8.8.8.8',
                'src_port': 1024 + (i % 60000),
                'dst_port': 80,
                'protocol': 'TCP' if i % 2 == 0 else 'UDP',
                'length': 64 + (i % 1400),
                'summary': f'Load test packet {i}'
            }
            self.processor.process_packet(packet_info)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证性能指标
        packets_per_second = packet_count / processing_time
        print(f"处理速度: {packets_per_second:.2f} packets/second")
        
        # 基本性能要求（应该能够处理至少50 pps）
        self.assertGreater(packets_per_second, 50)
        
        # 验证数据完整性
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], packet_count)
        
        # 验证存储完整性
        stored_packets = self.data_manager.get_packets(limit=packet_count + 10)
        self.assertEqual(len(stored_packets), packet_count)
    
    def test_data_consistency(self):
        """测试数据一致性"""
        # 处理一系列相关的数据包
        connection_packets = []
        base_time = datetime.now()
        
        # 模拟一个完整的TCP连接
        for i in range(10):
            # 请求包
            req_packet = {
                'timestamp': base_time + timedelta(milliseconds=i*100),
                'src_ip': '192.168.1.10',
                'dst_ip': '192.168.1.20',
                'src_port': 12345,
                'dst_port': 80,
                'protocol': 'TCP',
                'length': 64 + i,
                'summary': f'TCP request {i}'
            }
            
            # 响应包
            resp_packet = {
                'timestamp': base_time + timedelta(milliseconds=i*100+50),
                'src_ip': '192.168.1.20',
                'dst_ip': '192.168.1.10',
                'src_port': 80,
                'dst_port': 12345,
                'protocol': 'TCP',
                'length': 1024 + i*10,
                'summary': f'TCP response {i}'
            }
            
            connection_packets.extend([req_packet, resp_packet])
        
        # 处理所有数据包
        for packet in connection_packets:
            self.processor.process_packet(packet)
        
        # 验证连接跟踪
        connections = self.processor.get_active_connections()
        self.assertEqual(len(connections), 1)  # 应该只有一个连接
        
        connection = connections[0]
        self.assertEqual(connection['packet_count'], 20)  # 10个请求 + 10个响应
        
        # 验证统计一致性
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 20)
        
        # 验证IP统计
        self.assertEqual(stats['ip_counts']['192.168.1.10'], 20)  # 作为源和目标各10次
        self.assertEqual(stats['ip_counts']['192.168.1.20'], 20)
        
        # 验证端口统计
        self.assertEqual(stats['port_counts'][12345], 20)
        self.assertEqual(stats['port_counts'][80], 20)
    
    def test_memory_management(self):
        """测试内存管理"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 处理大量数据包
        for batch in range(10):
            for i in range(100):
                packet_info = {
                    'timestamp': datetime.now(),
                    'src_ip': f'10.0.{batch}.{i}',
                    'dst_ip': '8.8.8.8',
                    'protocol': 'TCP',
                    'length': 1024,
                    'summary': f'Memory test packet {batch}-{i}'
                }
                self.processor.process_packet(packet_info)
            
            # 每批次后检查内存使用
            current_memory = process.memory_info().rss
            memory_growth = current_memory - initial_memory
            
            # 内存增长应该在合理范围内（不超过100MB）
            self.assertLess(memory_growth, 100 * 1024 * 1024)
        
        # 重置统计信息应该释放内存
        self.processor.reset_stats()
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss
        # 重置后内存使用应该接近初始值
        memory_after_reset = final_memory - initial_memory
        self.assertLess(memory_after_reset, 50 * 1024 * 1024)


class TestModuleInteraction(unittest.TestCase):
    """模块交互测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.settings = Settings()
        
        # 使用临时文件数据库进行测试
        import tempfile
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.settings.database_path = self.temp_db.name
        
        self.data_manager = DataManager(self.settings.database_path)
        self.processor = DataProcessor(self.settings, self.data_manager)
        self.capture = PacketCapture(self.settings)
    
    def tearDown(self):
        """测试后的清理"""
        # 清理临时数据库文件
        import os
        if hasattr(self, 'temp_db'):
            self.temp_db.close()
            try:
                os.unlink(self.temp_db.name)
            except:
                pass
    
    def test_settings_propagation(self):
        """测试配置传播"""
        # 验证所有模块都使用相同的设置
        self.assertIs(self.processor.settings, self.settings)
        self.assertIs(self.capture.settings, self.settings)
        # DataManager不需要settings属性，跳过此检查
        # self.assertIs(self.data_manager.settings, self.settings)
    
    def test_data_flow_integrity(self):
        """测试数据流完整性"""
        # 确保数据库已初始化
        self.data_manager._init_database()
        
        # 创建测试数据
        test_packet = {
            'timestamp': datetime.now(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'src_port': 80,
            'dst_port': 8080,
            'protocol': 'TCP',
            'length': 1024,
            'summary': 'Test packet for data flow'
        }
        
        # 通过处理器处理
        self.processor.process_packet(test_packet)
        
        # 验证数据在各个层面的一致性
        
        # 1. 统计信息
        stats = self.processor.get_current_stats()
        self.assertEqual(stats['total_packets'], 1)
        self.assertEqual(stats['total_bytes'], 1024)
        
        # 2. 存储数据
        stored_packets = self.data_manager.get_packets(limit=1)
        self.assertEqual(len(stored_packets), 1)
        
        stored_packet = stored_packets[0]
        self.assertEqual(stored_packet['src_ip'], test_packet['src_ip'])
        self.assertEqual(stored_packet['dst_ip'], test_packet['dst_ip'])
        self.assertEqual(stored_packet['protocol'], test_packet['protocol'])
        
        # 3. 连接跟踪
        connections = self.processor.get_active_connections()
        self.assertEqual(len(connections), 1)
        
        connection = connections[0]
        self.assertEqual(connection['src_ip'], test_packet['src_ip'])
        self.assertEqual(connection['dst_ip'], test_packet['dst_ip'])


if __name__ == '__main__':
    # 运行测试时显示更多信息
    unittest.main(verbosity=2)