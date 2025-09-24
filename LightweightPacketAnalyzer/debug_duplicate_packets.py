#!/usr/bin/env python3
"""
调试数据包重复显示问题
"""

import sqlite3
from datetime import datetime

def debug_duplicate_packets():
    """调试数据包重复问题"""
    
    try:
        # 连接数据库
        conn = sqlite3.connect('network_analyzer.db')
        conn.row_factory = sqlite3.Row  # 使用字典式访问
        cursor = conn.cursor()
        
        print('🔍 检查数据包重复问题')
        print('=' * 50)
        
        # 1. 检查会话表
        cursor.execute('SELECT COUNT(*) FROM sessions')
        session_count = cursor.fetchone()[0]
        print(f'📊 总会话数: {session_count}')
        
        # 2. 检查数据包表
        cursor.execute('SELECT COUNT(*) FROM packets')
        packet_count = cursor.fetchone()[0]
        print(f'📦 总数据包数: {packet_count}')
        
        if session_count == 0:
            print('❌ 没有找到任何会话')
            return
            
        if packet_count == 0:
            print('❌ 没有找到任何数据包')
            return
        
        # 3. 获取最近的会话
        cursor.execute('''
            SELECT id, session_name, start_time, end_time, packet_count, total_bytes
            FROM sessions 
            ORDER BY id DESC 
            LIMIT 3
        ''')
        sessions = cursor.fetchall()
        
        for session in sessions:
            session_id = session['id']
            name = session['session_name']
            start_time = session['start_time']
            end_time = session['end_time']
            expected_count = session['packet_count'] or 0
            
            print(f'\n📋 会话 {session_id} ({name})')
            print(f'   时间范围: {start_time} - {end_time}')
            print(f'   预期数据包数: {expected_count}')
            
            # 4. 查询该会话时间范围内的数据包
            if end_time:
                cursor.execute('''
                    SELECT * FROM packets 
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp
                ''', (start_time, end_time))
            else:
                cursor.execute('''
                    SELECT * FROM packets 
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                ''', (start_time,))
            
            packets = cursor.fetchall()
            actual_count = len(packets)
            print(f'   实际查询到数据包数: {actual_count}')
            
            if actual_count == 0:
                print('   ❌ 没有查询到数据包')
                continue
            
            # 5. 检查是否有重复的数据包
            seen_packets = set()
            duplicates = []
            
            for packet in packets:
                # 创建数据包的唯一标识
                packet_key = (
                    packet['timestamp'],
                    packet['src_ip'],
                    packet['dst_ip'],
                    packet['protocol'],
                    packet['length']
                )
                
                if packet_key in seen_packets:
                    duplicates.append(packet)
                else:
                    seen_packets.add(packet_key)
            
            if duplicates:
                print(f'   ❌ 发现 {len(duplicates)} 个重复数据包:')
                for i, dup in enumerate(duplicates[:5]):  # 只显示前5个
                    print(f'     {i+1}. {dup["timestamp"]}: {dup["src_ip"]}->{dup["dst_ip"]} ({dup["protocol"]})')
            else:
                print('   ✅ 没有发现重复数据包')
            
            # 6. 显示前几个数据包的详细信息
            print(f'   📝 前3个数据包:')
            for i, packet in enumerate(packets[:3]):
                print(f'     {i+1}. ID:{packet["id"]} {packet["timestamp"]}: {packet["src_ip"]}->{packet["dst_ip"]} ({packet["protocol"]})')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ 调试过程中发生错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_duplicate_packets()