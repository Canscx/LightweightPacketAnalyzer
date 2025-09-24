#!/usr/bin/env python3
"""
调试会话79的数据包保存/加载问题
"""

import sqlite3
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_session_79():
    """检查会话79的数据库状态"""
    db_path = "network_analyzer.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 会话79数据库状态检查 ===\n")
        
        # 1. 检查sessions表中的会话79记录
        print("1. 检查sessions表中的会话79记录:")
        cursor.execute("""
            SELECT id, name, packet_count, total_bytes, created_at, updated_at 
            FROM sessions 
            WHERE id = 79
        """)
        session_record = cursor.fetchone()
        
        if session_record:
            print(f"   会话ID: {session_record[0]}")
            print(f"   会话名称: {session_record[1]}")
            print(f"   数据包数量: {session_record[2]}")
            print(f"   总字节数: {session_record[3]}")
            print(f"   创建时间: {session_record[4]}")
            print(f"   更新时间: {session_record[5]}")
        else:
            print("   ❌ 未找到会话79的记录")
            return
        
        print()
        
        # 2. 检查packets表中session_id=79的数据包数量
        print("2. 检查packets表中session_id=79的数据包:")
        cursor.execute("SELECT COUNT(*) FROM packets WHERE session_id = 79")
        packet_count = cursor.fetchone()[0]
        print(f"   实际数据包数量: {packet_count}")
        
        # 3. 检查packets表结构
        print("\n3. 检查packets表结构:")
        cursor.execute("PRAGMA table_info(packets)")
        columns = cursor.fetchall()
        print("   表字段:")
        for col in columns:
            print(f"     - {col[1]} ({col[2]})")
        
        # 4. 如果有数据包，显示前几条记录的基本信息
        if packet_count > 0:
            print(f"\n4. 显示前5条数据包记录:")
            cursor.execute("""
                SELECT id, timestamp, src_ip, dst_ip, protocol, length, session_id
                FROM packets 
                WHERE session_id = 79 
                ORDER BY timestamp 
                LIMIT 5
            """)
            packets = cursor.fetchall()
            
            for i, packet in enumerate(packets, 1):
                print(f"   数据包{i}: ID={packet[0]}, 时间={packet[1]}, "
                      f"源IP={packet[2]}, 目标IP={packet[3]}, "
                      f"协议={packet[4]}, 长度={packet[5]}, 会话ID={packet[6]}")
        
        # 5. 检查是否有其他会话的数据包
        print(f"\n5. 检查所有会话的数据包分布:")
        cursor.execute("""
            SELECT session_id, COUNT(*) as count 
            FROM packets 
            GROUP BY session_id 
            ORDER BY session_id DESC 
            LIMIT 10
        """)
        session_distribution = cursor.fetchall()
        
        for session_id, count in session_distribution:
            print(f"   会话{session_id}: {count}个数据包")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    check_session_79()