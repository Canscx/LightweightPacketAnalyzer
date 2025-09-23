"""
GUI模块测试

测试MainWindow类的核心功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

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


if __name__ == '__main__':
    unittest.main()