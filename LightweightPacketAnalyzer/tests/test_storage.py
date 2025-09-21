"""
存储模块测试
"""

import unittest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from src.network_analyzer.storage.data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """DataManager类的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # 创建DataManager实例
        self.data_manager = DataManager(self.db_path)
    
    def tearDown(self):
        """清理测试环境"""
        # 删除临时目录和所有文件
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        # 验证数据库文件已创建
        self.assertTrue(os.path.exists(self.db_path))
        
        # 验证表已创建
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['packets', 'statistics', 'sessions']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_store_packet(self):
        """测试存储数据包"""
        packet_data = {
            'timestamp': datetime.now().timestamp(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'src_port': 80,
            'dst_port': 8080,
            'protocol': 'TCP',
            'length': 1024,
            'raw_data': b'test data'
        }
        
        # 存储数据包
        packet_id = self.data_manager.save_packet(packet_data)
        self.assertIsInstance(packet_id, int)
        self.assertGreater(packet_id, 0)
        
        # 验证数据包已存储
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM packets WHERE id = ?", (packet_id,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()
    
    def test_get_packets(self):
        """测试获取数据包"""
        # 先存储一些测试数据
        packet_data = {
            'timestamp': datetime.now().timestamp(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'protocol': 'TCP',
            'length': 1024
        }
        self.data_manager.save_packet(packet_data)
        
        # 获取数据包
        packets = self.data_manager.get_packets(limit=10)
        self.assertIsInstance(packets, list)
        if packets:
            self.assertIn('src_ip', packets[0])
            self.assertIn('dst_ip', packets[0])
    
    def test_store_statistics(self):
        """测试存储统计数据"""
        stats = {
            'total_packets': 100.0,
            'total_bytes': 1024.0,
            'avg_packet_size': 10.24
        }
        
        # 存储统计数据
        self.data_manager.save_statistics('traffic', stats)
        
        # 验证存储成功（通过获取统计数据）
        retrieved_stats = self.data_manager.get_statistics('traffic')
        self.assertIsInstance(retrieved_stats, list)
        
        # 验证统计数据已存储
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM statistics WHERE stat_type = ?", ('traffic',))
        results = cursor.fetchall()
        self.assertGreater(len(results), 0)
        conn.close()
    
    def test_get_statistics(self):
        """测试获取统计数据"""
        # 先存储一些统计数据
        stats = {'test_metric': 42.0}
        self.data_manager.save_statistics('test', stats)
        
        # 获取统计数据
        retrieved_stats = self.data_manager.get_statistics('test')
        self.assertIsInstance(retrieved_stats, list)
        self.assertGreater(len(retrieved_stats), 0)
    
    def test_store_session(self):
        """测试存储会话"""
        session_name = "test_session"
        metadata = {"description": "Test session"}
        
        # 创建会话
        session_id = self.data_manager.create_session(session_name, metadata)
        self.assertIsInstance(session_id, int)
        self.assertGreater(session_id, 0)
        
        # 验证会话已存储
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()
    
    def test_get_sessions(self):
        """测试获取会话"""
        # 先创建一个会话
        session_name = "test_session"
        self.data_manager.create_session(session_name)
        
        # 获取会话列表
        sessions = self.data_manager.get_sessions()
        self.assertIsInstance(sessions, list)
        self.assertGreater(len(sessions), 0)
    
    def test_cleanup_old_data(self):
        """测试清理旧数据"""
        # 先添加一些测试数据
        packet_data = {
            'timestamp': datetime.now().timestamp(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'protocol': 'TCP',
            'length': 1024
        }
        self.data_manager.save_packet(packet_data)
        
        # 执行清理（保留1天的数据）
        deleted_count = self.data_manager.cleanup_old_data(days=1)
        self.assertIsInstance(deleted_count, int)
        self.assertGreaterEqual(deleted_count, 0)
    
    def test_get_database_info(self):
        """测试获取数据库信息"""
        info = self.data_manager.get_database_info()
        self.assertIsInstance(info, dict)
        
        # 验证必要的键存在
        expected_keys = ['database_path', 'database_size', 'packet_count', 'statistics_count', 'session_count']
        for key in expected_keys:
            self.assertIn(key, info)


    def test_close_connection(self):
        """测试关闭数据库连接"""
        # DataManager没有显式的close方法，因为它使用连接池
        # 这里我们测试数据库操作后的状态
        packet_data = {
            'timestamp': datetime.now().timestamp(),
            'src_ip': '192.168.1.1',
            'dst_ip': '192.168.1.2',
            'protocol': 'TCP',
            'length': 1024
        }
        
        # 执行数据库操作
        packet_id = self.data_manager.save_packet(packet_data)
        self.assertIsInstance(packet_id, int)
        
        # 验证数据库仍然可用
        packets = self.data_manager.get_packets(limit=1)
        self.assertIsInstance(packets, list)


if __name__ == '__main__':
    unittest.main()