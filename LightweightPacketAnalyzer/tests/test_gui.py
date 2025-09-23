"""
GUI模块测试

测试MainWindow类的核心功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tkinter as tk

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from network_analyzer.gui.main_window import MainWindow


class TestMainWindow(unittest.TestCase):
    """MainWindow测试类"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建模拟的settings对象
        self.mock_settings = Mock()
        # 设置数据库路径为内存数据库
        self.mock_settings.DATABASE_PATH = ":memory:"
        # 设置get_database_path方法返回字符串路径而不是Mock对象
        self.mock_settings.get_database_path.return_value = ":memory:"
        # 设置窗口尺寸属性为具体数值，避免Mock对象与int运算错误
        self.mock_settings.WINDOW_WIDTH = 1200
        self.mock_settings.WINDOW_HEIGHT = 800
        self.mock_settings.APP_NAME = "Test App"

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')  # 阻止UI初始化
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')  # 阻止GUI更新定时器启动
    @patch('tkinter.Tk')
    def test_main_window_core_init(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试MainWindow核心初始化（不包括UI组件）"""
        # 设置Mock对象的返回值
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 验证基本属性设置
        self.assertEqual(window.settings, self.mock_settings)
        self.assertIsNotNone(window.logger)
        
        # 验证各个组件的初始化
        mock_data_manager.assert_called_once_with(":memory:")
        mock_packet_capture.assert_called_once_with(self.mock_settings)
        mock_data_processor.assert_called_once()
        
        # 验证GUI相关设置
        mock_tk.assert_called_once()
        mock_root.title.assert_called_once_with("Test App")
        mock_root.geometry.assert_called_once_with("1200x800")
        
        # 验证UI初始化和GUI更新定时器被阻止
        mock_init_ui.assert_called_once()
        mock_start_gui_updates.assert_called_once()
        
        # 验证队列初始化
        self.assertIsNotNone(window.packet_queue)
        self.assertIsNotNone(window.stats_queue)
        
        # 验证GUI更新标志初始化
        self.assertFalse(window._gui_update_active)
        self.assertIsNone(window._update_timer_id)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_check_capture_status_with_capture(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_check_capture_status方法 - 有捕获器且正在捕获"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 设置packet_capture的is_capturing属性
        window.packet_capture.is_capturing = True
        
        # 测试方法
        result = window._check_capture_status()
        
        # 验证结果
        self.assertTrue(result)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_check_capture_status_without_capture(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_check_capture_status方法 - 有捕获器但未捕获"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 设置packet_capture的is_capturing属性
        window.packet_capture.is_capturing = False
        
        # 测试方法
        result = window._check_capture_status()
        
        # 验证结果
        self.assertFalse(result)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_check_capture_status_no_packet_capture(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_check_capture_status方法 - 无捕获器"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 设置packet_capture为None
        window.packet_capture = None
        
        # 测试方法
        result = window._check_capture_status()
        
        # 验证结果
        self.assertFalse(result)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_check_capture_status_exception_handling(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_check_capture_status方法 - 异常处理"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 创建一个会抛出异常的Mock对象
        mock_capture = Mock()
        type(mock_capture).is_capturing = property(lambda self: (_ for _ in ()).throw(Exception("Test exception")))
        window.packet_capture = mock_capture
        
        # Mock logger
        window.logger = Mock()
        
        # 测试方法
        result = window._check_capture_status()
        
        # 验证结果
        self.assertFalse(result)
        # 验证日志记录被调用
        window.logger.error.assert_called_once()

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.simpledialog.askstring')
    def test_get_session_name_success(self, mock_askstring, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_get_session_name方法 - 成功获取会话名称"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askstring.return_value = "测试会话"
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._get_session_name()
        
        # 验证结果
        self.assertEqual(result, "测试会话")
        mock_askstring.assert_called_once_with(
            "新建会话",
            "请输入会话名称:",
            parent=window.root,
            initialvalue="新会话"
        )

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.simpledialog.askstring')
    def test_get_session_name_cancel(self, mock_askstring, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_get_session_name方法 - 用户取消"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askstring.return_value = None
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._get_session_name()
        
        # 验证结果
        self.assertIsNone(result)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.messagebox.showerror')
    def test_get_session_name_empty(self, mock_showerror, mock_askstring, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_get_session_name方法 - 空名称"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askstring.return_value = "   "  # 空白字符串
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._get_session_name()
        
        # 验证结果
        self.assertIsNone(result)
        mock_showerror.assert_called_once_with("错误", "会话名称不能为空")

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.askyesnocancel')
    def test_ask_save_current_data_yes(self, mock_askyesnocancel, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_ask_save_current_data方法 - 选择是"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askyesnocancel.return_value = True
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._ask_save_current_data()
        
        # 验证结果
        self.assertEqual(result, 'yes')

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.askyesnocancel')
    def test_ask_save_current_data_no(self, mock_askyesnocancel, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_ask_save_current_data方法 - 选择否"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askyesnocancel.return_value = False
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._ask_save_current_data()
        
        # 验证结果
        self.assertEqual(result, 'no')

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.askyesnocancel')
    def test_ask_save_current_data_cancel(self, mock_askyesnocancel, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试_ask_save_current_data方法 - 选择取消"""
        # 设置Mock对象
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_askyesnocancel.return_value = None
        
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 测试方法
        result = window._ask_save_current_data()
        
        # 验证结果
        self.assertEqual(result, 'cancel')

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_save_current_session_success(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试成功保存当前会话"""
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 设置当前会话
        window.current_session_id = 1
        window.current_session_name = "测试会话"
        
        # Mock数据处理器统计数据
        mock_stats = {
            'total_packets': 100,
            'total_bytes': 50000
        }
        
        with patch.object(window.data_processor, 'get_statistics', return_value=mock_stats), \
             patch.object(window.data_manager, 'update_session') as mock_update, \
             patch('tkinter.messagebox.showinfo') as mock_info:
            
            result = window._save_current_session()
            
            self.assertTrue(result)
            mock_update.assert_called_once_with(1, 100, 50000)
            mock_info.assert_called_once()

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_save_current_session_no_session_id(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试保存会话时没有当前会话ID"""
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        
        # 清空当前会话
        window.current_session_id = None
        window.current_session_name = "新会话"
        
        mock_stats = {
            'total_packets': 50,
            'total_bytes': 25000
        }
        
        with patch.object(window.data_processor, 'get_statistics', return_value=mock_stats), \
             patch.object(window.data_manager, 'create_session', return_value=2) as mock_create, \
             patch.object(window.data_manager, 'update_session') as mock_update, \
             patch('tkinter.messagebox.showinfo') as mock_info:
            
            result = window._save_current_session()
            
            self.assertTrue(result)
            mock_create.assert_called_once_with("新会话")
            mock_update.assert_called_once_with(2, 50, 25000)
            self.assertEqual(window.current_session_id, 2)

    @patch('network_analyzer.gui.main_window.DataProcessor')
    @patch('network_analyzer.gui.main_window.PacketCapture')
    @patch('network_analyzer.gui.main_window.DataManager')
    @patch('network_analyzer.gui.main_window.MainWindow._init_ui')
    @patch('network_analyzer.gui.main_window.MainWindow._start_gui_updates')
    @patch('tkinter.Tk')
    def test_save_current_session_exception(self, mock_tk, mock_start_gui_updates, mock_init_ui, mock_data_manager, mock_packet_capture, mock_data_processor):
        """测试保存会话时发生异常"""
        # 创建MainWindow实例
        window = MainWindow(self.mock_settings)
        window.current_session_id = 1
        
        with patch.object(window.data_processor, 'get_statistics', side_effect=Exception("测试异常")), \
             patch('tkinter.messagebox.showerror') as mock_error, \
             patch.object(window.logger, 'error') as mock_log:
            
            result = window._save_current_session()
            
            self.assertFalse(result)
            mock_error.assert_called_once()
            mock_log.assert_called_once()


    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_reset_gui_components_success(self, mock_tk, mock_logging, mock_messagebox):
        """测试成功重置GUI组件"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟GUI组件
            window.packet_tree = MagicMock()
            window.packet_tree.get_children.return_value = ['item1', 'item2']
            
            window.stats_text = MagicMock()
            window.detail_text = MagicMock()
            window.status_text = MagicMock()
            window.packet_count_label = MagicMock()
            
            # 设置初始会话状态
            window.current_session_id = "test_session"
            window.current_session_name = "测试会话"
            
            # 模拟数据处理器
            window.data_processor = MagicMock()
            
            # 执行重置
            window._reset_gui_components()
            
            # 验证数据包列表被清空
            window.packet_tree.delete.assert_any_call('item1')
            window.packet_tree.delete.assert_any_call('item2')
            
            # 验证文本组件被重置
            window.stats_text.config.assert_any_call(state=tk.NORMAL)
            window.stats_text.delete.assert_called_with(1.0, tk.END)
            window.stats_text.insert.assert_called_with(tk.END, "暂无统计信息")
            window.stats_text.config.assert_any_call(state=tk.DISABLED)
            
            window.detail_text.config.assert_any_call(state=tk.NORMAL)
            window.detail_text.delete.assert_called_with(1.0, tk.END)
            window.detail_text.insert.assert_called_with(tk.END, "请选择数据包查看详情")
            window.detail_text.config.assert_any_call(state=tk.DISABLED)
            
            # 验证状态栏更新
            window.status_text.config.assert_called_with(text="就绪 - 新会话")
            window.packet_count_label.config.assert_called_with(text="数据包: 0")
            
            # 验证会话状态重置
            self.assertIsNone(window.current_session_id)
            self.assertIsNone(window.current_session_name)
            
            # 验证数据处理器重置
            window.data_processor.reset_statistics.assert_called_once()
    
    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_reset_gui_components_missing_attributes(self, mock_tk, mock_logging, mock_messagebox):
        """测试重置GUI组件时缺少某些属性"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 不设置GUI组件属性，测试hasattr检查
            
            # 执行重置（不应该抛出异常）
            window._reset_gui_components()
            
            # 验证会话状态仍然被重置
            self.assertIsNone(window.current_session_id)
            self.assertIsNone(window.current_session_name)
    
    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_reset_gui_components_exception_handling(self, mock_tk, mock_logging, mock_messagebox):
        """测试重置GUI组件时的异常处理"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟GUI组件抛出异常
            window.packet_tree = MagicMock()
            window.packet_tree.get_children.side_effect = Exception("测试异常")
            
            # 执行重置
            window._reset_gui_components()
            
            # 验证异常被处理
            mock_messagebox.showerror.assert_called_once()
            error_call = mock_messagebox.showerror.call_args[0]
            self.assertEqual(error_call[0], "错误")
            self.assertIn("重置GUI组件时发生错误", error_call[1])

    # 新建会话方法的单元测试
    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_success(self, mock_tk, mock_logging, mock_messagebox):
        """测试成功新建会话"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟方法返回值
            window._check_capture_status = MagicMock(return_value=False)
            window._ask_save_current_data = MagicMock(return_value="no")
            window._get_session_name = MagicMock(return_value="测试会话")
            window._reset_gui_components = MagicMock()
            window._update_session_status = MagicMock()
            window.data_manager.create_session = MagicMock(return_value="session_123")
            
            # 执行新建会话
            window._new_session()
            
            # 验证调用顺序和参数
            window._check_capture_status.assert_called_once()
            window._ask_save_current_data.assert_called_once()
            window._get_session_name.assert_called_once()
            window._reset_gui_components.assert_called_once()
            window.data_manager.create_session.assert_called_once_with("测试会话")
            window._update_session_status.assert_called_once_with("测试会话")
            
            # 验证会话信息更新
            self.assertEqual(window.current_session_id, "session_123")
            self.assertEqual(window.current_session_name, "测试会话")
            
            # 验证成功消息
            mock_messagebox.showinfo.assert_called_once_with("成功", "新会话 '测试会话' 创建成功")

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_capture_running(self, mock_tk, mock_logging, mock_messagebox):
        """测试捕获正在运行时新建会话"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟捕获正在运行
            window._check_capture_status = MagicMock(return_value=True)
            
            # 执行新建会话
            window._new_session()
            
            # 验证警告消息
            mock_messagebox.showwarning.assert_called_once_with("警告", "请先停止数据包捕获后再新建会话")

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_user_cancel(self, mock_tk, mock_logging, mock_messagebox):
        """测试用户取消新建会话"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟用户取消操作
            window._check_capture_status = MagicMock(return_value=False)
            window._ask_save_current_data = MagicMock(return_value="cancel")
            
            # 执行新建会话
            window._new_session()
            
            # 验证没有继续执行后续步骤
            window._ask_save_current_data.assert_called_once()

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_save_failed(self, mock_tk, mock_logging, mock_messagebox):
        """测试保存当前会话失败时新建会话"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟保存失败
            window._check_capture_status = MagicMock(return_value=False)
            window._ask_save_current_data = MagicMock(return_value="yes")
            window._save_current_session = MagicMock(return_value=False)
            
            # 执行新建会话
            window._new_session()
            
            # 验证错误消息
            mock_messagebox.showerror.assert_called_once_with("错误", "保存当前会话失败，无法继续新建会话")

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_create_failed(self, mock_tk, mock_logging, mock_messagebox):
        """测试创建新会话失败"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟创建会话失败
            window._check_capture_status = MagicMock(return_value=False)
            window._ask_save_current_data = MagicMock(return_value="no")
            window._get_session_name = MagicMock(return_value="测试会话")
            window._reset_gui_components = MagicMock()
            window.data_manager.create_session = MagicMock(return_value=None)
            
            # 执行新建会话
            window._new_session()
            
            # 验证错误消息
            mock_messagebox.showerror.assert_called_once_with("错误", "创建新会话失败")

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_exception_handling(self, mock_tk, mock_logging, mock_messagebox):
        """测试新建会话时的异常处理"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟异常
            window._check_capture_status = MagicMock(side_effect=Exception("测试异常"))
            
            # 执行新建会话
            window._new_session()
            
            # 验证异常被处理
            mock_messagebox.showerror.assert_called_once()
            error_call = mock_messagebox.showerror.call_args[0]
            self.assertEqual(error_call[0], "错误")
            self.assertIn("新建会话失败", error_call[1])

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_update_session_status(self, mock_tk, mock_logging, mock_messagebox):
        """测试更新会话状态"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟GUI组件
            window.status_text = MagicMock()
            window.root = mock_root
            
            # 重置title调用计数（因为初始化时已经调用过一次）
            mock_root.title.reset_mock()
            
            # 执行状态更新
            window._update_session_status("测试会话")
            
            # 验证状态栏更新
            window.status_text.config.assert_called_once_with(text="当前会话: 测试会话")
            
            # 验证窗口标题更新
            mock_root.title.assert_called_once_with("Test App - 测试会话")

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_public_interface_success(self, mock_tk, mock_logging, mock_messagebox):
        """测试新建会话公共接口成功"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 设置初始状态
            window.current_session_id = "old_session"
            
            # 模拟_new_session方法成功执行
            def mock_new_session():
                window.current_session_id = "new_session"
            
            window._new_session = MagicMock(side_effect=mock_new_session)
            
            # 执行公共接口
            result = window.new_session()
            
            # 验证返回值
            self.assertTrue(result)
            window._new_session.assert_called_once()

    @patch('network_analyzer.gui.main_window.messagebox')
    @patch('network_analyzer.gui.main_window.logging')
    @patch('network_analyzer.gui.main_window.tk.Tk')
    def test_new_session_public_interface_failed(self, mock_tk, mock_logging, mock_messagebox):
        """测试新建会话公共接口失败"""
        with patch('network_analyzer.gui.main_window.Settings') as mock_settings:
            mock_settings.return_value.get_database_path.return_value = ":memory:"
            mock_settings.return_value.APP_NAME = "Test App"
            mock_settings.return_value.WINDOW_WIDTH = 800
            mock_settings.return_value.WINDOW_HEIGHT = 600
            
            # 模拟Tk实例
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            window = MainWindow(mock_settings.return_value)
            
            # 模拟_new_session方法抛出异常
            window._new_session = MagicMock(side_effect=Exception("测试异常"))
            
            # 执行公共接口
            result = window.new_session()
            
            # 验证返回值
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()