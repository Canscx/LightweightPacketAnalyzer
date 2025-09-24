#!/usr/bin/env python3
"""
测试重复数据包修复效果的脚本
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
from network_analyzer.storage.data_manager import DataManager

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

def test_duplicate_fix():
    """测试重复数据包修复效果"""
    print("=== 测试重复数据包修复效果 ===\n")
    
    # 初始化设置和数据管理器
    settings = Settings()
    db_path = settings.get_database_path()
    
    print(f"数据库路径: {db_path}")
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print("数据库文件不存在，无法进行测试")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. 检查会话数量
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        session_count = cursor.fetchone()['count']
        print(f"1. 会话总数: {session_count}")
        
        # 2. 检查数据包总数
        cursor.execute("SELECT COUNT(*) as count FROM packets")
        packet_count = cursor.fetchone()['count']
        print(f"2. 数据包总数: {packet_count}")
        
        if session_count == 0:
            print("没有会话数据，无法进行重复检查")
            return
        
        # 3. 获取最近的会话
        cursor.execute("""
            SELECT id, session_name, start_time, end_time, packet_count 
            FROM sessions 
            ORDER BY start_time DESC 
            LIMIT 3
        """)
        recent_sessions = cursor.fetchall()
        
        print(f"\n3. 最近的 {len(recent_sessions)} 个会话:")
        for session in recent_sessions:
            print(f"   会话 {session['id']}: {session['session_name']} - {session['packet_count']} 包")
        
        # 4. 对每个会话检查重复数据包
        for session in recent_sessions:
            session_id = session['id']
            start_time = session['start_time']
            end_time = session['end_time']
            
            print(f"\n4. 检查会话 {session_id} 的重复数据包:")
            
            # 查询该会话时间范围内的数据包
            cursor.execute("""
                SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
                FROM packets 
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY timestamp, src_ip, dst_ip, protocol, length
                HAVING COUNT(*) > 1
                ORDER BY timestamp
            """, (start_time, end_time or 9999999999))
            
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"   发现 {len(duplicates)} 组重复数据包:")
                for dup in duplicates[:5]:  # 只显示前5个
                    print(f"     {dup['timestamp']:.6f} {dup['src_ip']} -> {dup['dst_ip']} "
                          f"{dup['protocol']} {dup['length']}字节 (重复{dup['count']}次)")
                if len(duplicates) > 5:
                    print(f"     ... 还有 {len(duplicates) - 5} 组重复数据包")
            else:
                print("   ✓ 没有发现重复数据包")
        
        # 5. 全局重复检查
        print(f"\n5. 全局重复数据包检查:")
        cursor.execute("""
            SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
            FROM packets 
            GROUP BY timestamp, src_ip, dst_ip, protocol, length
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        
        global_duplicates = cursor.fetchall()
        
        if global_duplicates:
            print(f"   发现 {len(global_duplicates)} 组全局重复数据包:")
            for dup in global_duplicates:
                timestamp = parse_timestamp(dup['timestamp'])
                print(f"     {timestamp:.6f} {dup['src_ip']} -> {dup['dst_ip']} "
                      f"{dup['protocol']} {dup['length']}字节 (重复{dup['count']}次)")
        else:
            print("   ✓ 没有发现全局重复数据包")
        
    except Exception as e:
        print(f"检查过程中发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_duplicate_fix()