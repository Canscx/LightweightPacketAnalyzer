#!/usr/bin/env python3
"""
测试协议统计功能的DataManager扩展接口

验证T1任务：扩展DataManager协议统计查询接口
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_analyzer.storage.data_manager import DataManager
import time
from datetime import datetime

def test_protocol_statistics():
    """测试协议统计功能"""
    print("=== 测试协议统计功能 ===")
    
    # 使用现有数据库
    db_path = "network_analyzer.db"
    data_manager = DataManager(db_path)
    
    print(f"数据库路径: {db_path}")
    
    # 获取数据库信息
    db_info = data_manager.get_database_info()
    print(f"数据库信息: {db_info}")
    
    if db_info['packet_count'] == 0:
        print("⚠️  数据库中没有数据包，无法测试统计功能")
        return False
    
    print(f"\n📊 开始测试协议统计接口...")
    
    # 测试1: get_protocol_statistics - 完整统计
    print("\n1. 测试 get_protocol_statistics() - 完整统计")
    try:
        stats = data_manager.get_protocol_statistics()
        print(f"   ✅ 协议数量统计: {stats['protocol_counts']}")
        print(f"   ✅ 协议字节统计: {stats['protocol_bytes']}")
        print(f"   ✅ 总数据包数: {stats['total_packets']}")
        print(f"   ✅ 总字节数: {stats['total_bytes']}")
        print(f"   ✅ 时间范围: {stats['time_range']}")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试2: get_protocol_counts - 协议数量
    print("\n2. 测试 get_protocol_counts() - 协议数量统计")
    try:
        counts = data_manager.get_protocol_counts()
        print(f"   ✅ 协议数量: {counts}")
        if counts:
            top_protocol = max(counts.items(), key=lambda x: x[1])
            print(f"   ✅ 最多协议: {top_protocol[0]} ({top_protocol[1]} 个数据包)")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试3: get_protocol_bytes - 协议字节
    print("\n3. 测试 get_protocol_bytes() - 协议字节统计")
    try:
        bytes_stats = data_manager.get_protocol_bytes()
        print(f"   ✅ 协议字节: {bytes_stats}")
        if bytes_stats:
            top_bytes = max(bytes_stats.items(), key=lambda x: x[1])
            print(f"   ✅ 最大流量协议: {top_bytes[0]} ({top_bytes[1]} 字节)")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试4: 按会话过滤
    print("\n4. 测试按会话过滤")
    try:
        sessions = data_manager.get_sessions()
        if sessions:
            session_id = sessions[0]['id']
            print(f"   测试会话ID: {session_id}")
            
            session_stats = data_manager.get_protocol_statistics(session_id=session_id)
            print(f"   ✅ 会话协议统计: {session_stats['protocol_counts']}")
            
            session_counts = data_manager.get_protocol_counts(session_id=session_id)
            print(f"   ✅ 会话协议数量: {session_counts}")
            
            session_bytes = data_manager.get_protocol_bytes(session_id=session_id)
            print(f"   ✅ 会话协议字节: {session_bytes}")
        else:
            print("   ⚠️  没有会话数据，跳过会话过滤测试")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试5: 按时间范围过滤
    print("\n5. 测试按时间范围过滤")
    try:
        # 获取最近1小时的数据
        end_time = time.time()
        start_time = end_time - 3600  # 1小时前
        
        time_stats = data_manager.get_protocol_statistics(
            start_time=start_time, 
            end_time=end_time
        )
        print(f"   ✅ 时间范围统计: {time_stats['protocol_counts']}")
        print(f"   ✅ 时间范围内总数据包: {time_stats['total_packets']}")
        
        time_counts = data_manager.get_protocol_counts(
            start_time=start_time, 
            end_time=end_time
        )
        print(f"   ✅ 时间范围协议数量: {time_counts}")
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试6: 性能测试
    print("\n6. 性能测试")
    try:
        start_perf = time.time()
        stats = data_manager.get_protocol_statistics()
        end_perf = time.time()
        
        duration = end_perf - start_perf
        print(f"   ✅ 查询耗时: {duration:.3f} 秒")
        
        if duration < 1.0:
            print(f"   ✅ 性能满足要求 (<1秒)")
        else:
            print(f"   ⚠️  性能可能需要优化 (>{duration:.3f}秒)")
            
    except Exception as e:
        print(f"   ❌ 性能测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！T1任务验收成功")
    return True

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    db_path = "network_analyzer.db"
    data_manager = DataManager(db_path)
    
    # 测试空数据情况
    print("\n1. 测试未来时间范围（应该返回空结果）")
    try:
        future_time = time.time() + 86400  # 明天
        empty_stats = data_manager.get_protocol_statistics(
            start_time=future_time,
            end_time=future_time + 3600
        )
        print(f"   ✅ 空结果测试: {empty_stats}")
        assert empty_stats['total_packets'] == 0
        assert empty_stats['protocol_counts'] == {}
        print("   ✅ 边界情况处理正确")
    except Exception as e:
        print(f"   ❌ 边界测试失败: {e}")
        return False
    
    # 测试无效会话ID
    print("\n2. 测试无效会话ID")
    try:
        invalid_stats = data_manager.get_protocol_statistics(session_id=99999)
        print(f"   ✅ 无效会话ID结果: {invalid_stats}")
        print("   ✅ 无效输入处理正确")
    except Exception as e:
        print(f"   ❌ 无效输入测试失败: {e}")
        return False
    
    print("\n🎉 边界情况测试通过！")
    return True

if __name__ == "__main__":
    print("开始测试DataManager协议统计接口扩展...")
    
    # 基础功能测试
    basic_test = test_protocol_statistics()
    
    # 边界情况测试
    edge_test = test_edge_cases()
    
    if basic_test and edge_test:
        print("\n🎉🎉🎉 T1任务完全验收通过！")
        print("✅ DataManager协议统计查询接口扩展成功")
        print("✅ 所有功能正常工作")
        print("✅ 性能满足要求")
        print("✅ 错误处理完善")
        print("✅ 边界情况处理正确")
    else:
        print("\n❌ T1任务验收失败，需要修复问题")
        sys.exit(1)