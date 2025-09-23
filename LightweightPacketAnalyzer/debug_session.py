#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from network_analyzer.config.settings import Settings

def debug_session():
    settings = Settings()
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    print('最新的会话:')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY id DESC LIMIT 1')
    session = cursor.fetchone()
    if session:
        print(f'ID: {session["id"]}, 名称: {session["session_name"]}, 开始: {session["start_time"]}, 结束: {session["end_time"]}, 包数: {session["packet_count"]}')
        
        print(f'\n该会话时间范围内的数据包:')
        cursor.execute('SELECT * FROM packets WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp', 
                       (session['start_time'], session['end_time'] or 999999999999))
        packets = cursor.fetchall()
        print(f'找到 {len(packets)} 个数据包')
        for p in packets[:10]:  # 显示前10个
            print(f'  {p["src_ip"]} -> {p["dst_ip"]} ({p["protocol"]}) - {p["length"]} 字节, 时间: {p["timestamp"]}')
    else:
        print('没有找到会话')

    conn.close()

if __name__ == "__main__":
    debug_session()