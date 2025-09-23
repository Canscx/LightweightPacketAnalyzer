#!/usr/bin/env python3
"""
会话问题详细调试脚本
分析为什么某些会话显示有数据包但实际查询不到
"""

import sqlite3
import sys
from datetime import datetime

def debug_session_issue():
    """调试会话问题"""
    db_path = "network_analyzer.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 分析会话问题")
        print("=" * 50)
        
        # 获取有问题的会话（packet_count > 0 但实际查询不到数据包）
        print("\n📋 查找有问题的会话...")
        cursor.execute("""
            SELECT id, session_name, start_time, end_time, packet_count, total_bytes
            FROM sessions 
            WHERE packet_count > 0
            ORDER BY id DESC
            LIMIT 10
        """)
        
        problem_sessions = []
        for row in cursor.fetchall():
            session_id, name, start_time, end_time, packet_count, total_bytes = row
            
            # 查询该会话时间范围内的实际数据包数
            if end_time:
                cursor.execute("""
                    SELECT COUNT(*) FROM packets 
                    WHERE timestamp >= ? AND timestamp <= ?
                """, (start_time, end_time))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM packets 
                    WHERE timestamp >= ?
                """, (start_time,))
            
            actual_count = cursor.fetchone()[0]
            
            print(f"\n🧪 会话 {session_id} ({name})")
            print(f"   记录的数据包数: {packet_count}")
            print(f"   实际数据包数: {actual_count}")
            print(f"   开始时间: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')}")
            print(f"   结束时间: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S.%f') if end_time else 'None'}")
            
            if packet_count != actual_count:
                problem_sessions.append({
                    'id': session_id,
                    'name': name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'recorded_count': packet_count,
                    'actual_count': actual_count
                })
                print(f"   ❌ 数据包数不匹配！")
                
                # 查找最接近的数据包时间戳
                cursor.execute("""
                    SELECT timestamp, src_ip, dst_ip, protocol 
                    FROM packets 
                    ORDER BY ABS(timestamp - ?) 
                    LIMIT 5
                """, (start_time,))
                
                closest_packets = cursor.fetchall()
                print(f"   🔍 最接近开始时间的数据包:")
                for i, (ts, src, dst, proto) in enumerate(closest_packets, 1):
                    time_diff = abs(ts - start_time)
                    print(f"      {i}. {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')} "
                          f"({src} -> {dst}, {proto}) 时间差: {time_diff:.6f}秒")
            else:
                print(f"   ✅ 数据包数匹配")
        
        print(f"\n📊 总结:")
        print(f"   有问题的会话数: {len(problem_sessions)}")
        
        if problem_sessions:
            print(f"\n🔧 建议修复方案:")
            print(f"   1. 重新计算会话的实际数据包数")
            print(f"   2. 调整会话的时间范围以包含相关数据包")
            print(f"   3. 清理无效的会话记录")
            
            # 提供修复选项
            print(f"\n❓ 是否要修复这些会话？(y/n): ", end="")
            choice = input().lower().strip()
            
            if choice == 'y':
                fix_sessions(cursor, conn, problem_sessions)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        return False
    
    return True

def fix_sessions(cursor, conn, problem_sessions):
    """修复有问题的会话"""
    print(f"\n🔧 开始修复会话...")
    
    for session in problem_sessions:
        session_id = session['id']
        start_time = session['start_time']
        end_time = session['end_time']
        
        print(f"\n修复会话 {session_id} ({session['name']})...")
        
        # 方案1: 重新计算该时间范围内的实际数据包数和字节数
        if end_time:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(length), 0)
                FROM packets 
                WHERE timestamp >= ? AND timestamp <= ?
            """, (start_time, end_time))
        else:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(length), 0)
                FROM packets 
                WHERE timestamp >= ?
            """, (start_time,))
        
        actual_count, actual_bytes = cursor.fetchone()
        
        # 更新会话记录
        cursor.execute("""
            UPDATE sessions 
            SET packet_count = ?, total_bytes = ?
            WHERE id = ?
        """, (actual_count, actual_bytes, session_id))
        
        print(f"   ✅ 已更新: 数据包数 {session['recorded_count']} -> {actual_count}, "
              f"字节数 -> {actual_bytes}")
    
    conn.commit()
    print(f"\n✅ 修复完成！")

if __name__ == "__main__":
    debug_session_issue()