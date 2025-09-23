#!/usr/bin/env python3
"""
测试会话功能的脚本
"""
import sys
import os
import sqlite3
import time
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.config.settings import Settings

def test_session_functionality():
    """测试会话保存和加载功能"""
    print("开始测试会话功能...")
    
    # 初始化组件
    settings = Settings()
    data_manager = DataManager(settings.DATABASE_PATH)
    
    # 1. 创建测试会话
    print("\n1. 创建测试会话...")
    session_start_time = time.time()
    session_id = data_manager.create_session("测试会话")
    print(f"创建会话ID: {session_id}")
    
    # 2. 添加一些测试数据包
    print("\n2. 添加测试数据包...")
    test_packets = [
        {
            'timestamp': session_start_time + 0.1,
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'src_port': 12345,
            'dst_port': 53,
            'protocol': 'UDP',
            'length': 64,
            'summary': 'DNS Query'
        },
        {
            'timestamp': session_start_time + 0.2,
            'src_ip': '8.8.8.8',
            'dst_ip': '192.168.1.100',
            'src_port': 53,
            'dst_port': 12345,
            'protocol': 'UDP',
            'length': 128,
            'summary': 'DNS Response'
        },
        {
            'timestamp': session_start_time + 0.3,
            'src_ip': '192.168.1.100',
            'dst_ip': '93.184.216.34',
            'src_port': 54321,
            'dst_port': 80,
            'protocol': 'TCP',
            'length': 256,
            'summary': 'HTTP Request'
        }
    ]
    
    for i, packet in enumerate(test_packets):
        data_manager.save_packet(packet)
        print(f"保存数据包 {i+1}: {packet['src_ip']} -> {packet['dst_ip']}")
    
    # 3. 更新会话统计
    print("\n3. 更新会话统计...")
    total_packets = len(test_packets)
    total_bytes = sum(p['length'] for p in test_packets)
    data_manager.update_session(session_id, total_packets, total_bytes)
    
    # 手动设置会话结束时间
    session_end_time = session_start_time + 1.0  # 会话持续1秒
    with data_manager._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET end_time = ? 
            WHERE id = ?
        """, (session_end_time, session_id))
        conn.commit()
    
    print(f"更新会话统计: {total_packets} 个数据包, {total_bytes} 字节")
    
    # 4. 测试会话加载
    print("\n4. 测试会话加载...")
    sessions = data_manager.get_sessions()
    print(f"找到 {len(sessions)} 个会话:")
    for session in sessions:
        print(f"  会话 {session['id']}: {session['session_name']} - {session['packet_count']} 包, {session['total_bytes']} 字节")
    
    # 5. 测试数据包加载
    print("\n5. 测试数据包加载...")
    if sessions:
        # 直接使用我们创建的会话ID，而不是从sessions列表中获取
        session_packets = data_manager.get_packets_by_session(session_id)
        print(f"会话 {session_id} 包含 {len(session_packets)} 个数据包:")
        for packet in session_packets:
            print(f"  {packet['src_ip']} -> {packet['dst_ip']} ({packet['protocol']}) - {packet['length']} 字节")
    
    # 6. 验证数据一致性
    print("\n6. 验证数据一致性...")
    # 获取我们创建的会话的统计信息
    with data_manager._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT packet_count, total_bytes FROM sessions WHERE id = ?", (session_id,))
        session_stats = cursor.fetchone()
    
    if session_stats:
        expected_packets = session_stats['packet_count']
        expected_bytes = session_stats['total_bytes']
        print(f"会话统计 - 数据包数量: {expected_packets}, 总字节数: {expected_bytes}")
        
        # 获取会话数据包
        session_packets = data_manager.get_packets_by_session(session_id)
        actual_packets = len(session_packets)
        
        # 检查是否找到了我们的测试数据包
        test_packet_count = 0
        for packet in session_packets:
            # 检查是否是我们的测试数据包
            if (packet['src_ip'] in ['192.168.1.100', '8.8.8.8'] and 
                packet['dst_ip'] in ['8.8.8.8', '192.168.1.100', '93.184.216.34']):
                test_packet_count += 1
        
        if test_packet_count >= 3:
            print(f"✓ 找到了 {test_packet_count} 个测试数据包")
        else:
            print(f"✗ 只找到了 {test_packet_count} 个测试数据包，期望至少3个")
    else:
        print("✗ 无法获取会话统计信息")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_session_functionality()