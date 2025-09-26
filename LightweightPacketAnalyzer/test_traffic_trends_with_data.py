#!/usr/bin/env python3
"""
流量趋势功能测试脚本（包含模拟数据）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from datetime import datetime, timedelta
import random
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.gui.traffic_trends_dialog import TrafficTrendsDialog

def insert_test_data(data_manager):
    """插入测试数据"""
    print("插入测试数据...")
    
    # 创建测试会话
    session_id = data_manager.create_session("测试会话", {"description": "流量趋势测试数据"})
    print(f"创建测试会话: {session_id}")
    
    # 生成最近5分钟的测试数据
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)
    
    protocols = ['TCP', 'UDP', 'ICMP', 'DNS']
    test_packets = []
    
    # 每10秒生成一批数据包
    current_time = start_time
    while current_time <= end_time:
        # 为每个协议生成随机数量的数据包
        for protocol in protocols:
            packet_count = random.randint(1, 10)
            for _ in range(packet_count):
                packet = {
                    'timestamp': current_time.timestamp(),
                    'src_ip': f"192.168.1.{random.randint(1, 100)}",
                    'dst_ip': f"10.0.0.{random.randint(1, 100)}",
                    'src_port': random.randint(1024, 65535),
                    'dst_port': random.randint(80, 8080),
                    'protocol': protocol,
                    'length': random.randint(64, 1500),
                    'session_id': session_id
                }
                test_packets.append(packet)
        
        current_time += timedelta(seconds=10)
    
    # 批量插入数据
    data_manager.save_packets_batch(test_packets)
    print(f"插入了 {len(test_packets)} 个测试数据包")
    
    return session_id

def test_traffic_trends_with_data():
    """测试流量趋势功能（包含数据）"""
    print("开始测试流量趋势功能（包含数据）...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("流量趋势测试")
    root.geometry("1400x900")
    
    try:
        # 初始化数据管理器
        data_manager = DataManager("test_traffic_trends.db")
        print("数据管理器初始化成功")
        
        # 插入测试数据
        session_id = insert_test_data(data_manager)
        
        # 创建流量趋势对话框
        trends_dialog = TrafficTrendsDialog(root, data_manager)
        print("流量趋势对话框创建成功")
        
        # 显示对话框
        trends_dialog.show()
        print("流量趋势对话框已显示")
        
        # 添加说明标签
        info_label = tk.Label(root, 
                             text=f"流量趋势测试 - 会话ID: {session_id}\n包含最近5分钟的模拟网络数据",
                             font=("Arial", 12),
                             bg="lightblue",
                             pady=10)
        info_label.pack(fill=tk.X)
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("测试完成")

if __name__ == "__main__":
    test_traffic_trends_with_data()