#!/usr/bin/env python3
"""
清理数据库中重复数据包的脚本
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

def clean_duplicate_packets():
    """清理数据库中的重复数据包"""
    
    # 获取数据库路径
    settings = Settings()
    db_path = settings.get_database_path()
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"连接到数据库: {db_path}")
    
    # 备份数据库
    backup_path = db_path + ".backup"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"数据库已备份到: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        # 统计清理前的数据包数量
        cursor.execute("SELECT COUNT(*) as total FROM packets")
        total_before = cursor.fetchone()['total']
        print(f"清理前总数据包数: {total_before}")
        
        # 查找重复数据包
        print("正在查找重复数据包...")
        duplicate_query = """
        SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count,
               GROUP_CONCAT(id) as ids
        FROM packets 
        GROUP BY timestamp, src_ip, dst_ip, protocol, length
        HAVING COUNT(*) > 1
        """
        
        cursor.execute(duplicate_query)
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("未发现重复数据包")
            conn.rollback()
            return
        
        print(f"发现 {len(duplicates)} 组重复数据包")
        
        total_deleted = 0
        
        # 对每组重复数据包，保留ID最小的一个，删除其他的
        for dup in duplicates:
            ids = [int(id_str) for id_str in dup['ids'].split(',')]
            ids.sort()
            
            # 保留第一个（ID最小的），删除其他的
            ids_to_delete = ids[1:]
            
            if ids_to_delete:
                placeholders = ','.join(['?'] * len(ids_to_delete))
                delete_query = f"DELETE FROM packets WHERE id IN ({placeholders})"
                cursor.execute(delete_query, ids_to_delete)
                
                deleted_count = len(ids_to_delete)
                total_deleted += deleted_count
                
                dt = datetime.fromtimestamp(float(dup['timestamp']))
                print(f"删除重复数据包: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} "
                      f"{dup['src_ip']} -> {dup['dst_ip']} {dup['protocol']} "
                      f"(删除 {deleted_count} 个重复项)")
        
        # 统计清理后的数据包数量
        cursor.execute("SELECT COUNT(*) as total FROM packets")
        total_after = cursor.fetchone()['total']
        
        print(f"\n清理完成:")
        print(f"  清理前: {total_before} 个数据包")
        print(f"  清理后: {total_after} 个数据包")
        print(f"  删除了: {total_deleted} 个重复数据包")
        
        # 提交事务
        conn.commit()
        print("数据库清理成功!")
        
    except Exception as e:
        print(f"清理过程中发生错误: {e}")
        conn.rollback()
        print("已回滚所有更改")
        
    finally:
        conn.close()

def verify_cleanup():
    """验证清理效果"""
    settings = Settings()
    db_path = settings.get_database_path()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 检查是否还有重复数据包
    duplicate_query = """
    SELECT timestamp, src_ip, dst_ip, protocol, length, COUNT(*) as count
    FROM packets 
    GROUP BY timestamp, src_ip, dst_ip, protocol, length
    HAVING COUNT(*) > 1
    LIMIT 5
    """
    
    cursor.execute(duplicate_query)
    remaining_duplicates = cursor.fetchall()
    
    if remaining_duplicates:
        print(f"\n警告: 仍有 {len(remaining_duplicates)} 组重复数据包:")
        for dup in remaining_duplicates:
            dt = datetime.fromtimestamp(float(dup['timestamp']))
            print(f"  {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} "
                  f"{dup['src_ip']} -> {dup['dst_ip']} {dup['protocol']} "
                  f"(重复 {dup['count']} 次)")
    else:
        print("\n✓ 验证通过: 未发现重复数据包")
    
    conn.close()

if __name__ == "__main__":
    print("=== 数据库重复数据包清理工具 ===")
    
    # 询问用户确认
    response = input("是否要清理数据库中的重复数据包? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        clean_duplicate_packets()
        verify_cleanup()
    else:
        print("操作已取消")