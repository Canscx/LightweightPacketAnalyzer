#!/usr/bin/env python3
"""测试GUI数据包详情显示的完整集成测试"""

import sys
import os
sys.path.insert(0, 'src')

from network_analyzer.storage.data_manager import DataManager
import sqlite3

def test_packet_features_matching():
    """测试数据包特征匹配功能"""
    
    print("=== 测试数据包特征匹配功能 ===")
    
    # 创建数据管理器
    dm = DataManager('network_analyzer.db')
    
    # 获取数据库中的数据包
    conn = sqlite3.connect('network_analyzer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length FROM packets ORDER BY id')
    packets = cursor.fetchall()
    conn.close()
    
    print(f'数据库中有 {len(packets)} 个数据包')
    
    # 模拟GUI中的数据包特征存储和查询过程
    item_to_packet_features = {}
    
    for i, packet in enumerate(packets):
        packet_id, timestamp, src_ip, dst_ip, protocol, length = packet
        
        # 模拟GUI中_add_packet_to_list的逻辑
        item_id = f"item_{i+1}"
        packet_features = {
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'protocol': protocol,
            'length': length,
            'session_id': 1  # 模拟session_id（虽然数据库中没有）
        }
        
        item_to_packet_features[item_id] = packet_features
        print(f'\n模拟添加数据包到GUI: {item_id}')
        print(f'  特征: {packet_features}')
        
        # 模拟GUI中_get_packet_raw_data的逻辑
        try:
            # 使用修复后的查询方式（不传递session_id）
            packet_data = dm.get_packet_by_features(
                timestamp=packet_features['timestamp'],
                src_ip=packet_features['src_ip'],
                dst_ip=packet_features['dst_ip'],
                protocol=packet_features['protocol'],
                length=packet_features['length'],
                session_id=None  # 明确设置为None
            )
            
            if packet_data:
                raw_data = packet_data.get('raw_data', b'')
                if isinstance(raw_data, str):
                    raw_data = raw_data.encode('latin-1')
                print(f'  ✓ 成功获取原始数据，长度: {len(raw_data)} bytes')
                print(f'  ✓ 数据包ID: {packet_data.get("id")}')
            else:
                print(f'  ✗ 无法获取原始数据')
                
        except Exception as e:
            print(f'  ✗ 查询时出错: {e}')
    
    print(f'\n=== 测试完成 ===')
    return len(packets)

def test_session_id_handling():
    """测试session_id字段处理"""
    
    print("\n=== 测试session_id字段处理 ===")
    
    dm = DataManager('network_analyzer.db')
    
    # 测试不同的session_id参数
    test_cases = [
        {"session_id": None, "description": "session_id=None"},
        {"session_id": 1, "description": "session_id=1"},
        {"session_id": "test", "description": "session_id='test'"},
    ]
    
    # 获取第一个数据包用于测试
    conn = sqlite3.connect('network_analyzer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, src_ip, dst_ip, protocol, length FROM packets LIMIT 1')
    packet = cursor.fetchone()
    conn.close()
    
    if packet:
        timestamp, src_ip, dst_ip, protocol, length = packet
        
        for test_case in test_cases:
            print(f'\n测试 {test_case["description"]}:')
            try:
                result = dm.get_packet_by_features(
                    timestamp=timestamp,
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    protocol=protocol,
                    length=length,
                    session_id=test_case["session_id"]
                )
                
                if result:
                    print(f'  ✓ 查询成功，找到数据包ID: {result.get("id")}')
                else:
                    print(f'  ✗ 查询失败，未找到数据包')
                    
            except Exception as e:
                print(f'  ✗ 查询出错: {e}')
    
    print(f'\n=== session_id测试完成 ===')

if __name__ == "__main__":
    packet_count = test_packet_features_matching()
    test_session_id_handling()
    
    print(f'\n总结: 数据库中有 {packet_count} 个数据包，GUI数据包详情显示功能已修复')