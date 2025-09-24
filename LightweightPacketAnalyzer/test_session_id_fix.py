#!/usr/bin/env python3
"""
测试session_id修复效果的脚本
验证新捕获的数据包能正确关联到会话并显示详情
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.processing.data_processor import DataProcessor
from network_analyzer.config.settings import Settings

def test_session_id_functionality():
    """测试session_id功能"""
    print("=" * 60)
    print("测试session_id修复效果")
    print("=" * 60)
    
    # 初始化组件
    settings = Settings()
    data_manager = DataManager(settings.get_database_path())
    data_processor = DataProcessor(settings, data_manager)
    
    # 1. 创建新会话
    print("\n1. 创建新会话...")
    session_id = data_manager.create_session("测试会话_session_id修复")
    print(f"   创建会话ID: {session_id}")
    
    # 2. 设置DataProcessor的session_id
    print("\n2. 设置DataProcessor的session_id...")
    data_processor.set_session_id(session_id)
    current_session_id = data_processor.get_session_id()
    print(f"   DataProcessor当前session_id: {current_session_id}")
    
    # 3. 模拟数据包存储
    print("\n3. 模拟存储数据包...")
    test_packets = [
        {
            'timestamp': time.time(),
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'src_port': 12345,
            'dst_port': 53,
            'protocol': 'UDP',
            'length': 64,
            'summary': 'DNS查询',
            'raw_data': b'\x00\x01\x02\x03'
        },
        {
            'timestamp': time.time() + 1,
            'src_ip': '8.8.8.8',
            'dst_ip': '192.168.1.100',
            'src_port': 53,
            'dst_port': 12345,
            'protocol': 'UDP',
            'length': 128,
            'summary': 'DNS响应',
            'raw_data': b'\x04\x05\x06\x07'
        },
        {
            'timestamp': time.time() + 2,
            'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1',
            'src_port': 54321,
            'dst_port': 80,
            'protocol': 'TCP',
            'length': 256,
            'summary': 'HTTP请求',
            'raw_data': b'\x08\x09\x0a\x0b'
        }
    ]
    
    # 通过DataProcessor存储数据包（会自动添加session_id）
    for i, packet in enumerate(test_packets):
        success = data_manager.save_packet({
            **packet,
            'session_id': data_processor.get_session_id()
        })
        print(f"   数据包{i+1}存储: {'成功' if success else '失败'}")
    
    # 4. 验证数据包查询
    print("\n4. 验证数据包查询...")
    packets = data_manager.get_packets_by_session(session_id)
    print(f"   查询到{len(packets)}个数据包")
    
    for i, packet in enumerate(packets):
        print(f"   数据包{i+1}:")
        print(f"     ID: {packet['id']}")
        print(f"     时间戳: {datetime.fromtimestamp(packet['timestamp'])}")
        print(f"     源地址: {packet['src_ip']}:{packet['src_port']}")
        print(f"     目标地址: {packet['dst_ip']}:{packet['dst_port']}")
        print(f"     协议: {packet['protocol']}")
        print(f"     长度: {packet['length']}")
        print(f"     会话ID: {packet['session_id']}")
        print()
    
    # 5. 验证数据包详情获取
    print("5. 验证数据包详情获取...")
    if packets:
        first_packet_id = packets[0]['id']
        packet_detail = data_manager.get_packet_by_id(first_packet_id)
        if packet_detail:
            print(f"   成功获取数据包{first_packet_id}的详情")
            print(f"   详情包含session_id: {packet_detail.get('session_id')}")
        else:
            print(f"   ❌ 无法获取数据包{first_packet_id}的详情")
    
    # 6. 测试会话切换
    print("\n6. 测试会话切换...")
    # 创建另一个会话
    session_id_2 = data_manager.create_session("测试会话2_session_id修复")
    print(f"   创建第二个会话ID: {session_id_2}")
    
    # 切换DataProcessor的session_id
    data_processor.set_session_id(session_id_2)
    print(f"   切换后DataProcessor的session_id: {data_processor.get_session_id()}")
    
    # 存储一个数据包到新会话
    new_packet = {
        'timestamp': time.time() + 10,
        'src_ip': '10.0.0.1',
        'dst_ip': '10.0.0.2',
        'src_port': 8080,
        'dst_port': 9090,
        'protocol': 'TCP',
        'length': 512,
        'summary': '新会话数据包',
        'raw_data': b'\x0c\x0d\x0e\x0f',
        'session_id': data_processor.get_session_id()
    }
    
    success = data_manager.save_packet(new_packet)
    print(f"   新会话数据包存储: {'成功' if success else '失败'}")
    
    # 验证两个会话的数据包分离
    packets_session_1 = data_manager.get_packets_by_session(session_id)
    packets_session_2 = data_manager.get_packets_by_session(session_id_2)
    
    print(f"   会话1数据包数量: {len(packets_session_1)}")
    print(f"   会话2数据包数量: {len(packets_session_2)}")
    
    # 7. 总结测试结果
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    success_count = 0
    total_tests = 6
    
    # 检查各项功能
    if session_id and session_id > 0:
        print("✅ 会话创建功能正常")
        success_count += 1
    else:
        print("❌ 会话创建功能异常")
    
    if data_processor.get_session_id() == session_id_2:
        print("✅ DataProcessor session_id设置功能正常")
        success_count += 1
    else:
        print("❌ DataProcessor session_id设置功能异常")
    
    if len(packets) == 3:
        print("✅ 数据包存储功能正常")
        success_count += 1
    else:
        print("❌ 数据包存储功能异常")
    
    if all(p.get('session_id') == session_id for p in packets_session_1):
        print("✅ 数据包session_id关联功能正常")
        success_count += 1
    else:
        print("❌ 数据包session_id关联功能异常")
    
    if len(packets_session_1) == 3 and len(packets_session_2) == 1:
        print("✅ 会话数据包分离功能正常")
        success_count += 1
    else:
        print("❌ 会话数据包分离功能异常")
    
    if packets and data_manager.get_packet_by_id(packets[0]['id']):
        print("✅ 数据包详情查询功能正常")
        success_count += 1
    else:
        print("❌ 数据包详情查询功能异常")
    
    print(f"\n总体测试结果: {success_count}/{total_tests} 项功能正常")
    
    if success_count == total_tests:
        print("🎉 所有功能测试通过！session_id修复成功！")
        return True
    else:
        print("⚠️  部分功能存在问题，需要进一步检查")
        return False

if __name__ == "__main__":
    try:
        success = test_session_id_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)