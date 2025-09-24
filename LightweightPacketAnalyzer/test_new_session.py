#!/usr/bin/env python3
"""
测试新会话中数据包重复情况的脚本
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from network_analyzer.config.settings import Settings

def parse_timestamp(timestamp_value):
    """解析不同格式的时间戳"""
    if isinstance(timestamp_value, (int, float)):
        return float(timestamp_value)
    elif isinstance(timestamp_value, str):
        try:
            # 尝试直接转换为浮点数
            return float(timestamp_value)
        except ValueError:
            try:
                # 尝试解析日期时间字符串
                dt = datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S.%f')
                return dt.timestamp()
            except ValueError:
                try:
                    # 尝试其他格式
                    dt = datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S')
                    return dt.timestamp()
                except ValueError:
                    print(f"无法解析时间戳格式: {timestamp_value}")
                    return 0.0
    else:
        return 0.0

def test_latest_session():
    """测试最新会话中的数据包重复情况"""
    
    # 获取数据库路径
    settings = Settings()
    db_path = settings.get_database_path()
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"连接到数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 获取最新的会话
        cursor.execute("""
            SELECT id, session_name, start_time, end_time, packet_count
            FROM sessions 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        recent_sessions = cursor.fetchall()
        
        if not recent_sessions:
            print("数据库中没有会话记录")
            return
        
        print("=== 最近的会话 ===")
        for i, session in enumerate(recent_sessions, 1):
            start_dt = datetime.fromtimestamp(float(session['start_time']))
            end_time = session['end_time']
            if end_time:
                end_dt = datetime.fromtimestamp(float(end_time))
                duration = f"{end_dt.strftime('%H:%M:%S')} (持续 {float(end_time) - float(session['start_time']):.1f}秒)"
            else:
                duration = "进行中"
            
            print(f"{i}. 会话 {session['id']}: {session['session_name']}")
            print(f"   开始时间: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   结束时间: {duration}")
            print(f"   数据包数: {session['packet_count']}")
        
        # 选择最新的会话进行详细检查
        latest_session = recent_sessions[0]
        session_id = latest_session['id']
        
        print(f"\n=== 检查最新会话 {session_id} 的重复数据包 ===")
        
        # 获取该会话的时间范围
        start_time = float(latest_session['start_time'])
        end_time = float(latest_session['end_time']) if latest_session['end_time'] else float('inf')
        
        # 查找该时间范围内的重复数据包
        if end_time == float('inf'):
            # 会话还在进行中，查找开始时间之后的所有数据包
            duplicate_query = """
            SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
            FROM packets 
            WHERE timestamp >= ?
            GROUP BY timestamp, src_ip, dst_ip, protocol, length
            HAVING COUNT(*) > 1
            ORDER BY timestamp DESC
            """
            cursor.execute(duplicate_query, (start_time,))
        else:
            # 会话已结束，查找时间范围内的重复数据包
            duplicate_query = """
            SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
            FROM packets 
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY timestamp, src_ip, dst_ip, protocol, length
            HAVING COUNT(*) > 1
            ORDER BY timestamp DESC
            """
            cursor.execute(duplicate_query, (start_time, end_time))
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"❌ 发现 {len(duplicates)} 组重复数据包:")
            for i, dup in enumerate(duplicates, 1):
                timestamp = parse_timestamp(dup['timestamp'])
                dt = datetime.fromtimestamp(timestamp)
                print(f"  {i}. 时间: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                print(f"     {dup['src_ip']} -> {dup['dst_ip']} {dup['protocol']} {dup['length']}字节")
                print(f"     重复次数: {dup['count']}")
            
            print(f"\n❌ 测试失败: 最新会话中仍有重复数据包")
            return False
        else:
            print("✅ 未发现重复数据包")
            
            # 统计该会话的总数据包数
            if end_time == float('inf'):
                cursor.execute("SELECT COUNT(*) as total FROM packets WHERE timestamp >= ?", (start_time,))
            else:
                cursor.execute("SELECT COUNT(*) as total FROM packets WHERE timestamp >= ? AND timestamp <= ?", 
                             (start_time, end_time))
            
            total_packets = cursor.fetchone()['total']
            print(f"✅ 会话中共有 {total_packets} 个数据包，全部唯一")
            print(f"✅ 测试通过: 修复生效，不再产生重复数据包")
            return True
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False
        
    finally:
        conn.close()

def compare_with_old_sessions():
    """与旧会话进行对比"""
    settings = Settings()
    db_path = settings.get_database_path()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("\n=== 与历史会话对比 ===")
        
        # 检查几个历史会话的重复情况
        cursor.execute("""
            SELECT id, session_name, start_time, end_time
            FROM sessions 
            WHERE id <= 42
            ORDER BY id DESC 
            LIMIT 3
        """)
        
        old_sessions = cursor.fetchall()
        
        for session in old_sessions:
            session_id = session['id']
            start_time = float(session['start_time'])
            end_time = float(session['end_time']) if session['end_time'] else float('inf')
            
            if end_time == float('inf'):
                cursor.execute("""
                    SELECT COUNT(*) as duplicate_groups
                    FROM (
                        SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
                        FROM packets 
                        WHERE timestamp >= ?
                        GROUP BY timestamp, src_ip, dst_ip, protocol, length
                        HAVING COUNT(*) > 1
                    )
                """, (start_time,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as duplicate_groups
                    FROM (
                        SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
                        FROM packets 
                        WHERE timestamp >= ? AND timestamp <= ?
                        GROUP BY timestamp, src_ip, dst_ip, protocol, length
                        HAVING COUNT(*) > 1
                    )
                """, (start_time, end_time))
            
            duplicate_groups = cursor.fetchone()['duplicate_groups']
            
            start_dt = datetime.fromtimestamp(start_time)
            print(f"会话 {session_id} ({start_dt.strftime('%Y-%m-%d %H:%M:%S')}): {duplicate_groups} 组重复数据包")
    
    except Exception as e:
        print(f"对比过程中发生错误: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== 新会话数据包重复测试 ===")
    
    success = test_latest_session()
    compare_with_old_sessions()
    
    if success:
        print("\n🎉 恭喜! 重复数据包问题已修复")
    else:
        print("\n⚠️  仍需进一步调查重复数据包问题")