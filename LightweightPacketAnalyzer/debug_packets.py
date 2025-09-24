#!/usr/bin/env python3
"""
调试脚本：检查数据库中数据包的详细信息
"""

import sqlite3
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_packets():
    """检查数据库中的数据包详细信息"""
    db_path = "data/network_analyzer.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查数据包表结构
        print("=== 数据包表结构 ===")
        cursor.execute("PRAGMA table_info(packets)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"列: {col[1]}, 类型: {col[2]}, 非空: {col[3]}, 默认值: {col[4]}, 主键: {col[5]}")
        
        print("\n=== 数据包详细信息 ===")
        cursor.execute("""
            SELECT id, timestamp, src_ip, dst_ip, protocol, length, 
                   session_id, raw_data IS NOT NULL as has_raw_data,
                   LENGTH(raw_data) as raw_data_length
            FROM packets 
            ORDER BY id
        """)
        
        packets = cursor.fetchall()
        print(f"总共找到 {len(packets)} 个数据包:")
        
        for packet in packets:
            print(f"\n数据包 ID: {packet[0]}")
            print(f"  时间戳: {packet[1]} (类型: {type(packet[1])})")
            print(f"  源IP: {packet[2]}")
            print(f"  目标IP: {packet[3]}")
            print(f"  协议: {packet[4]}")
            print(f"  长度: {packet[5]}")
            print(f"  会话ID: {packet[6]}")
            print(f"  有原始数据: {packet[7]}")
            print(f"  原始数据长度: {packet[8]}")
        
        # 检查会话信息
        print("\n=== 会话信息 ===")
        cursor.execute("SELECT id, name, created_at FROM sessions")
        sessions = cursor.fetchall()
        for session in sessions:
            print(f"会话 ID: {session[0]}, 名称: {session[1]}, 创建时间: {session[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据包失败: {e}")

if __name__ == "__main__":
    check_packets()