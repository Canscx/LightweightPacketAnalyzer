#!/usr/bin/env python3
"""
测试脚本：插入模拟数据包到数据库
用于测试数据包详情显示功能
"""

import sqlite3
import os
from datetime import datetime
import struct

def create_test_packets():
    """创建测试数据包"""
    
    # 模拟以太网帧数据 (Ethernet + IP + TCP)
    # 以太网头部 (14字节)
    eth_dst = b'\x00\x11\x22\x33\x44\x55'  # 目标MAC
    eth_src = b'\x66\x77\x88\x99\xaa\xbb'  # 源MAC  
    eth_type = b'\x08\x00'  # IPv4
    
    # IP头部 (20字节)
    ip_version_ihl = b'\x45'  # IPv4, 头部长度20字节
    ip_tos = b'\x00'  # 服务类型
    ip_len = b'\x00\x28'  # 总长度40字节
    ip_id = b'\x12\x34'  # 标识
    ip_flags_frag = b'\x40\x00'  # 不分片
    ip_ttl = b'\x40'  # TTL=64
    ip_proto = b'\x06'  # TCP
    ip_checksum = b'\x00\x00'  # 校验和(简化)
    ip_src = b'\xc0\xa8\x01\x64'  # 192.168.1.100
    ip_dst = b'\xc0\xa8\x01\x01'  # 192.168.1.1
    
    # TCP头部 (20字节)
    tcp_src_port = b'\x04\xd2'  # 1234
    tcp_dst_port = b'\x00\x50'  # 80 (HTTP)
    tcp_seq = b'\x00\x00\x00\x01'  # 序列号
    tcp_ack = b'\x00\x00\x00\x00'  # 确认号
    tcp_flags = b'\x50\x02'  # 头部长度20字节, SYN标志
    tcp_window = b'\x20\x00'  # 窗口大小
    tcp_checksum = b'\x00\x00'  # 校验和(简化)
    tcp_urgent = b'\x00\x00'  # 紧急指针
    
    packet1 = eth_dst + eth_src + eth_type + ip_version_ihl + ip_tos + ip_len + ip_id + ip_flags_frag + ip_ttl + ip_proto + ip_checksum + ip_src + ip_dst + tcp_src_port + tcp_dst_port + tcp_seq + tcp_ack + tcp_flags + tcp_window + tcp_checksum + tcp_urgent
    
    # 创建第二个数据包 (UDP)
    ip_proto2 = b'\x11'  # UDP
    ip_dst2 = b'\x08\x08\x08\x08'  # 8.8.8.8
    
    # UDP头部 (8字节)
    udp_src_port = b'\x04\xd2'  # 1234
    udp_dst_port = b'\x00\x35'  # 53 (DNS)
    udp_len = b'\x00\x08'  # UDP长度8字节
    udp_checksum = b'\x00\x00'  # 校验和(简化)
    
    packet2 = eth_dst + eth_src + eth_type + ip_version_ihl + ip_tos + b'\x00\x22' + ip_id + ip_flags_frag + ip_ttl + ip_proto2 + ip_checksum + ip_src + ip_dst2 + udp_src_port + udp_dst_port + udp_len + udp_checksum
    
    # 创建第三个数据包 (ICMP)
    ip_proto3 = b'\x01'  # ICMP
    
    # ICMP头部 (8字节)
    icmp_type = b'\x08'  # Echo Request
    icmp_code = b'\x00'  # Code 0
    icmp_checksum = b'\x00\x00'  # 校验和(简化)
    icmp_id = b'\x12\x34'  # ID
    icmp_seq = b'\x00\x01'  # 序列号
    
    packet3 = eth_dst + eth_src + eth_type + ip_version_ihl + ip_tos + b'\x00\x22' + ip_id + ip_flags_frag + ip_ttl + ip_proto3 + ip_checksum + ip_src + ip_dst + icmp_type + icmp_code + icmp_checksum + icmp_id + icmp_seq
    
    return [
        {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1',
            'src_port': 1234,
            'dst_port': 80,
            'protocol': 'TCP',
            'length': len(packet1),
            'raw_data': packet1
        },
        {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'src_port': 1234,
            'dst_port': 53,
            'protocol': 'UDP',
            'length': len(packet2),
            'raw_data': packet2
        },
        {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1',
            'src_port': None,
            'dst_port': None,
            'protocol': 'ICMP',
            'length': len(packet3),
            'raw_data': packet3
        }
    ]

def insert_test_data():
    """插入测试数据到数据库"""
    
    db_path = 'data/network_analyzer.db'
    
    # 确保数据目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            packet_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT NOT NULL,
            src_ip TEXT,
            dst_ip TEXT,
            src_port INTEGER,
            dst_port INTEGER,
            protocol TEXT,
            length INTEGER,
            raw_data BLOB,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    # 创建测试会话
    cursor.execute('''
        INSERT INTO sessions (name, start_time, packet_count)
        VALUES (?, ?, ?)
    ''', ('测试会话', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 3))
    
    session_id = cursor.lastrowid
    
    # 插入测试数据包
    test_packets = create_test_packets()
    
    for packet in test_packets:
        cursor.execute('''
            INSERT INTO packets (session_id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            packet['timestamp'],
            packet['src_ip'],
            packet['dst_ip'],
            packet['src_port'],
            packet['dst_port'],
            packet['protocol'],
            packet['length'],
            packet['raw_data']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"成功插入 {len(test_packets)} 个测试数据包到数据库")
    print(f"会话ID: {session_id}")

if __name__ == '__main__':
    insert_test_data()