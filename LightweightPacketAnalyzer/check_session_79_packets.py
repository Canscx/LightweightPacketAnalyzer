#!/usr/bin/env python3
"""
检查会话79的数据包
"""

import sqlite3
import os

def check_session_79_packets():
    """检查会话79的数据包"""
    db_path = "network_analyzer.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 会话79数据包检查 ===\n")
        
        # 1. 检查所有会话的数据包分布
        print("1. 所有会话的数据包分布:")
        cursor.execute("""
            SELECT session_id, COUNT(*) as count 
            FROM packets 
            GROUP BY session_id 
            ORDER BY session_id DESC
        """)
        session_distribution = cursor.fetchall()
        
        for session_id, count in session_distribution:
            print(f"   会话{session_id}: {count}个数据包")
        
        # 2. 检查是否有session_id=79的数据包
        print(f"\n2. 检查session_id=79的数据包:")
        cursor.execute("SELECT COUNT(*) FROM packets WHERE session_id = 79")
        packet_count_79 = cursor.fetchone()[0]
        print(f"   session_id=79的数据包数量: {packet_count_79}")
        
        # 3. 检查是否有session_id为NULL的数据包
        print(f"\n3. 检查session_id为NULL的数据包:")
        cursor.execute("SELECT COUNT(*) FROM packets WHERE session_id IS NULL")
        packet_count_null = cursor.fetchone()[0]
        print(f"   session_id为NULL的数据包数量: {packet_count_null}")
        
        # 4. 显示所有数据包的session_id
        print(f"\n4. 所有数据包的session_id:")
        cursor.execute("SELECT id, session_id, timestamp, protocol FROM packets ORDER BY id")
        all_packets = cursor.fetchall()
        
        for packet in all_packets:
            print(f"   数据包ID={packet[0]}, session_id={packet[1]}, 时间={packet[2]}, 协议={packet[3]}")
        
        # 5. 检查sessions表中的所有记录
        print(f"\n5. sessions表中的所有记录:")
        cursor.execute("SELECT id, session_name, packet_count, total_bytes FROM sessions ORDER BY id DESC")
        all_sessions = cursor.fetchall()
        
        for session in all_sessions:
            print(f"   会话ID={session[0]}, 名称={session[1]}, 数据包数={session[2]}, 字节数={session[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_session_79_packets()