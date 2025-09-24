#!/usr/bin/env python3
"""
调试GUI重复显示问题的脚本
检查_load_session_data和相关方法的调用情况
"""

import sys
import os
import sqlite3
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.config.settings import Settings

def debug_duplicate_gui_issue():
    """调试GUI重复显示问题"""
    
    # 设置日志
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("=== 调试GUI重复显示问题 ===")
    
    try:
        # 初始化设置和数据管理器
        settings = Settings()
        data_manager = DataManager(settings.get_database_path())
        
        # 检查数据库中的会话和数据包
        print("\n1. 检查数据库内容:")
        sessions = data_manager.get_sessions()
        print(f"   会话总数: {len(sessions)}")
        
        if not sessions:
            print("   数据库中没有会话，无法测试重复显示问题")
            return
        
        # 选择最新的会话进行测试
        latest_session = sessions[0]  # 按创建时间倒序排列
        session_id = latest_session['id']
        session_name = latest_session.get('session_name', '未知')
        
        print(f"   测试会话: ID={session_id}, 名称='{session_name}'")
        
        # 检查get_packets_by_session的返回结果
        print(f"\n2. 检查get_packets_by_session({session_id})的返回结果:")
        packets = data_manager.get_packets_by_session(session_id)
        print(f"   返回的数据包数量: {len(packets)}")
        
        if len(packets) == 0:
            print("   该会话没有数据包")
            return
        
        # 检查是否有重复的数据包
        print("\n3. 检查数据包是否重复:")
        packet_signatures = []
        duplicates = []
        
        for i, packet in enumerate(packets):
            # 创建数据包签名（时间戳+源IP+目标IP+协议+长度）
            signature = (
                packet.get('timestamp', 0),
                packet.get('src_ip', ''),
                packet.get('dst_ip', ''),
                packet.get('protocol', ''),
                packet.get('length', 0)
            )
            
            if signature in packet_signatures:
                duplicates.append((i, packet))
                print(f"   发现重复数据包 #{i}: {signature}")
            else:
                packet_signatures.append(signature)
        
        if duplicates:
            print(f"   总共发现 {len(duplicates)} 个重复数据包")
        else:
            print("   没有发现重复的数据包")
        
        # 显示前5个数据包的详细信息
        print(f"\n4. 前5个数据包的详细信息:")
        for i, packet in enumerate(packets[:5]):
            timestamp = packet.get('timestamp', 0)
            if timestamp:
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]
            else:
                time_str = "未知时间"
            
            print(f"   #{i+1}: {time_str} | {packet.get('src_ip', 'N/A')} -> {packet.get('dst_ip', 'N/A')} | {packet.get('protocol', 'N/A')} | {packet.get('length', 0)} bytes")
        
        # 直接查询数据库检查是否有重复记录
        print(f"\n5. 直接查询数据库检查重复记录:")
        db_path = settings.get_database_path()
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询该会话时间范围内的数据包
            start_time = latest_session.get('start_time', 0)
            end_time = latest_session.get('end_time', 0)
            
            if end_time == 0:
                # 如果会话还没结束，使用当前时间
                end_time = datetime.now().timestamp()
            
            query = """
            SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
            FROM packets 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY timestamp, src_ip, dst_ip, protocol, length
            HAVING COUNT(*) > 1
            ORDER BY timestamp
            """
            
            cursor.execute(query, (start_time, end_time))
            db_duplicates = cursor.fetchall()
            
            if db_duplicates:
                print(f"   数据库中发现 {len(db_duplicates)} 组重复记录:")
                for dup in db_duplicates:
                    time_str = datetime.fromtimestamp(dup['timestamp']).strftime('%H:%M:%S.%f')[:-3]
                    print(f"     {time_str} | {dup['src_ip']} -> {dup['dst_ip']} | {dup['protocol']} | 重复{dup['count']}次")
            else:
                print("   数据库中没有发现重复记录")
        
        print(f"\n=== 调试完成 ===")
        
        # 总结
        print(f"\n总结:")
        print(f"- 会话ID: {session_id}")
        print(f"- 数据包总数: {len(packets)}")
        print(f"- get_packets_by_session返回的重复数据包: {len(duplicates)}")
        print(f"- 数据库中的重复记录组: {len(db_duplicates) if 'db_duplicates' in locals() else 0}")
        
        if len(duplicates) == 0 and (not 'db_duplicates' in locals() or len(db_duplicates) == 0):
            print("\n结论: 数据层面没有重复，问题可能在GUI显示逻辑中")
        else:
            print("\n结论: 发现了数据重复问题")
        
    except Exception as e:
        logger.error(f"调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_duplicate_gui_issue()