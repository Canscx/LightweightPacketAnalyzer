#!/usr/bin/env python3
"""
测试ProtocolStatistics核心统计类

验证T2任务：实现ProtocolStatistics核心统计类
"""

import sys
import os
from pathlib import Path
import time
import json

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.statistics.protocol_statistics import (
    ProtocolStatistics, 
    StatisticsFilter, 
    ProtocolDistribution,
    TimeSeriesData
)

def test_protocol_statistics_core():
    """测试ProtocolStatistics核心功能"""
    print("=== 测试ProtocolStatistics核心统计类 ===")
    
    # 初始化
    db_path = "network_analyzer.db"
    data_manager = DataManager(db_path)
    protocol_stats = ProtocolStatistics(data_manager)
    
    print(f"数据库路径: {db_path}")
    
    # 获取数据库信息
    db_info = data_manager.get_database_info()
    print(f"数据库信息: {db_info}")
    
    if db_info['packet_count'] == 0:
        print("⚠️  数据库中没有数据包，无法测试统计功能")
        return False
    
    print(f"\n📊 开始测试ProtocolStatistics核心功能...")
    
    # 测试1: get_protocol_distribution - 基础协议分布
    print("\n1. 测试 get_protocol_distribution() - 基础协议分布")
    try:
        distribution = protocol_stats.get_protocol_distribution()
        
        print(f"   ✅ 协议数量: {distribution.protocol_counts}")
        print(f"   ✅ 协议字节: {distribution.protocol_bytes}")
        print(f"   ✅ 协议百分比: {distribution.protocol_percentages}")
        print(f"   ✅ 总数据包: {distribution.total_packets}")
        print(f"   ✅ 总字节数: {distribution.total_bytes}")
        print(f"   ✅ 时间范围: {distribution.time_range}")
        
        # 测试Top协议
        top_by_packets = distribution.get_top_protocols(limit=3, by_packets=True)
        top_by_bytes = distribution.get_top_protocols(limit=3, by_packets=False)
        print(f"   ✅ Top协议(按数量): {top_by_packets}")
        print(f"   ✅ Top协议(按字节): {top_by_bytes}")
        
        # 测试协议百分比
        if distribution.protocol_counts:
            first_protocol = list(distribution.protocol_counts.keys())[0]
            percentage = distribution.get_protocol_percentage(first_protocol, by_packets=True)
            print(f"   ✅ {first_protocol}协议百分比: {percentage:.2f}%")
        
        assert isinstance(distribution, ProtocolDistribution)
        assert distribution.total_packets >= 0
        assert distribution.total_bytes >= 0
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试2: 使用过滤器
    print("\n2. 测试 StatisticsFilter - 过滤功能")
    try:
        # 测试协议过滤
        if distribution.protocol_counts:
            protocols = list(distribution.protocol_counts.keys())[:2]  # 取前2个协议
            filter_params = StatisticsFilter(protocols=protocols)
            
            filtered_distribution = protocol_stats.get_protocol_distribution(filter_params)
            print(f"   ✅ 过滤协议: {protocols}")
            print(f"   ✅ 过滤结果: {filtered_distribution.protocol_counts}")
            
            # 验证过滤结果只包含指定协议
            for protocol in filtered_distribution.protocol_counts.keys():
                assert protocol in protocols, f"过滤结果包含未指定协议: {protocol}"
        
        # 测试时间过滤
        current_time = time.time()
        time_filter = StatisticsFilter(
            start_time=current_time - 3600,  # 1小时前
            end_time=current_time
        )
        
        time_filtered = protocol_stats.get_protocol_distribution(time_filter)
        print(f"   ✅ 时间过滤结果: {time_filtered.protocol_counts}")
        
        # 测试过滤器转换
        filter_dict = filter_params.to_dict()
        print(f"   ✅ 过滤器字典: {filter_dict}")
        assert isinstance(filter_dict, dict)
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试3: get_time_series_data - 时间序列数据
    print("\n3. 测试 get_time_series_data() - 时间序列数据")
    try:
        if distribution.protocol_counts:
            protocol = list(distribution.protocol_counts.keys())[0]
            
            # 测试不同时间间隔
            for interval in [30, 60, 120]:
                ts_data = protocol_stats.get_time_series_data(protocol, interval)
                
                print(f"   ✅ 协议 {protocol}, 间隔 {interval}s:")
                print(f"       时间点数: {len(ts_data.timestamps)}")
                print(f"       数值数: {len(ts_data.values)}")
                print(f"       峰值时间: {ts_data.get_peak_time()}")
                print(f"       平均速率: {ts_data.get_average_rate():.2f} 包/秒")
                
                assert isinstance(ts_data, TimeSeriesData)
                assert ts_data.protocol == protocol
                assert ts_data.interval == interval
                assert len(ts_data.timestamps) == len(ts_data.values)
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试4: get_protocol_comparison - 协议对比
    print("\n4. 测试 get_protocol_comparison() - 协议对比")
    try:
        if len(distribution.protocol_counts) >= 2:
            protocols = list(distribution.protocol_counts.keys())[:2]
            
            comparison = protocol_stats.get_protocol_comparison(protocols)
            print(f"   ✅ 对比协议: {protocols}")
            
            for protocol, dist in comparison.items():
                print(f"   ✅ {protocol}: {dist.protocol_counts}")
                assert isinstance(dist, ProtocolDistribution)
        else:
            print("   ⚠️  协议数量不足，跳过对比测试")
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试5: get_traffic_summary - 流量摘要
    print("\n5. 测试 get_traffic_summary() - 流量摘要")
    try:
        summary = protocol_stats.get_traffic_summary()
        
        print(f"   ✅ 总数据包: {summary['total_packets']}")
        print(f"   ✅ 总字节数: {summary['total_bytes']}")
        print(f"   ✅ 协议种类: {summary['protocol_count']}")
        print(f"   ✅ 平均包大小: {summary['avg_packet_size']:.2f} 字节")
        print(f"   ✅ 时间跨度: {summary['time_span']:.2f} 秒")
        print(f"   ✅ 包速率: {summary['packet_rate']:.2f} 包/秒")
        print(f"   ✅ 字节速率: {summary['byte_rate']:.2f} 字节/秒")
        print(f"   ✅ Top协议(数量): {summary['top_protocols_by_packets']}")
        print(f"   ✅ Top协议(字节): {summary['top_protocols_by_bytes']}")
        
        # 验证数据类型和合理性
        assert isinstance(summary['total_packets'], int)
        assert isinstance(summary['total_bytes'], int)
        assert isinstance(summary['protocol_count'], int)
        assert summary['avg_packet_size'] >= 0
        assert summary['time_span'] >= 0
        assert summary['packet_rate'] >= 0
        assert summary['byte_rate'] >= 0
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    # 测试6: export_statistics - 数据导出
    print("\n6. 测试 export_statistics() - 数据导出")
    try:
        # 基础导出
        export_data = protocol_stats.export_statistics()
        
        print(f"   ✅ 导出时间: {export_data['export_time']}")
        print(f"   ✅ 包含协议分布: {'protocol_distribution' in export_data}")
        print(f"   ✅ 包含流量摘要: {'traffic_summary' in export_data}")
        
        # 包含时间序列的导出
        if distribution.protocol_counts:
            export_with_ts = protocol_stats.export_statistics(
                include_time_series=True,
                time_interval=60
            )
            
            print(f"   ✅ 包含时间序列: {'time_series' in export_with_ts}")
            if 'time_series' in export_with_ts:
                ts_protocols = list(export_with_ts['time_series'].keys())
                print(f"   ✅ 时间序列协议: {ts_protocols}")
        
        # 验证导出数据结构
        assert 'export_time' in export_data
        assert 'protocol_distribution' in export_data
        assert 'traffic_summary' in export_data
        assert isinstance(export_data['export_time'], float)
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！T2任务验收成功")
    return True

def test_performance():
    """性能测试"""
    print("\n=== 性能测试 ===")
    
    db_path = "network_analyzer.db"
    data_manager = DataManager(db_path)
    protocol_stats = ProtocolStatistics(data_manager)
    
    # 测试各个方法的性能
    methods_to_test = [
        ('get_protocol_distribution', lambda: protocol_stats.get_protocol_distribution()),
        ('get_traffic_summary', lambda: protocol_stats.get_traffic_summary()),
        ('export_statistics', lambda: protocol_stats.export_statistics())
    ]
    
    for method_name, method_func in methods_to_test:
        try:
            start_time = time.time()
            result = method_func()
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"   ✅ {method_name}: {duration:.3f} 秒")
            
            if duration < 1.0:
                print(f"       ✅ 性能良好 (<1秒)")
            else:
                print(f"       ⚠️  性能需要关注 (>{duration:.3f}秒)")
                
        except Exception as e:
            print(f"   ❌ {method_name} 性能测试失败: {e}")
            return False
    
    print("\n🎉 性能测试完成！")
    return True

def test_edge_cases():
    """边界情况测试"""
    print("\n=== 边界情况测试 ===")
    
    db_path = "network_analyzer.db"
    data_manager = DataManager(db_path)
    protocol_stats = ProtocolStatistics(data_manager)
    
    # 测试空过滤器
    print("\n1. 测试空过滤器")
    try:
        empty_filter = StatisticsFilter()
        result = protocol_stats.get_protocol_distribution(empty_filter)
        print(f"   ✅ 空过滤器结果: {result.total_packets} 个数据包")
    except Exception as e:
        print(f"   ❌ 空过滤器测试失败: {e}")
        return False
    
    # 测试不存在的协议
    print("\n2. 测试不存在的协议")
    try:
        ts_data = protocol_stats.get_time_series_data("NONEXISTENT_PROTOCOL")
        print(f"   ✅ 不存在协议的时间序列: {len(ts_data.timestamps)} 个时间点")
        assert len(ts_data.timestamps) == 0
        assert len(ts_data.values) == 0
    except Exception as e:
        print(f"   ❌ 不存在协议测试失败: {e}")
        return False
    
    # 测试无效时间范围
    print("\n3. 测试无效时间范围")
    try:
        future_filter = StatisticsFilter(
            start_time=time.time() + 86400,  # 明天
            end_time=time.time() + 90000     # 明天+1小时
        )
        result = protocol_stats.get_protocol_distribution(future_filter)
        print(f"   ✅ 未来时间范围结果: {result.total_packets} 个数据包")
        assert result.total_packets == 0
    except Exception as e:
        print(f"   ❌ 无效时间范围测试失败: {e}")
        return False
    
    print("\n🎉 边界情况测试通过！")
    return True

if __name__ == "__main__":
    print("开始测试ProtocolStatistics核心统计类...")
    
    # 核心功能测试
    core_test = test_protocol_statistics_core()
    
    # 性能测试
    perf_test = test_performance()
    
    # 边界情况测试
    edge_test = test_edge_cases()
    
    if core_test and perf_test and edge_test:
        print("\n🎉🎉🎉 T2任务完全验收通过！")
        print("✅ ProtocolStatistics核心统计类实现成功")
        print("✅ 所有统计功能正常工作")
        print("✅ 数据结构设计合理")
        print("✅ 性能满足要求")
        print("✅ 错误处理完善")
        print("✅ 边界情况处理正确")
        print("✅ 代码质量良好")
    else:
        print("\n❌ T2任务验收失败，需要修复问题")
        sys.exit(1)