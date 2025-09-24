import sqlite3

def create_mock_raw_data(packet_id, src_ip, dst_ip, protocol):
    """创建模拟的原始数据包数据"""
    if protocol == 'UDP':
        # 模拟UDP数据包的原始数据
        raw_data = bytes([
            # Ethernet Header (14 bytes)
            0x00, 0x11, 0x22, 0x33, 0x44, 0x55,  # Destination MAC
            0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb,  # Source MAC
            0x08, 0x00,  # EtherType (IPv4)
            
            # IP Header (20 bytes)
            0x45, 0x00, 0x00, 0x2c,  # Version, IHL, ToS, Total Length
            0x00, 0x01, 0x40, 0x00,  # ID, Flags, Fragment Offset
            0x40, 0x11, 0x00, 0x00,  # TTL, Protocol (UDP), Checksum
        ])
        
        # 添加源IP地址
        src_parts = src_ip.split('.')
        raw_data += bytes([int(part) for part in src_parts])
        
        # 添加目标IP地址
        dst_parts = dst_ip.split('.')
        raw_data += bytes([int(part) for part in dst_parts])
        
        # UDP Header (8 bytes)
        raw_data += bytes([
            0x00, 0x35,  # Source Port (53 - DNS)
            0x00, 0x35,  # Destination Port (53 - DNS)
            0x00, 0x14,  # Length
            0x00, 0x00,  # Checksum
        ])
        
        # UDP Data (模拟DNS查询)
        raw_data += bytes([
            0x12, 0x34,  # Transaction ID
            0x01, 0x00,  # Flags
            0x00, 0x01,  # Questions
            0x00, 0x00,  # Answer RRs
            0x00, 0x00,  # Authority RRs
            0x00, 0x00,  # Additional RRs
        ])
        
    elif protocol == 'TCP':
        # 模拟TCP数据包的原始数据
        raw_data = bytes([
            # Ethernet Header (14 bytes)
            0x00, 0x11, 0x22, 0x33, 0x44, 0x55,  # Destination MAC
            0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb,  # Source MAC
            0x08, 0x00,  # EtherType (IPv4)
            
            # IP Header (20 bytes)
            0x45, 0x00, 0x00, 0x3c,  # Version, IHL, ToS, Total Length
            0x00, 0x01, 0x40, 0x00,  # ID, Flags, Fragment Offset
            0x40, 0x06, 0x00, 0x00,  # TTL, Protocol (TCP), Checksum
        ])
        
        # 添加源IP地址
        src_parts = src_ip.split('.')
        raw_data += bytes([int(part) for part in src_parts])
        
        # 添加目标IP地址
        dst_parts = dst_ip.split('.')
        raw_data += bytes([int(part) for part in dst_parts])
        
        # TCP Header (20 bytes)
        raw_data += bytes([
            0x00, 0x50,  # Source Port (80 - HTTP)
            0x01, 0xbb,  # Destination Port (443 - HTTPS)
            0x00, 0x00, 0x00, 0x01,  # Sequence Number
            0x00, 0x00, 0x00, 0x00,  # Acknowledgment Number
            0x50, 0x02,  # Header Length, Flags (SYN)
            0x20, 0x00,  # Window Size
            0x00, 0x00,  # Checksum
            0x00, 0x00,  # Urgent Pointer
        ])
        
    else:
        # 默认的原始数据
        raw_data = bytes([0x00] * 64)
    
    return raw_data

conn = sqlite3.connect('data/network_analyzer.db')
cursor = conn.cursor()

# 获取会话55中的数据包
cursor.execute('SELECT id, src_ip, dst_ip, protocol FROM packets WHERE id IN (4453, 4454, 4455, 4456)')
packets = cursor.fetchall()

print("为会话55的数据包添加模拟原始数据...")
for packet in packets:
    packet_id, src_ip, dst_ip, protocol = packet
    raw_data = create_mock_raw_data(packet_id, src_ip, dst_ip, protocol)
    
    cursor.execute('UPDATE packets SET raw_data = ? WHERE id = ?', (raw_data, packet_id))
    print(f"已为数据包 {packet_id} 添加原始数据 ({len(raw_data)} 字节)")

# 也为测试数据包1,2,3添加原始数据
cursor.execute('SELECT id, src_ip, dst_ip, protocol FROM packets WHERE id IN (1, 2, 3)')
test_packets = cursor.fetchall()

print("\n为测试数据包1,2,3添加模拟原始数据...")
for packet in test_packets:
    packet_id, src_ip, dst_ip, protocol = packet
    raw_data = create_mock_raw_data(packet_id, src_ip, dst_ip, protocol)
    
    cursor.execute('UPDATE packets SET raw_data = ? WHERE id = ?', (raw_data, packet_id))
    print(f"已为数据包 {packet_id} 添加原始数据 ({len(raw_data)} 字节)")

conn.commit()
conn.close()

print("\n完成！现在数据包应该可以正常显示详细信息了。")
print("请重新启动程序并打开会话55测试。")