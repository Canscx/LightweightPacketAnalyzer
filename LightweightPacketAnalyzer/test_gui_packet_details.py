#!/usr/bin/env python3
"""测试GUI中数据包详情显示功能"""

import sys
import os
sys.path.insert(0, 'src')

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.main_window import MainWindow
from network_analyzer.processing.data_processor import DataProcessor
import sqlite3
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_gui_packet_details():
    """测试GUI中数据包详情显示功能"""
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = MainWindow()
    
    # 模拟加载现有会话
    main_window.data_manager = DataManager('network_analyzer.db')
    main_window.data_processor = DataProcessor()
    
    # 获取数据库中的数据包
    conn = sqlite3.connect('network_analyzer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length FROM packets ORDER BY id')
    packets = cursor.fetchall()
    conn.close()
    
    print(f'数据库中有 {len(packets)} 个数据包')
    
    # 模拟添加数据包到GUI列表
    for packet in packets:
        packet_id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length = packet
        
        # 创建模拟的数据包特征
        packet_features = {
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'protocol': protocol,
            'length': length,
            'session_id': 1  # 模拟session_id
        }
        
        # 模拟添加到GUI列表
        print(f'模拟添加数据包 {packet_id}: {src_ip}:{src_port} -> {dst_ip}:{dst_port} ({protocol})')
        
        # 测试获取原始数据
        try:
            raw_data = main_window.data_manager.get_packet_by_features(
                timestamp=packet_features['timestamp'],
                src_ip=packet_features['src_ip'],
                dst_ip=packet_features['dst_ip'],
                protocol=packet_features['protocol'],
                length=packet_features['length'],
                session_id=None  # 不使用session_id
            )
            
            if raw_data:
                print(f'  ✓ 成功获取原始数据，长度: {len(raw_data.get("raw_data", b""))} bytes')
            else:
                print(f'  ✗ 无法获取原始数据')
                
        except Exception as e:
            print(f'  ✗ 获取原始数据时出错: {e}')
    
    print('\n测试完成')
    app.quit()

if __name__ == "__main__":
    test_gui_packet_details()