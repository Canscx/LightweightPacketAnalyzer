#!/usr/bin/env python3
"""
数据库调试脚本 - 检查数据包和会话数据
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def check_database():
    """检查数据库内容"""
    db_path = Path("data/network_analyzer.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    print(f"✅ 数据库文件存在: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查表结构
        print("\n📋 数据库表结构:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查会话数据
        print("\n📊 会话数据:")
        cursor.execute("SELECT id, session_name, start_time, end_time, packet_count, total_bytes FROM sessions")
        sessions = cursor.fetchall()
        
        if not sessions:
            print("  ❌ 没有会话数据")
        else:
            for session in sessions:
                session_id, session_name, start_time, end_time, packet_count, total_bytes = session
                start_dt = datetime.fromtimestamp(start_time) if start_time else None
                end_dt = datetime.fromtimestamp(end_time) if end_time else None
                print(f"  会话 {session_id}: {session_name}")
                print(f"    开始时间: {start_dt}")
                print(f"    结束时间: {end_dt}")
                print(f"    数据包数: {packet_count}")
                print(f"    总字节数: {total_bytes}")
        
        # 检查数据包数据
        print("\n📦 数据包数据:")
        cursor.execute("SELECT COUNT(*) FROM packets")
        packet_count = cursor.fetchone()[0]
        print(f"  总数据包数: {packet_count}")
        
        if packet_count > 0:
            cursor.execute("SELECT id, timestamp, src_ip, dst_ip, protocol, length FROM packets LIMIT 5")
            packets = cursor.fetchall()
            print("  前5个数据包:")
            for packet in packets:
                packet_id, timestamp, src_ip, dst_ip, protocol, length = packet
                timestamp_dt = datetime.fromtimestamp(timestamp) if timestamp else None
                print(f"    包 {packet_id}: {src_ip} -> {dst_ip} ({protocol}) {length}字节 @ {timestamp_dt}")
        
        # 检查数据包数据格式
        print("\n📦 数据包数据格式检查:")
        cursor.execute("SELECT timestamp, src_ip, dst_ip, protocol, length FROM packets LIMIT 5")
        packets = cursor.fetchall()
        if not packets:
            print("  ❌ 没有数据包数据")
        else:
            for i, packet in enumerate(packets):
                timestamp, src_ip, dst_ip, protocol, length = packet
                print(f"  数据包 {i+1}:")
                print(f"    timestamp: {timestamp} (类型: {type(timestamp)})")
                print(f"    src_ip: {src_ip}, dst_ip: {dst_ip}")
                print(f"    protocol: {protocol}, length: {length}")
                
                # 尝试解析timestamp
                try:
                    if isinstance(timestamp, (int, float)):
                        dt = datetime.fromtimestamp(timestamp)
                        print(f"    解析为时间: {dt}")
                    else:
                        print(f"    timestamp不是数字类型: {type(timestamp)}")
                except Exception as e:
                    print(f"    timestamp解析失败: {e}")
                print()

        # 检查时间范围匹配
        if sessions and packet_count > 0:
            print("\n🔍 时间范围匹配检查:")
            for session in sessions:
                session_id, session_name, start_time, end_time, _, _ = session
                if start_time and end_time:
                    cursor.execute("""
                        SELECT COUNT(*) FROM packets 
                        WHERE timestamp >= ? AND timestamp <= ?
                    """, (start_time, end_time))
                    matching_packets = cursor.fetchone()[0]
                    print(f"  会话 {session_id} ({session_name}): 时间范围内有 {matching_packets} 个数据包")
                else:
                    print(f"  会话 {session_id} ({session_name}): 时间范围不完整 (start: {start_time}, end: {end_time})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    check_database()