import sqlite3

conn = sqlite3.connect('data/network_analyzer.db')
cursor = conn.cursor()

# 检查会话55的详细信息
cursor.execute('SELECT * FROM sessions WHERE id = 55')
session = cursor.fetchone()
print('会话55详情:', session)

if session:
    start_time, end_time = session[2], session[3]
    print(f'时间范围: {start_time} - {end_time}')
    
    # 检查该时间范围内的数据包
    if end_time:
        cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length, CASE WHEN raw_data IS NULL THEN 0 ELSE 1 END FROM packets WHERE timestamp >= ? AND timestamp <= ? ORDER BY id LIMIT 10', (start_time, end_time))
    else:
        cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length, CASE WHEN raw_data IS NULL THEN 0 ELSE 1 END FROM packets WHERE timestamp >= ? ORDER BY id LIMIT 10', (start_time,))
    
    packets = cursor.fetchall()
    print(f'时间范围内数据包数: {len(packets)}')
    for p in packets:
        has_raw = "有" if p[6] else "无"
        print(f'  ID {p[0]}: {p[2]} -> {p[3]} ({p[4]}) 原始数据: {has_raw}')

# 检查测试数据包1,2,3的状态
print("\n检查测试数据包1,2,3:")
for packet_id in [1, 2, 3]:
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length, CASE WHEN raw_data IS NULL THEN 0 ELSE 1 END FROM packets WHERE id = ?', (packet_id,))
    packet = cursor.fetchone()
    if packet:
        has_raw = "有" if packet[6] else "无"
        print(f'  数据包{packet_id}: {packet[2]} -> {packet[3]} ({packet[4]}) 原始数据: {has_raw}')
    else:
        print(f'  数据包{packet_id}: 不存在')

# 检查数据包4453-4456
print("\n检查数据包4453-4456:")
for packet_id in [4453, 4454, 4455, 4456]:
    cursor.execute('SELECT id, timestamp, src_ip, dst_ip, protocol, length, CASE WHEN raw_data IS NULL THEN 0 ELSE 1 END FROM packets WHERE id = ?', (packet_id,))
    packet = cursor.fetchone()
    if packet:
        has_raw = "有" if packet[6] else "无"
        print(f'  数据包{packet_id}: {packet[2]} -> {packet[3]} ({packet[4]}) 原始数据: {has_raw}')
    else:
        print(f'  数据包{packet_id}: 不存在')

conn.close()