#!/usr/bin/env python3
"""
检查数据库中所有数据包和会话信息
"""

import sqlite3
import os

def check_all_data():
    """检查数据库中的所有数据"""
    db_path = "network_analyzer.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查会话表
        print("🔍 检查会话表:")
        cursor.execute("SELECT id, session_name, created_at FROM sessions ORDER BY id DESC")
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"   找到 {len(sessions)} 个会话:")
            for session in sessions:
                print(f"   - 会话ID: {session[0]}, 名称: {session[1]}, 创建时间: {session[2]}")
        else:
            print("   没有找到会话")
        
        # 检查数据包表
        print("\n🔍 检查数据包表:")
        cursor.execute("SELECT COUNT(*) FROM packets")
        total_packets = cursor.fetchone()[0]
        print(f"   总数据包数量: {total_packets}")
        
        if total_packets > 0:
            # 按会话分组统计
            cursor.execute("""
                SELECT p.session_id, COUNT(*) as packet_count,
                       MIN(p.id) as min_id, MAX(p.id) as max_id
                FROM packets p
                GROUP BY p.session_id 
                ORDER BY p.session_id DESC
            """)
            session_stats = cursor.fetchall()
            
            print("\n📊 按会话统计数据包:")
            for stat in session_stats:
                session_id, count, min_id, max_id = stat
                if session_id:
                    print(f"   会话 {session_id}: {count} 个数据包 (ID: {min_id}-{max_id})")
                else:
                    print(f"   无会话: {count} 个数据包 (ID: {min_id}-{max_id})")
            
            # 显示最新的20个数据包
            print("\n🔍 最新20个数据包:")
            cursor.execute("""
                SELECT id, session_id, timestamp, protocol, src_ip, dst_ip,
                       CASE 
                           WHEN raw_data IS NULL THEN 'NULL'
                           WHEN raw_data = '' THEN 'EMPTY'
                           ELSE 'HAS_DATA (' || LENGTH(raw_data) || ' bytes)'
                       END as raw_data_status
                FROM packets 
                ORDER BY id DESC 
                LIMIT 20
            """)
            
            packets = cursor.fetchall()
            print("-" * 90)
            print(f"{'ID':<6} {'会话':<6} {'时间戳':<20} {'协议':<8} {'源IP':<15} {'目标IP':<15} {'Raw Data'}")
            print("-" * 90)
            
            for packet in packets:
                packet_id, session_id, timestamp, protocol, src_ip, dst_ip, raw_data_status = packet
                print(f"{packet_id:<6} {session_id:<6} {timestamp:<20} {protocol:<8} {src_ip:<15} {dst_ip:<15} {raw_data_status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

if __name__ == "__main__":
    check_all_data()