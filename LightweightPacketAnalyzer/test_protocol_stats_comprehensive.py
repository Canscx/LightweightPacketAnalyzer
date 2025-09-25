#!/usr/bin/env python3
"""
协议统计功能综合测试脚本
测试整个协议统计功能的端到端工作流程，包括：
1. 功能测试 - 验证所有功能正常工作
2. 性能测试 - 验证响应时间和内存使用
3. 用户体验测试 - 验证界面友好性
4. 错误处理测试 - 验证异常情况处理
"""

import sys
import os
import time
import logging
import traceback
import tkinter as tk
from datetime import datetime, timedelta
import psutil
import threading

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.config.settings import Settings
from network_analyzer.storage.data_manager import DataManager
from network_analyzer.statistics.protocol_statistics import ProtocolStatistics, StatisticsFilter
from network_analyzer.statistics.statistics_visualizer import StatisticsVisualizer
from network_analyzer.gui.dialogs.protocol_stats_dialog import ProtocolStatsDialog

class ProtocolStatsTestSuite:
    """协议统计功能测试套件"""
    
    def __init__(self):
        self.setup_logging()
        self.settings = Settings()
        self.data_manager = None
        self.test_results = {
            'functional_tests': [],
            'performance_tests': [],
            'ui_tests': [],
            'error_handling_tests': []
        }
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_protocol_stats_comprehensive.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_test_environment(self):
        """设置测试环境"""
        try:
            self.logger.info("设置测试环境...")
            
            # 初始化数据管理器
            self.data_manager = DataManager(self.settings.DATABASE_PATH)
            
            # 检查数据库中是否有测试数据
            sessions = self.data_manager.get_sessions()
            if not sessions:
                self.logger.warning("数据库中没有会话数据，某些测试可能无法执行")
                return False
                
            self.logger.info(f"找到 {len(sessions)} 个会话用于测试")
            return True
            
        except Exception as e:
            self.logger.error(f"设置测试环境失败: {e}")
            return False
            
    def test_functional_requirements(self):
        """功能测试 - 验证所有功能正常工作"""
        self.logger.info("开始功能测试...")
        
        try:
            # 测试1: ProtocolStatistics核心功能
            self.logger.info("测试1: ProtocolStatistics核心功能")
            protocol_stats = ProtocolStatistics(self.data_manager)
            
            # 获取会话列表
            sessions = self.data_manager.get_sessions()
            if not sessions:
                self.test_results['functional_tests'].append({
                    'test': 'ProtocolStatistics核心功能',
                    'status': 'SKIP',
                    'message': '没有可用的会话数据'
                })
                return
                
            test_session_id = sessions[0]['id']
            
            # 测试协议分布
            filter_obj = StatisticsFilter(session_id=test_session_id)
            distribution = protocol_stats.get_protocol_distribution(filter_obj)
            
            assert distribution is not None, "协议分布数据不能为空"
            assert hasattr(distribution, 'protocol_counts'), "分布数据应包含protocol_counts属性"
            assert hasattr(distribution, 'protocol_bytes'), "分布数据应包含protocol_bytes属性"
            
            self.test_results['functional_tests'].append({
                'test': 'ProtocolStatistics核心功能',
                'status': 'PASS',
                'message': f'成功获取协议分布数据，包含 {len(distribution.protocol_counts)} 种协议'
            })
            
            # 测试2: StatisticsVisualizer图表生成
            self.logger.info("测试2: StatisticsVisualizer图表生成")
            visualizer = StatisticsVisualizer()
            
            # 创建临时根窗口用于测试
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            
            # 测试饼图生成
            pie_frame = tk.Frame(root)
            visualizer.create_protocol_pie_chart(distribution)
            
            # 测试柱状图生成
            bar_frame = tk.Frame(root)
            visualizer.create_protocol_bar_chart(distribution)
            
            root.destroy()
            
            self.test_results['functional_tests'].append({
                'test': 'StatisticsVisualizer图表生成',
                'status': 'PASS',
                'message': '成功生成饼图和柱状图'
            })
            
            # 测试3: ProtocolStatsDialog界面创建
            self.logger.info("测试3: ProtocolStatsDialog界面创建")
            root = tk.Tk()
            root.withdraw()
            
            dialog = ProtocolStatsDialog(root, self.data_manager, test_session_id)
            
            # 验证对话框组件
            assert hasattr(dialog, 'pie_frame'), "对话框应包含饼图框架"
            assert hasattr(dialog, 'bar_frame'), "对话框应包含柱状图框架"
            assert hasattr(dialog, 'table_frame'), "对话框应包含表格框架"
            
            root.destroy()
            
            self.test_results['functional_tests'].append({
                'test': 'ProtocolStatsDialog界面创建',
                'status': 'PASS',
                'message': '成功创建协议统计对话框'
            })
            
        except Exception as e:
            self.logger.error(f"功能测试失败: {e}")
            self.test_results['functional_tests'].append({
                'test': '功能测试',
                'status': 'FAIL',
                'message': f'测试失败: {str(e)}'
            })
            
    def test_performance_requirements(self):
        """性能测试 - 验证响应时间和内存使用"""
        self.logger.info("开始性能测试...")
        
        try:
            protocol_stats = ProtocolStatistics(self.data_manager)
            sessions = self.data_manager.get_sessions()
            
            if not sessions:
                self.test_results['performance_tests'].append({
                    'test': '性能测试',
                    'status': 'SKIP',
                    'message': '没有可用的会话数据'
                })
                return
                
            test_session_id = sessions[0]['id']
            
            # 测试1: 协议分布查询性能
            self.logger.info("测试协议分布查询性能...")
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            filter_obj = StatisticsFilter(session_id=test_session_id)
            distribution = protocol_stats.get_protocol_distribution(filter_obj)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            query_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # 性能要求：查询时间 < 2秒，内存增长 < 50MB
            performance_ok = query_time < 2.0 and memory_usage < 50
            
            self.test_results['performance_tests'].append({
                'test': '协议分布查询性能',
                'status': 'PASS' if performance_ok else 'FAIL',
                'message': f'查询时间: {query_time:.2f}s, 内存使用: {memory_usage:.2f}MB'
            })
            
            # 测试2: 图表渲染性能
            self.logger.info("测试图表渲染性能...")
            start_time = time.time()
            
            root = tk.Tk()
            root.withdraw()
            
            visualizer = StatisticsVisualizer()
            pie_frame = tk.Frame(root)
            visualizer.create_protocol_pie_chart(distribution)
            
            end_time = time.time()
            render_time = end_time - start_time
            
            root.destroy()
            
            # 渲染时间要求 < 1秒
            render_ok = render_time < 1.0
            
            self.test_results['performance_tests'].append({
                'test': '图表渲染性能',
                'status': 'PASS' if render_ok else 'FAIL',
                'message': f'渲染时间: {render_time:.2f}s'
            })
            
        except Exception as e:
            self.logger.error(f"性能测试失败: {e}")
            self.test_results['performance_tests'].append({
                'test': '性能测试',
                'status': 'FAIL',
                'message': f'测试失败: {str(e)}'
            })
            
    def test_user_experience(self):
        """用户体验测试 - 验证界面友好性"""
        self.logger.info("开始用户体验测试...")
        
        try:
            sessions = self.data_manager.get_sessions()
            if not sessions:
                self.test_results['ui_tests'].append({
                    'test': '用户体验测试',
                    'status': 'SKIP',
                    'message': '没有可用的会话数据'
                })
                return
                
            test_session_id = sessions[0]['id']
            
            # 测试1: 对话框响应性
            self.logger.info("测试对话框响应性...")
            root = tk.Tk()
            root.withdraw()
            
            start_time = time.time()
            dialog = ProtocolStatsDialog(root, self.data_manager, test_session_id)
            creation_time = time.time() - start_time
            
            # 对话框创建时间应 < 3秒
            responsive = creation_time < 3.0
            
            self.test_results['ui_tests'].append({
                'test': '对话框响应性',
                'status': 'PASS' if responsive else 'FAIL',
                'message': f'对话框创建时间: {creation_time:.2f}s'
            })
            
            # 测试2: 界面组件完整性
            self.logger.info("测试界面组件完整性...")
            components_ok = all([
                hasattr(dialog, 'pie_frame'),
                hasattr(dialog, 'bar_frame'),
                hasattr(dialog, 'table_frame'),
                hasattr(dialog, 'filter_frame')
            ])
            
            self.test_results['ui_tests'].append({
                'test': '界面组件完整性',
                'status': 'PASS' if components_ok else 'FAIL',
                'message': '所有必需的界面组件都存在' if components_ok else '缺少必需的界面组件'
            })
            
            root.destroy()
            
        except Exception as e:
            self.logger.error(f"用户体验测试失败: {e}")
            self.test_results['ui_tests'].append({
                'test': '用户体验测试',
                'status': 'FAIL',
                'message': f'测试失败: {str(e)}'
            })
            
    def test_error_handling(self):
        """错误处理测试 - 验证异常情况处理"""
        self.logger.info("开始错误处理测试...")
        
        try:
            protocol_stats = ProtocolStatistics(self.data_manager)
            
            # 测试1: 无效会话ID处理
            self.logger.info("测试无效会话ID处理...")
            try:
                filter_obj = StatisticsFilter(session_id=99999)  # 不存在的会话ID
                distribution = protocol_stats.get_protocol_distribution(filter_obj)
                
                # 应该返回空结果而不是抛出异常
                error_handled = distribution is not None
                
                self.test_results['error_handling_tests'].append({
                    'test': '无效会话ID处理',
                    'status': 'PASS' if error_handled else 'FAIL',
                    'message': '正确处理无效会话ID' if error_handled else '未正确处理无效会话ID'
                })
                
            except Exception as e:
                self.test_results['error_handling_tests'].append({
                    'test': '无效会话ID处理',
                    'status': 'FAIL',
                    'message': f'未捕获异常: {str(e)}'
                })
                
            # 测试2: 空数据处理
            self.logger.info("测试空数据处理...")
            try:
                root = tk.Tk()
                root.withdraw()
                
                visualizer = StatisticsVisualizer()
                pie_frame = tk.Frame(root)
                
                # 传入空数据
                from network_analyzer.statistics.protocol_statistics import ProtocolDistribution
                empty_distribution = ProtocolDistribution(
                    protocol_counts={},
                    protocol_bytes={},
                    protocol_percentages={},
                    total_packets=0,
                    total_bytes=0,
                    time_range={'start': None, 'end': None}
                )
                visualizer.create_protocol_pie_chart(empty_distribution)
                
                root.destroy()
                
                self.test_results['error_handling_tests'].append({
                    'test': '空数据处理',
                    'status': 'PASS',
                    'message': '正确处理空数据'
                })
                
            except Exception as e:
                self.test_results['error_handling_tests'].append({
                    'test': '空数据处理',
                    'status': 'FAIL',
                    'message': f'空数据处理失败: {str(e)}'
                })
                
        except Exception as e:
            self.logger.error(f"错误处理测试失败: {e}")
            self.test_results['error_handling_tests'].append({
                'test': '错误处理测试',
                'status': 'FAIL',
                'message': f'测试失败: {str(e)}'
            })
            
    def generate_test_report(self):
        """生成测试报告"""
        self.logger.info("生成测试报告...")
        
        report = []
        report.append("=" * 60)
        report.append("协议统计功能综合测试报告")
        report.append("=" * 60)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 统计测试结果
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for category, tests in self.test_results.items():
            report.append(f"\n{category.upper().replace('_', ' ')}:")
            report.append("-" * 40)
            
            for test in tests:
                total_tests += 1
                status = test['status']
                if status == 'PASS':
                    passed_tests += 1
                    status_symbol = "✅"
                elif status == 'FAIL':
                    failed_tests += 1
                    status_symbol = "❌"
                else:  # SKIP
                    skipped_tests += 1
                    status_symbol = "⏭️"
                    
                report.append(f"{status_symbol} {test['test']}: {test['message']}")
                
        # 总结
        report.append("\n" + "=" * 60)
        report.append("测试总结")
        report.append("=" * 60)
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过: {passed_tests}")
        report.append(f"失败: {failed_tests}")
        report.append(f"跳过: {skipped_tests}")
        
        if failed_tests == 0:
            report.append("\n🎉 所有测试通过！协议统计功能验证成功。")
        else:
            report.append(f"\n⚠️  有 {failed_tests} 个测试失败，需要修复。")
            
        # 保存报告到文件
        report_content = "\n".join(report)
        with open('protocol_stats_test_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # 输出到控制台
        print(report_content)
        
        return failed_tests == 0
        
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("开始协议统计功能综合测试...")
        
        # 设置测试环境
        if not self.setup_test_environment():
            self.logger.error("测试环境设置失败，终止测试")
            return False
            
        # 执行各类测试
        self.test_functional_requirements()
        self.test_performance_requirements()
        self.test_user_experience()
        self.test_error_handling()
        
        # 生成测试报告
        return self.generate_test_report()

def main():
    """主函数"""
    print("协议统计功能综合测试")
    print("=" * 40)
    
    test_suite = ProtocolStatsTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()