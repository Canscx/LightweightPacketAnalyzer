#!/usr/bin/env python3
"""
检查数据库表结构
"""

import sqlite3

def check_database():
    """检查数据库表结构"""
    db_path = "network_analyzer.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"数据库中的表: {tables}")
        
        # 如果有表，显示每个表的结构
        for table in tables:
            print(f"\n表 '{table}' 的结构:")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # 显示表中的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  记录数: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")

if __name__ == "__main__":
    check_database()