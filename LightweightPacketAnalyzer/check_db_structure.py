#!/usr/bin/env python3
"""
检查数据库表结构
"""

import sqlite3
import os

def check_database_structure():
    """检查数据库表结构"""
    db_path = "network_analyzer.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 数据库表结构检查 ===\n")
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"\n📋 表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   字段:")
            for col in columns:
                print(f"     - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
            
            # 获取记录数量
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   记录数量: {count}")
            
            # 如果是sessions表，显示所有记录
            if table_name == 'sessions':
                print("   所有会话记录:")
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 10")
                records = cursor.fetchall()
                for record in records:
                    print(f"     {record}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    check_database_structure()