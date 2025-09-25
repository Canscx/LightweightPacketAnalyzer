"""
捕获选项功能单元测试
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from network_analyzer.gui.components.bpf_validator import BPFValidator
from network_analyzer.gui.components.filter_template_manager import FilterTemplateManager, FilterTemplate
from network_analyzer.gui.components.interface_info_provider import InterfaceInfoProvider, InterfaceInfo
from network_analyzer.gui.components.capture_options_dialog import CaptureOptions
from network_analyzer.config.settings import Settings


class TestBPFValidator(unittest.TestCase):
    """BPF验证器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = BPFValidator()
    
    def test_basic_syntax_validation(self):
        """测试基础语法验证"""
        # 有效的过滤器
        valid_filters = [
            "tcp port 80",
            "host 192.168.1.1",
            "net 192.168.0.0/24",
            "icmp",
            "arp",
            "tcp and port 443",
            "not port 22",
            "src host 10.0.0.1 and dst port 80"
        ]
        
        for filter_expr in valid_filters:
            with self.subTest(filter_expr=filter_expr):
                result = self.validator.validate_filter(filter_expr)
                self.assertIsInstance(result, dict)
                self.assertTrue(result['is_valid'], f"过滤器 '{filter_expr}' 应该有效: {result.get('error_message', '')}")
    
    def test_invalid_syntax(self):
        """测试无效语法"""
        invalid_filters = [
            "tcp port",  # 缺少端口号
            "host",      # 缺少主机地址
            "tcp port 80 and",  # 不完整的表达式
            "((tcp port 80)",    # 不匹配的括号
            "tcp port '80",      # 不匹配的引号
        ]
        
        for filter_expr in invalid_filters:
            with self.subTest(filter_expr=filter_expr):
                result = self.validator.validate_filter(filter_expr)
                self.assertIsInstance(result, dict)
                self.assertFalse(result['is_valid'], f"过滤器 '{filter_expr}' 应该无效")
                self.assertIsNotNone(result.get('error_message'))
    
    def test_empty_filter(self):
        """测试空过滤器"""
        result = self.validator.validate_filter("")
        self.assertIsInstance(result, dict)
        self.assertTrue(result['is_valid'], "空过滤器应该有效")
        
        result = self.validator.validate_filter("   ")
        self.assertIsInstance(result, dict)
        self.assertTrue(result['is_valid'], "空白过滤器应该有效")
    
    def test_parentheses_validation(self):
        """测试括号验证"""
        # 有效括号
        valid_cases = [
            "(tcp port 80)",
            "((tcp port 80) and (udp port 53))",
            "tcp port 80 and (host 192.168.1.1 or host 192.168.1.2)"
        ]
        
        for case in valid_cases:
            with self.subTest(case=case):
                result = self.validator._check_parentheses(case)
                self.assertTrue(result, f"括号应该匹配: {case}")
        
        # 无效括号
        invalid_cases = [
            "(tcp port 80",
            "tcp port 80)",
            "((tcp port 80)",
            "tcp port 80))"
        ]
        
        for case in invalid_cases:
            with self.subTest(case=case):
                result = self.validator._check_parentheses(case)
                self.assertFalse(result, f"括号不应该匹配: {case}")
    
    def test_quotes_validation(self):
        """测试引号验证"""
        # 有效引号
        valid_cases = [
            'host "example.com"',
            "host 'example.com'",
            'tcp port 80 and host "test.com"'
        ]
        
        for case in valid_cases:
            with self.subTest(case=case):
                result = self.validator._check_quotes(case)
                self.assertTrue(result, f"引号应该匹配: {case}")
        
        # 无效引号
        invalid_cases = [
            'host "example.com',
            "host 'example.com",
            'host "example.com\''
        ]
        
        for case in invalid_cases:
            with self.subTest(case=case):
                result = self.validator._check_quotes(case)
                self.assertFalse(result, f"引号不应该匹配: {case}")
    
    def test_get_suggestions(self):
        """测试获取建议"""
        # 测试生成建议功能
        result = self.validator.validate_filter("tcp")
        self.assertIsInstance(result, dict)
        self.assertIn('suggestions', result)
        suggestions = result['suggestions']
        self.assertIsInstance(suggestions, list)
    
    def test_get_common_templates(self):
        """测试获取常用模板"""
        templates = self.validator.get_common_filters()
        self.assertIsInstance(templates, dict)
        self.assertTrue(len(templates) > 0)
        
        # 检查是否包含基本模板
        self.assertIn("HTTP流量", templates)
        self.assertIn("DNS查询", templates)


class TestFilterTemplateManager(unittest.TestCase):
    """过滤器模板管理器测试"""
    
    def setUp(self):
        """测试初始化"""
        # 创建临时设置
        self.temp_dir = tempfile.mkdtemp()
        
        self.manager = FilterTemplateManager(Path(self.temp_dir))
    
    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_templates_loading(self):
        """测试默认模板加载"""
        templates = self.manager.get_all_templates()
        self.assertTrue(len(templates) > 0)
        
        # 检查是否包含基本模板
        template_names = [t.name for t in templates]
        self.assertIn("HTTP流量", template_names)
        self.assertIn("DNS查询", template_names)
        self.assertIn("SSH连接", template_names)
    
    def test_add_custom_template(self):
        """测试添加自定义模板"""
        success = self.manager.add_template(
            name="测试模板",
            filter_expression="tcp port 8080",
            description="测试用模板",
            category="自定义"
        )
        
        self.assertTrue(success)
        
        # 验证模板已添加
        retrieved = self.manager.get_template("测试模板")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.filter_expression, "tcp port 8080")
        self.assertTrue(retrieved.is_custom)
    
    def test_template_persistence(self):
        """测试模板持久化"""
        # 添加自定义模板
        success = self.manager.add_template(
            name="持久化测试",
            filter_expression="udp port 1234",
            description="测试持久化",
            category="测试"
        )
        
        self.assertTrue(success)
        
        # 创建新的管理器实例
        new_manager = FilterTemplateManager(Path(self.temp_dir))
        
        # 验证模板已持久化
        retrieved = new_manager.get_template("持久化测试")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.filter_expression, "udp port 1234")
    
    def test_template_search(self):
        """测试模板搜索"""
        # 搜索HTTP相关模板
        results = self.manager.search_templates("HTTP")
        self.assertTrue(len(results) > 0)
        
        # 验证搜索结果
        for template in results:
            self.assertTrue(
                "http" in template.name.lower() or 
                "http" in template.description.lower() or
                "80" in template.filter_expression
            )
    
    def test_usage_tracking(self):
        """测试使用次数跟踪"""
        template_name = "HTTP流量"
        
        # 获取初始使用次数
        template = self.manager.get_template(template_name)
        initial_usage = template.usage_count if template else 0
        
        # 增加使用次数
        self.manager.increment_usage(template_name)
        
        # 验证使用次数增加
        updated_template = self.manager.get_template(template_name)
        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.usage_count, initial_usage + 1)


class TestInterfaceInfoProvider(unittest.TestCase):
    """网络接口信息提供器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.provider = InterfaceInfoProvider()
    
    @patch('network_analyzer.gui.components.interface_info_provider.get_if_list')
    def test_get_all_interfaces(self, mock_get_if_list):
        """测试获取所有接口"""
        # 模拟接口列表
        mock_get_if_list.return_value = ['eth0', 'lo', 'wlan0']
        
        interfaces = self.provider.get_all_interfaces()
        self.assertIsInstance(interfaces, list)
        
        # 验证接口信息
        for interface in interfaces:
            self.assertIsInstance(interface, InterfaceInfo)
            self.assertIsInstance(interface.name, str)
            self.assertTrue(len(interface.name) > 0)
    
    def test_interface_info_structure(self):
        """测试接口信息结构"""
        # 创建测试接口信息
        info = InterfaceInfo(
            name="test0",
            display_name="Test Interface",
            description="Test interface for unit testing",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
            is_up=True,
            is_loopback=False,
            mtu=1500,
            interface_type="Ethernet"
        )
        
        # 验证属性
        self.assertEqual(info.name, "test0")
        self.assertEqual(info.ip_address, "192.168.1.100")
        self.assertTrue(info.is_up)
        self.assertFalse(info.is_loopback)
        self.assertEqual(info.mtu, 1500)
    
    def test_format_interface_info(self):
        """测试接口信息格式化"""
        info = InterfaceInfo(
            name="eth0",
            display_name="Ethernet Interface",
            description="Primary ethernet interface",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
            is_up=True,
            mtu=1500,
            interface_type="Ethernet"
        )
        
        formatted = self.provider.format_interface_info(info)
        self.assertIsInstance(formatted, str)
        self.assertIn("eth0", formatted)
        self.assertIn("192.168.1.100", formatted)
        self.assertIn("00:11:22:33:44:55", formatted)
        self.assertIn("启用", formatted)
    
    def test_capture_suitable_interfaces(self):
        """测试获取适合捕获的接口"""
        with patch.object(self.provider, 'get_all_interfaces') as mock_get_all:
            # 模拟接口列表
            mock_interfaces = [
                InterfaceInfo(name="eth0", display_name="Ethernet", description="Ethernet", 
                            is_up=True, is_loopback=False, ip_address="192.168.1.100"),
                InterfaceInfo(name="lo", display_name="Loopback", description="Loopback", 
                            is_up=True, is_loopback=True, ip_address="127.0.0.1"),
                InterfaceInfo(name="eth1", display_name="Ethernet 2", description="Ethernet 2", 
                            is_up=False, is_loopback=False, mac_address="00:11:22:33:44:56")
            ]
            mock_get_all.return_value = mock_interfaces
            
            suitable = self.provider.get_capture_suitable_interfaces()
            
            # 应该排除回环接口，优先选择活动接口
            self.assertTrue(len(suitable) >= 1)
            
            # 第一个应该是活动的非回环接口
            if suitable:
                first_interface = suitable[0]
                self.assertFalse(first_interface.is_loopback)


class TestCaptureOptions(unittest.TestCase):
    """捕获选项数据类测试"""
    
    def test_default_options(self):
        """测试默认选项"""
        options = CaptureOptions()
        
        self.assertEqual(options.interface, "")
        self.assertEqual(options.filter_expression, "")
        self.assertEqual(options.packet_count, 1000)
        self.assertEqual(options.timeout, 60)
        self.assertTrue(options.promiscuous_mode)
        self.assertEqual(options.buffer_size, 1048576)
        self.assertFalse(options.save_to_file)
        self.assertEqual(options.output_file, "")
    
    def test_to_dict_conversion(self):
        """测试转换为字典"""
        options = CaptureOptions(
            interface="eth0",
            filter_expression="tcp port 80",
            packet_count=500,
            timeout=30
        )
        
        data = options.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['interface'], "eth0")
        self.assertEqual(data['filter_expression'], "tcp port 80")
        self.assertEqual(data['packet_count'], 500)
        self.assertEqual(data['timeout'], 30)
    
    def test_from_dict_creation(self):
        """测试从字典创建"""
        data = {
            'interface': 'wlan0',
            'filter_expression': 'udp port 53',
            'packet_count': 2000,
            'timeout': 120,
            'promiscuous_mode': False,
            'buffer_size': 2097152,
            'save_to_file': True,
            'output_file': '/tmp/capture.pcap'
        }
        
        options = CaptureOptions.from_dict(data)
        self.assertEqual(options.interface, 'wlan0')
        self.assertEqual(options.filter_expression, 'udp port 53')
        self.assertEqual(options.packet_count, 2000)
        self.assertEqual(options.timeout, 120)
        self.assertFalse(options.promiscuous_mode)
        self.assertEqual(options.buffer_size, 2097152)
        self.assertTrue(options.save_to_file)
        self.assertEqual(options.output_file, '/tmp/capture.pcap')


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_components_integration(self):
        """测试组件集成"""
        # 创建组件实例
        validator = BPFValidator()
        template_manager = FilterTemplateManager(Path(self.temp_dir))
        interface_provider = InterfaceInfoProvider()
        
        # 测试组件协作
        # 1. 从模板管理器获取模板
        templates = template_manager.get_all_templates()
        self.assertTrue(len(templates) > 0)
        
        # 2. 使用验证器验证模板中的过滤器
        for template in templates[:3]:  # 测试前3个模板
            result = validator.validate_filter(template.filter_expression)
            self.assertTrue(result['is_valid'], f"模板 '{template.name}' 的过滤器应该有效: {result.get('error_message', '')}")
        
        # 3. 获取网络接口信息
        interfaces = interface_provider.get_all_interfaces()
        self.assertIsInstance(interfaces, list)
    
    def test_capture_options_workflow(self):
        """测试捕获选项工作流"""
        # 1. 创建默认选项
        options = CaptureOptions()
        
        # 2. 修改选项
        options.interface = "eth0"
        options.filter_expression = "tcp port 80"
        options.packet_count = 500
        
        # 3. 验证过滤器
        validator = BPFValidator()
        result = validator.validate_filter(options.filter_expression)
        self.assertTrue(result['is_valid'])
        
        # 4. 转换为字典并恢复
        data = options.to_dict()
        restored_options = CaptureOptions.from_dict(data)
        
        self.assertEqual(restored_options.interface, options.interface)
        self.assertEqual(restored_options.filter_expression, options.filter_expression)
        self.assertEqual(restored_options.packet_count, options.packet_count)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)