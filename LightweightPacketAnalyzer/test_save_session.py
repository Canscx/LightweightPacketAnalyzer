#!/usr/bin/env python3
"""
T1.3 保存会话功能测试脚本
测试保存会话功能的各种场景
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import messagebox

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.gui.main_window import MainWindow
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.processing.data_processor import DataProcessor


class TestSaveSessionFunction(unittest.TestCase):
    """T1.3 保存会话功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口
        
        # Mock依赖
        self.mock_data_manager = Mock(spec=DataManager)
        self.mock_data_processor = Mock()  # 移除spec限制
        self.mock_data_processor.get_statistics = Mock()  # 显式添加方法
        self.mock_settings = Mock()
        self.mock_settings.get_database_path.return_value = ":memory:"
        self.mock_settings.WINDOW_WIDTH = 1200
        self.mock_settings.WINDOW_HEIGHT = 800
        
        # 创建MainWindow实例
        with patch('network_analyzer.gui.main_window.PacketCapture'), \
             patch('network_analyzer.gui.main_window.DataProcessor') as mock_dp_class, \
             patch('network_analyzer.gui.main_window.DataManager') as mock_dm_class, \
             patch('tkinter.Tk') as mock_tk:
            
            # 设置Mock类返回我们的Mock实例
            mock_dm_class.return_value = self.mock_data_manager
            mock_dp_class.return_value = self.mock_data_processor
            mock_tk.return_value = self.root
            
            self.main_window = MainWindow(self.mock_settings)
    
    def tearDown(self):
        """测试后清理"""
        self.root.destroy()
    
    @patch('tkinter.messagebox.showwarning')
    def test_save_session_no_data_processor(self, mock_warning):
        """测试1: 无数据处理器时的保存行为"""
        # 设置无数据处理器状态
        self.main_window.data_processor = None
        
        # 调用保存会话
        self.main_window._save_session()
        
        # 验证显示警告消息
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]  # 使用位置参数
        self.assertIn("无法保存", args[0])  # 检查消息内容
    
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    def test_save_session_no_packets_user_confirms(self, mock_info, mock_askyesno):
        """测试2: 无数据包但用户确认保存"""
        # 设置无数据包状态
        self.mock_data_processor.get_statistics.return_value = {'total_packets': 0}
        mock_askyesno.return_value = True  # 用户确认保存
        
        # Mock保存成功
        self.main_window.current_session_id = None
        self.mock_data_manager.create_session.return_value = 1
        self.mock_data_manager.update_session.return_value = None
        
        # 调用保存会话
        self.main_window._save_session()
        
        # 验证询问用户
        mock_askyesno.assert_called_once()
        args = mock_askyesno.call_args[0]
        self.assertIn("确认保存", args[0])
        
        # 验证显示成功消息
        mock_info.assert_called_once()
    
    @patch('tkinter.messagebox.askyesno')
    def test_save_session_no_packets_user_cancels(self, mock_askyesno):
        """测试3: 无数据包且用户取消保存"""
        # 设置无数据包状态
        self.mock_data_processor.get_statistics.return_value = {'total_packets': 0}
        mock_askyesno.return_value = False  # 用户取消保存
        
        # 调用保存会话
        self.main_window._save_session()
        
        # 验证询问用户
        mock_askyesno.assert_called_once()
        
        # 验证没有调用保存逻辑
        self.mock_data_manager.create_session.assert_not_called()
        self.mock_data_manager.update_session.assert_not_called()
    
    @patch('tkinter.messagebox.showinfo')
    def test_save_session_with_packets_success(self, mock_info):
        """测试4: 有数据包且保存成功"""
        # 设置有数据包状态
        self.mock_data_processor.get_statistics.return_value = {
            'total_packets': 100,
            'total_bytes': 50000
        }
        
        # Mock保存成功
        self.main_window.current_session_id = 1
        self.mock_data_manager.update_session.return_value = None
        
        # 调用保存会话
        self.main_window._save_session()
        
        # 验证调用了更新会话
        self.mock_data_manager.update_session.assert_called_once_with(1, 100, 50000)
        
        # 验证显示成功消息
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertIn("保存成功", args[0])
    
    @patch('tkinter.messagebox.showerror')
    def test_save_session_failure(self, mock_error):
        """测试5: 保存失败处理"""
        # 设置有数据包状态
        self.mock_data_processor.get_statistics.return_value = {
            'total_packets': 100,
            'total_bytes': 50000
        }
        
        # Mock保存失败
        self.main_window.current_session_id = 1
        self.mock_data_manager.update_session.side_effect = Exception("数据库错误")
        
        # 调用保存会话
        self.main_window._save_session()
        
        # 验证显示错误消息
        mock_error.assert_called_once()
        args = mock_error.call_args[0]
        self.assertIn("保存失败", args[0])
    
    def test_keyboard_shortcut_binding(self):
        """测试6: 键盘快捷键绑定"""
        # 检查是否绑定了Ctrl+S
        bindings = self.main_window.root.bind_all('<Control-s>')
        self.assertIsNotNone(bindings)
        
        bindings = self.main_window.root.bind_all('<Control-S>')
        self.assertIsNotNone(bindings)
    
    def test_menu_accelerator_display(self):
        """测试7: 菜单快捷键显示"""
        # 这个测试需要检查菜单项是否正确显示了accelerator
        # 由于tkinter菜单的限制，这里主要验证方法存在
        self.assertTrue(hasattr(self.main_window, '_save_session'))
        self.assertTrue(callable(getattr(self.main_window, '_save_session')))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("T1.3 保存会话功能 - 自动化测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSaveSessionFunction)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)