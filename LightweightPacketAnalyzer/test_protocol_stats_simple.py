#!/usr/bin/env python3
"""
协议统计功能简化测试脚本

专注于核心功能测试，避免GUI相关测试
"""

import sys
import os
import logging
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.statistics.protocol_statistics import ProtocolStatistics, StatisticsFilter
from network_analyzer.statistics.statistics_visualizer import StatisticsVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_protocol_stats_simple.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleProtocolStatsTest:
    """简化的协议统计测试类"""
    
    def __init__(self):
        self.test_results = {
            'functional_tests': [],
            'performance_tests': [],
            'error_handling_tests': []
        }
        self.data_manager = None
        self.protocol_stats = None
        self.visualizer = None
    
    def setup_test_environment(self):
        """设置测试环境"""
        try:
            logger.info("设置测试环境...")
            
            # 初始化数据管理器
            logger.info("数据库初始化...")
            self.data_manager = DataManager()
            
            # 检查数据
            sessions = self.data_manager.get_sessions()
            logger.info(f"找到 {len(sessions)} 个会话用于测试")
            
            # 初始化统计模块
            self.protocol_stats = ProtocolStatistics(self.data_manager)
            self.visualizer = StatisticsVisualizer()
            
            logger.info("测试环境设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置测试环境失败: {e}")
            return False
    
    def test_core_functionality(self):
        """测试核心功能"""
        logger.info("开始核心功能测试...")
        
        try:
            # 测试1: 基本协议分布统计
            logger.info("测试1: ProtocolStatistics核心功能")
            distribution = self.protocol_stats.get_protocol_distribution()
            
            assert distribution is not None, "协议分布数据不能为空"
            assert hasattr(distribution, 'protocol_counts'), "分布数据应包含protocol_counts属性"
            assert hasattr(distribution, 'protocol_bytes'), "分布数据应包含protocol_bytes属性"
            
            logger.info(f"成功获取协议分布数据，包含 {len(distribution.protocol_counts)} 种协议")
            
            # 测试2: 过滤功能
            logger.info("测试2: 过滤功能")
            filter_params = StatisticsFilter(protocols=['TCP', 'UDP'])
            filtered_distribution = self.protocol_stats.get_protocol_distribution(filter_params)
            
            assert filtered_distribution is not None, "过滤后的分布数据不能为空"
            logger.info("过滤功能测试通过")
            
            # 测试3: 图表数据生成
            logger.info("测试3: 图表数据生成")
            chart_data = self.visualizer.create_protocol_pie_chart(distribution)
            
            assert chart_data is not None, "图表数据不能为空"
            assert hasattr(chart_data, 'figure'), "图表数据应包含figure属性"
            logger.info("图表数据生成测试通过")
            
            self.test_results['functional_tests'].append({
                'test': '核心功能测试',
                'status': 'PASS',
                'message': '所有核心功能测试通过'
            })
            
        except Exception as e:
            logger.error(f"核心功能测试失败: {e}")
            self.test_results['functional_tests'].append({
                'test': '核心功能测试',
                'status': 'FAIL',
                'message': str(e)
            })
    
    def test_performance(self):
        """测试性能"""
        logger.info("开始性能测试...")
        
        try:
            # 性能测试1: 大数据量统计
            logger.info("测试大数据量统计性能...")
            start_time = time.time()
            
            distribution = self.protocol_stats.get_protocol_distribution()
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"统计耗时: {duration:.3f}秒")
            
            # 性能测试2: 图表生成性能
            logger.info("测试图表生成性能...")
            start_time = time.time()
            
            chart_data = self.visualizer.create_protocol_pie_chart(distribution)
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"图表生成耗时: {duration:.3f}秒")
            
            self.test_results['performance_tests'].append({
                'test': '性能测试',
                'status': 'PASS',
                'message': f'统计和图表生成性能正常'
            })
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            self.test_results['performance_tests'].append({
                'test': '性能测试',
                'status': 'FAIL',
                'message': str(e)
            })
    
    def test_error_handling(self):
        """测试错误处理"""
        logger.info("开始错误处理测试...")
        
        try:
            # 错误处理测试1: 无效会话ID
            logger.info("测试无效会话ID处理...")
            filter_params = StatisticsFilter(session_id=99999)
            distribution = self.protocol_stats.get_protocol_distribution(filter_params)
            
            # 应该返回空结果而不是抛出异常
            assert distribution is not None, "无效会话ID应返回空结果"
            logger.info("无效会话ID处理正常")
            
            # 错误处理测试2: 空数据处理
            logger.info("测试空数据处理...")
            from network_analyzer.statistics.protocol_statistics import ProtocolDistribution
            empty_distribution = ProtocolDistribution(
                protocol_counts={},
                protocol_bytes={},
                protocol_percentages={},
                total_packets=0,
                total_bytes=0,
                time_range={'start': None, 'end': None}
            )
            chart_data = self.visualizer.create_protocol_pie_chart(empty_distribution)
            
            assert chart_data is not None, "空数据应能正常生成图表"
            logger.info("空数据处理正常")
            
            self.test_results['error_handling_tests'].append({
                'test': '错误处理测试',
                'status': 'PASS',
                'message': '错误处理功能正常'
            })
            
        except Exception as e:
            logger.error(f"错误处理测试失败: {e}")
            self.test_results['error_handling_tests'].append({
                'test': '错误处理测试',
                'status': 'FAIL',
                'message': str(e)
            })
    
    def generate_test_report(self):
        """生成测试报告"""
        logger.info("生成测试报告...")
        
        report = {
            'test_time': datetime.now().isoformat(),
            'summary': {
                'functional_tests': len([t for t in self.test_results['functional_tests'] if t['status'] == 'PASS']),
                'performance_tests': len([t for t in self.test_results['performance_tests'] if t['status'] == 'PASS']),
                'error_handling_tests': len([t for t in self.test_results['error_handling_tests'] if t['status'] == 'PASS']),
                'total_tests': sum(len(tests) for tests in self.test_results.values()),
                'passed_tests': sum(len([t for t in tests if t['status'] == 'PASS']) for tests in self.test_results.values())
            },
            'details': self.test_results
        }
        
        # 保存报告
        import json
        with open('test_protocol_stats_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        summary = report['summary']
        logger.info(f"测试完成: {summary['passed_tests']}/{summary['total_tests']} 通过")
        
        return report

def main():
    """主函数"""
    logger.info("开始协议统计功能简化测试...")
    
    test = SimpleProtocolStatsTest()
    
    # 设置测试环境
    if not test.setup_test_environment():
        logger.error("测试环境设置失败，终止测试")
        return False
    
    # 执行测试
    test.test_core_functionality()
    test.test_performance()
    test.test_error_handling()
    
    # 生成报告
    report = test.generate_test_report()
    
    # 检查测试结果
    if report['summary']['passed_tests'] == report['summary']['total_tests']:
        logger.info("所有测试通过！")
        return True
    else:
        logger.warning("部分测试失败，请检查详细报告")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)