#!/usr/bin/env python3
"""
协议统计功能修复验证测试
测试ChartConfig参数修复后的功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.statistics.protocol_statistics import ProtocolStatistics
from network_analyzer.statistics.statistics_visualizer import StatisticsVisualizer, ChartConfig

def test_chart_config_fix():
    """测试ChartConfig参数修复"""
    print("=== 测试ChartConfig参数修复 ===")
    
    try:
        # 测试正确的ChartConfig创建
        pie_config = ChartConfig(
            title="协议分布",
            figsize=(6, 4)
        )
        print(f"✓ 饼图配置创建成功: {pie_config}")
        
        bar_config = ChartConfig(
            title="协议统计对比",
            figsize=(6, 4),
            xlabel="协议类型",
            ylabel="数据包数量"
        )
        print(f"✓ 柱状图配置创建成功: {bar_config}")
        
        # 测试StatisticsVisualizer初始化
        visualizer = StatisticsVisualizer()
        print("✓ StatisticsVisualizer初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ ChartConfig测试失败: {e}")
        return False

def test_protocol_stats_basic():
    """测试协议统计基本功能"""
    print("\n=== 测试协议统计基本功能 ===")
    
    try:
        # 初始化数据管理器
        data_manager = DataManager("test.db")
        print("✓ DataManager初始化成功")
        
        # 初始化协议统计
        protocol_stats = ProtocolStatistics(data_manager)
        print("✓ ProtocolStatistics初始化成功")
        
        # 测试获取协议分布（可能为空，但不应该报错）
        distribution = protocol_stats.get_protocol_distribution()
        protocol_count = len(distribution.protocol_counts) if distribution else 0
        print(f"✓ 获取协议分布成功: {protocol_count} 个协议")
        
        return True
        
    except Exception as e:
        print(f"✗ 协议统计基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("协议统计功能修复验证测试")
    print("=" * 50)
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    tests = [
        test_chart_config_fix,
        test_protocol_stats_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！协议统计功能修复成功")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)