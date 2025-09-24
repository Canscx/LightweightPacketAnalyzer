#!/usr/bin/env python3
"""
调试会话55数据包加载的脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager

def debug_session_packets():
    """调试会话55的数据包加载"""
    
    # 初始化数据管理器
    data_manager = DataManager('data/network_analyzer.db')
    
    print('🔍 调试会话55的数据包加载')
    print('=' * 50)
    
    # 1. 检查会话55的详细信息
    import sqlite3
    conn = sqlite3.connect('data/network_analyzer.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE id = 55')
    session_info = cursor.fetchone()
    if session_info:
        print(f'📊 会话55信息:')
        print(f'   ID: {session_info[0]}')
        print(f'   名称: {session_info[1]}')
        print(f'   开始时间: {session_info[2]}')
        print(f'   结束时间: {session_info[3]}')
        print(f'   数据包数: {session_info[4]}')
        print(f'   总字节数: {session_info[5]}')
    else:
        print('❌ 会话55不存在')
        conn.close()
        return
    
    # 2. 直接调用get_packets_by_session(55)
    print(f'\n🔍 调用get_packets_by_session(55):')
    packets = data_manager.get_packets_by_session(55)
    print(f'   返回数据包数量: {len(packets)}')
    
    # 3. 显示每个数据包的详细信息
    for i, packet in enumerate(packets):
        print(f'\n📦 数据包 {i+1}:')
        print(f'   ID: {packet.get("id", "N/A")}')
        print(f'   时间戳: {packet.get("timestamp", "N/A")}')
        print(f'   源IP: {packet.get("src_ip", "N/A")}')
        print(f'   目标IP: {packet.get("dst_ip", "N/A")}')
        print(f'   协议: {packet.get("protocol", "N/A")}')
        print(f'   长度: {packet.get("length", "N/A")}')
        raw_data = packet.get('raw_data')
        if raw_data:
            print(f'   原始数据: 存在 ({len(raw_data)} 字节)')
            print(f'   原始数据类型: {type(raw_data)}')
            if isinstance(raw_data, bytes):
                print(f'   前16字节: {raw_data[:16].hex()}')
            elif isinstance(raw_data, str):
                print(f'   前16字符: {raw_data[:16]}')
        else:
            print(f'   原始数据: 不存在')
    
    # 4. 检查数据库中所有数据包
    print(f'\n🔍 数据库中所有数据包:')
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length, CASE WHEN raw_data IS NULL THEN "无" ELSE "有" END as has_raw FROM packets ORDER BY id')
    all_packets = cursor.fetchall()
    print(f'   总数据包数: {len(all_packets)}')
    for packet in all_packets:
        print(f'   ID {packet[0]}: {packet[2]} -> {packet[3]} ({packet[4]}) 原始数据:{packet[6]}')
    
    # 5. 检查会话55时间范围内的数据包
    start_time = session_info[2]
    end_time = session_info[3]
    print(f'\n🔍 会话55时间范围内的数据包 ({start_time} - {end_time}):')
    if end_time:
        cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol FROM packets WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp', (start_time, end_time))
    else:
        cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol FROM packets WHERE timestamp >= ? ORDER BY timestamp', (start_time,))
    
    time_range_packets = cursor.fetchall()
    print(f'   时间范围内数据包数: {len(time_range_packets)}')
    for packet in time_range_packets:
        print(f'   ID {packet[0]}: 时间戳 {packet[1]}, {packet[2]} -> {packet[3]} ({packet[4]})')
    
    conn.close()

if __name__ == "__main__":
    debug_session_packets()