#!/usr/bin/env python3
"""
检查最新捕获的数据包是否包含raw_data
"""

import sqlite3
import os

def check_latest_packets():
    """检查最新的数据包是否包含raw_data"""
    db_path = "network_analyzer.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最新的10个数据包
        cursor.execute("""
            SELECT id, timestamp, protocol, src_ip, dst_ip, 
                   CASE 
                       WHEN raw_data IS NULL THEN 'NULL'
                       WHEN raw_data = '' THEN 'EMPTY'
                       ELSE 'HAS_DATA (' || LENGTH(raw_data) || ' bytes)'
                   END as raw_data_status
            FROM packets 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        packets = cursor.fetchall()
        
        if not packets:
            print("❌ 数据库中没有数据包")
            return
        
        print("🔍 最新10个数据包的raw_data状态:")
        print("-" * 80)
        print(f"{'ID':<6} {'时间戳':<20} {'协议':<8} {'源IP':<15} {'目标IP':<15} {'Raw Data状态'}")
        print("-" * 80)
        
        has_raw_data_count = 0
        for packet in packets:
            packet_id, timestamp, protocol, src_ip, dst_ip, raw_data_status = packet
            print(f"{packet_id:<6} {timestamp:<20} {protocol:<8} {src_ip:<15} {dst_ip:<15} {raw_data_status}")
            
            if 'HAS_DATA' in raw_data_status:
                has_raw_data_count += 1
        
        print("-" * 80)
        print(f"📊 统计结果:")
        print(f"   总数据包: {len(packets)}")
        print(f"   包含raw_data: {has_raw_data_count}")
        print(f"   缺少raw_data: {len(packets) - has_raw_data_count}")
        
        if has_raw_data_count == 0:
            print("\n❌ 所有最新数据包都缺少raw_data!")
            print("   这说明修复的代码没有生效，需要检查:")
            print("   1. 程序是否重新启动")
            print("   2. 代码修改是否正确")
            print("   3. 是否有其他错误")
        elif has_raw_data_count == len(packets):
            print("\n✅ 所有最新数据包都包含raw_data!")
            print("   问题可能在GUI显示逻辑上")
        else:
            print(f"\n⚠️  部分数据包包含raw_data ({has_raw_data_count}/{len(packets)})")
            print("   可能存在间歇性问题")
        
        # 检查最新的一个包的详细信息
        if packets:
            latest_id = packets[0][0]
            cursor.execute("SELECT raw_data FROM packets WHERE id = ?", (latest_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                raw_data = result[0]
                print(f"\n🔍 最新数据包 (ID: {latest_id}) 的raw_data详情:")
                if isinstance(raw_data, str):
                    print(f"   类型: 字符串, 长度: {len(raw_data)}")
                    print(f"   前20字符: {repr(raw_data[:20])}")
                elif isinstance(raw_data, bytes):
                    print(f"   类型: 字节, 长度: {len(raw_data)}")
                    print(f"   前20字节: {raw_data[:20].hex()}")
                else:
                    print(f"   类型: {type(raw_data)}, 值: {repr(raw_data)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

if __name__ == "__main__":
    check_latest_packets()