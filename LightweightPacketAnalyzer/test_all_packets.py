#!/usr/bin/env python3
"""测试所有数据包的查询功能"""

import sys
import os
sys.path.insert(0, 'src')

from network_analyzer.storage.data_manager import DataManager
import sqlite3

def test_all_packets():
    """测试所有数据包的查询功能"""
    
    # 测试get_packet_by_features方法
    dm = DataManager('network_analyzer.db')
    
    # 先查看数据库中的实际timestamp值
    conn = sqlite3.connect('network_analyzer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length FROM packets ORDER BY id')
    packets = cursor.fetchall()
    
    print('测试所有数据包的查询功能:')
    success_count = 0
    
    for i, packet in enumerate(packets, 1):
        print(f'\n测试数据包 {i}: ID={packet[0]}')
        print(f'  timestamp: {packet[1]}')
        print(f'  src_ip: {packet[2]}, dst_ip: {packet[3]}')
        print(f'  protocol: {packet[4]}, length: {packet[5]}')
        
        result = dm.get_packet_by_features(
            timestamp=packet[1],
            src_ip=packet[2],
            dst_ip=packet[3],
            protocol=packet[4],
            length=packet[5],
            session_id=None
        )
        
        if result:
            print(f'  ✓ 成功找到数据包，ID: {result.get("id")}')
            raw_data = result.get("raw_data", b"")
            if isinstance(raw_data, str):
                raw_data = raw_data.encode()
            print(f'  ✓ 原始数据长度: {len(raw_data)} bytes')
            success_count += 1
        else:
            print(f'  ✗ 未找到数据包')
    
    print(f'\n总结: {success_count}/{len(packets)} 个数据包查询成功')
    
    conn.close()
    return success_count == len(packets)

if __name__ == "__main__":
    test_all_packets()