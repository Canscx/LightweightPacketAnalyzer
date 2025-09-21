"""
配置模块测试
"""

import unittest
import tempfile
import os
from pathlib import Path

from network_analyzer.config.settings import Settings


class TestSettings(unittest.TestCase):
    """Settings类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_env_file = os.path.join(self.temp_dir, '.env')
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_env_file):
            os.remove(self.test_env_file)
        os.rmdir(self.temp_dir)
    
    def test_default_settings(self):
        """测试默认设置"""
        settings = Settings()
        
        # 测试基本设置
        self.assertEqual(settings.APP_NAME, "网络流量统计")
        self.assertEqual(settings.VERSION, "0.1.0")
        
        # 测试窗口设置
        self.assertEqual(settings.WINDOW_WIDTH, 1200)
        self.assertEqual(settings.WINDOW_HEIGHT, 800)
        
        # 测试数据包捕获设置
        self.assertEqual(settings.CAPTURE_INTERFACE, "auto")
        self.assertEqual(settings.CAPTURE_TIMEOUT, 1)
        self.assertEqual(settings.MAX_PACKET_COUNT, 10000)
        
        # 测试数据存储设置
        self.assertEqual(settings.DATABASE_PATH, "data/network_analyzer.db")
        self.assertEqual(settings.DATA_RETENTION_DAYS, 30)
        
    def test_env_file_loading(self):
        """测试环境文件加载"""
        # 创建临时环境文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("APP_NAME=Test App\n")
            f.write("DEBUG=true\n")
            temp_env_file = f.name
        
        try:
            # 修改环境变量
            os.environ["APP_NAME"] = "Test App"
            os.environ["DEBUG"] = "true"
            
            settings = Settings()
            self.assertEqual(settings.APP_NAME, "Test App")
            self.assertTrue(settings.DEBUG)
        finally:
            # 清理
            os.unlink(temp_env_file)
            os.environ.pop("APP_NAME", None)
            os.environ.pop("DEBUG", None)
    
    def test_get_database_path(self):
        """测试获取数据库路径"""
        settings = Settings()
        db_path = settings.get_database_path()
        
        # 验证返回的是Path对象且为绝对路径
        self.assertIsInstance(db_path, Path)
        self.assertTrue(db_path.is_absolute())
        
    def test_get_log_path(self):
        """测试获取日志路径"""
        settings = Settings()
        log_path = settings.get_log_path()
        
        # 验证返回的是Path对象且为绝对路径
        self.assertIsInstance(log_path, Path)
        self.assertTrue(log_path.is_absolute())
    
    def test_validate_settings(self):
        """测试设置验证"""
        settings = Settings()
        
        # 测试有效设置
        self.assertTrue(settings.validate_settings())
        
        # 测试无效设置
        settings.WINDOW_WIDTH = -100
        self.assertFalse(settings.validate_settings())
        
        settings.WINDOW_WIDTH = 1200
        settings.MAX_PACKET_COUNT = 0
        self.assertFalse(settings.validate_settings())
    
    def test_to_dict(self):
        """测试转换为字典"""
        settings = Settings()
        config_dict = settings.to_dict()
        
        # 验证字典包含必要的键
        expected_keys = [
            'VERSION', 'APP_NAME', 'DESCRIPTION',
            'CAPTURE_INTERFACE', 'CAPTURE_FILTER', 'CAPTURE_TIMEOUT', 'MAX_PACKET_COUNT',
            'DATABASE_PATH', 'DATA_RETENTION_DAYS', 'AUTO_CLEANUP',
            'WINDOW_WIDTH', 'WINDOW_HEIGHT', 'THEME',
            'LOG_LEVEL', 'LOG_FILE', 'LOG_MAX_SIZE', 'LOG_BACKUP_COUNT',
            'BUFFER_SIZE', 'WORKER_THREADS',
            'ENABLE_PROMISCUOUS_MODE', 'REQUIRE_ADMIN',
            'DEBUG', 'TESTING'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config_dict)
        
        # 验证特定值
        self.assertEqual(config_dict['VERSION'], settings.VERSION)
        self.assertEqual(config_dict['APP_NAME'], settings.APP_NAME)
        self.assertEqual(config_dict['DEBUG'], settings.DEBUG)


if __name__ == '__main__':
    unittest.main()