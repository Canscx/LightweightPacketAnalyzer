#!/usr/bin/env python3
"""
测试会话加载功能的脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager

def test_session_load():
    """测试会话加载功能"""
    
    # 初始化数据管理器
    data_manager = DataManager("data/network_analyzer.db")
    
    print("🔍 测试会话加载功能")
    print("=" * 50)
    
    # 获取所有会话
    sessions = data_manager.get_sessions()
    print(f"📊 总共有 {len(sessions)} 个会话")
    
    # 测试有数据包的会话
    test_sessions = []
    for session in sessions:
        if session.get('packet_count', 0) > 0:
            test_sessions.append(session)
    
    print(f"📦 有数据包的会话: {len(test_sessions)} 个")
    
    # 测试前3个有数据包的会话
    for i, session in enumerate(test_sessions[:3]):
        session_id = session['id']
        session_name = session['session_name']
        packet_count = session.get('packet_count', 0)
        
        print(f"\n🧪 测试会话 {session_id} ({session_name})")
        print(f"   预期数据包数: {packet_count}")
        
        # 调用get_packets_by_session
        packets = data_manager.get_packets_by_session(session_id)
        print(f"   实际获取数据包数: {len(packets)}")
        
        if len(packets) > 0:
            print("   ✅ 成功获取数据包")
            # 显示前3个数据包的信息
            for j, packet in enumerate(packets[:3]):
                timestamp = packet.get('timestamp', 'N/A')
                src_ip = packet.get('src_ip', 'N/A')
                dst_ip = packet.get('dst_ip', 'N/A')
                protocol = packet.get('protocol', 'N/A')
                print(f"     数据包 {j+1}: {src_ip} -> {dst_ip} ({protocol}) @ {timestamp}")
        else:
            print("   ❌ 未获取到数据包")
            
            # 调试：直接查询数据库
            print("   🔍 直接查询数据库:")
            import sqlite3
            conn = sqlite3.connect("data/network_analyzer.db")
            cursor = conn.cursor()
            
            # 获取会话时间范围
            cursor.execute("SELECT start_time, end_time FROM sessions WHERE id = ?", (session_id,))
            session_info = cursor.fetchone()
            if session_info:
                start_time, end_time = session_info
                print(f"     会话时间范围: {start_time} - {end_time}")
                
                # 查询该时间范围内的数据包
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
                
                direct_count = cursor.fetchone()[0]
                print(f"     直接查询结果: {direct_count} 个数据包")
                
                # 显示时间范围内的数据包样本
                if end_time:
                    cursor.execute("""
                        SELECT timestamp, src_ip, dst_ip, protocol FROM packets 
                        WHERE timestamp >= ? AND timestamp <= ?
                        LIMIT 3
                    """, (start_time, end_time))
                else:
                    cursor.execute("""
                        SELECT timestamp, src_ip, dst_ip, protocol FROM packets 
                        WHERE timestamp >= ?
                        LIMIT 3
                    """, (start_time,))
                
                sample_packets = cursor.fetchall()
                for k, packet in enumerate(sample_packets):
                    timestamp, src_ip, dst_ip, protocol = packet
                    print(f"       样本 {k+1}: {src_ip} -> {dst_ip} ({protocol}) @ {timestamp}")
            
            conn.close()

if __name__ == "__main__":
    test_session_load()