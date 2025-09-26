"""
报告生成器 - 核心统一接口

统一协调所有报告生成子模块，提供：
- 多格式报告生成
- 进度反馈
- 错误处理
- 配置管理
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from .data_collector import DataCollector, ReportData
from .charts.chart_generator import ChartGenerator
from .generators.pdf_generator import PDFGenerator
from .generators.html_generator import HTMLGenerator
from .generators.csv_generator import CSVGenerator
from ..storage.data_manager import DataManager


logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """报告格式枚举"""
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    ALL = "all"


class ReportConfig:
    """报告配置类"""
    
    def __init__(self):
        self.formats: List[ReportFormat] = [ReportFormat.PDF]
        self.include_charts: bool = True
        self.include_detailed_stats: bool = True
        self.output_dir: Optional[str] = None
        self.template_name: Optional[str] = None
        self.chart_style: str = "default"
        self.pdf_page_size: str = "A4"
        self.csv_encoding: str = "utf-8-sig"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'formats': [f.value for f in self.formats],
            'include_charts': self.include_charts,
            'include_detailed_stats': self.include_detailed_stats,
            'output_dir': self.output_dir,
            'template_name': self.template_name,
            'chart_style': self.chart_style,
            'pdf_page_size': self.pdf_page_size,
            'csv_encoding': self.csv_encoding
        }


class ReportGenerator:
    """报告生成器 - 主要接口类"""
    
    def __init__(self, data_manager: DataManager, output_dir: Optional[str] = None):
        """
        初始化报告生成器
        
        Args:
            data_manager: 数据管理器
            output_dir: 输出目录
        """
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # 初始化子模块
        self._init_submodules()
        
        # 进度回调函数
        self.progress_callback: Optional[Callable[[str, float], None]] = None
    
    def _init_submodules(self):
        """初始化子模块"""
        try:
            # 创建子目录
            charts_dir = self.output_dir / "charts"
            charts_dir.mkdir(exist_ok=True)
            
            # 初始化各个生成器
            self.data_collector = DataCollector(self.data_manager)
            self.chart_generator = ChartGenerator(str(charts_dir))
            self.pdf_generator = PDFGenerator(str(self.output_dir))
            self.html_generator = HTMLGenerator(str(self.output_dir))
            self.csv_generator = CSVGenerator(str(self.output_dir))
            
            self.logger.info("报告生成器子模块初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化子模块失败: {e}")
            raise
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """
        设置进度回调函数
        
        Args:
            callback: 进度回调函数 (message: str, progress: float)
        """
        self.progress_callback = callback
    
    def _update_progress(self, message: str, progress: float):
        """更新进度"""
        if self.progress_callback:
            try:
                self.progress_callback(message, progress)
            except Exception as e:
                self.logger.error(f"进度回调失败: {e}")
    
    def generate_report(self, session_id: int, 
                       config: Optional[ReportConfig] = None) -> Dict[str, Any]:
        """
        生成完整报告
        
        Args:
            session_id: 会话ID
            config: 报告配置
            
        Returns:
            Dict[str, Any]: 生成结果信息
        """
        try:
            if config is None:
                config = ReportConfig()
            
            self.logger.info(f"开始生成会话 {session_id} 的报告")
            self._update_progress("开始生成报告...", 0.0)
            
            # 验证会话数据
            if not self.data_collector.validate_session_data(session_id):
                raise ValueError(f"会话 {session_id} 数据无效或不存在")
            
            # 第1步：收集数据 (20%)
            self._update_progress("收集报告数据...", 0.2)
            report_data = self.data_collector.collect_session_data(session_id)
            
            # 第2步：生成图表 (40%)
            charts = {}
            if config.include_charts:
                self._update_progress("生成统计图表...", 0.4)
                charts = self._generate_all_charts(report_data, config)
            
            # 第3步：生成报告文件 (80%)
            self._update_progress("生成报告文件...", 0.6)
            generated_files = self._generate_report_files(report_data, charts, config)
            
            # 第4步：完成 (100%)
            self._update_progress("报告生成完成", 1.0)
            
            # 构建结果信息
            result = {
                'success': True,
                'session_id': session_id,
                'generated_files': generated_files,
                'charts': charts,
                'generation_time': datetime.now(),
                'config': config.to_dict()
            }
            
            self.logger.info(f"会话 {session_id} 报告生成完成")
            return result
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            self._update_progress(f"生成失败: {e}", 0.0)
            raise
    
    def _generate_all_charts(self, report_data: ReportData, 
                           config: ReportConfig) -> Dict[str, str]:
        """生成所有图表"""
        charts = {}
        
        try:
            # 1. 协议分布饼图
            protocol_stats = report_data.protocol_stats
            distribution = protocol_stats.get('distribution', {})
            protocol_counts = distribution.get('protocol_counts', {})
            
            if protocol_counts:
                chart_path = self.chart_generator.generate_protocol_pie_chart(
                    protocol_counts, "协议分布统计"
                )
                charts['protocol_pie_chart'] = chart_path
            
            # 2. 流量趋势线图
            traffic_trends = report_data.traffic_trends
            time_series = traffic_trends.get('time_series', [])
            
            if time_series:
                time_data = [item.get('timestamp', 0) for item in time_series]
                packet_counts = [item.get('packet_count', 0) for item in time_series]
                
                if time_data and packet_counts:
                    chart_path = self.chart_generator.generate_traffic_trend_chart(
                        time_data, packet_counts, "流量趋势分析"
                    )
                    charts['traffic_trend_chart'] = chart_path
            
            # 3. Top协议条形图
            top_protocols = protocol_stats.get('top_protocols_by_count', [])
            if top_protocols:
                chart_path = self.chart_generator.generate_top_protocols_bar_chart(
                    top_protocols[:10], "Top 10 协议统计"
                )
                charts['top_protocols_chart'] = chart_path
            
            # 4. 组合仪表板
            dashboard_data = {
                'protocol_distribution': protocol_counts,
                'traffic_trends': {
                    'time_data': [item.get('timestamp', 0) for item in time_series],
                    'packet_counts': [item.get('packet_count', 0) for item in time_series]
                },
                'top_protocols': top_protocols
            }
            
            chart_path = self.chart_generator.generate_combined_chart(
                dashboard_data, "dashboard"
            )
            charts['dashboard_chart'] = chart_path
            
            self.logger.info(f"生成了 {len(charts)} 个图表")
            return charts
            
        except Exception as e:
            self.logger.error(f"生成图表失败: {e}")
            return {}
    
    def _generate_report_files(self, report_data: ReportData, 
                             charts: Dict[str, str],
                             config: ReportConfig) -> Dict[str, str]:
        """生成报告文件"""
        generated_files = {}
        
        try:
            # 准备完整的报告数据（包含图表路径）
            full_report_data = {
                'session_info': report_data.session_info.__dict__,
                'protocol_stats': report_data.protocol_stats,
                'traffic_trends': report_data.traffic_trends,
                'summary_stats': report_data.summary_stats,
                'generation_time': report_data.generation_time,
                **charts  # 添加图表路径
            }
            
            # 生成各种格式的报告
            for format_type in config.formats:
                if format_type == ReportFormat.PDF:
                    self._update_progress("生成PDF报告...", 0.7)
                    pdf_path = self.pdf_generator.generate_report(full_report_data)
                    generated_files['pdf'] = pdf_path
                
                elif format_type == ReportFormat.HTML:
                    self._update_progress("生成HTML报告...", 0.75)
                    html_path = self.html_generator.generate_report(
                        full_report_data, template_name=config.template_name
                    )
                    generated_files['html'] = html_path
                
                elif format_type == ReportFormat.CSV:
                    self._update_progress("导出CSV数据...", 0.8)
                    csv_files = self.csv_generator.export_to_multiple_files(full_report_data)
                    generated_files.update(csv_files)
                
                elif format_type == ReportFormat.ALL:
                    # 生成所有格式
                    self._update_progress("生成PDF报告...", 0.7)
                    pdf_path = self.pdf_generator.generate_report(full_report_data)
                    generated_files['pdf'] = pdf_path
                    
                    self._update_progress("生成HTML报告...", 0.75)
                    html_path = self.html_generator.generate_report(full_report_data)
                    generated_files['html'] = html_path
                    
                    self._update_progress("导出CSV数据...", 0.8)
                    csv_files = self.csv_generator.export_to_multiple_files(full_report_data)
                    generated_files.update(csv_files)
            
            return generated_files
            
        except Exception as e:
            self.logger.error(f"生成报告文件失败: {e}")
            raise
    
    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """
        获取可用的会话列表
        
        Returns:
            List[Dict]: 会话信息列表
        """
        try:
            return self.data_collector.get_available_sessions()
        except Exception as e:
            self.logger.error(f"获取会话列表失败: {e}")
            return []
    
    def validate_session(self, session_id: int) -> bool:
        """
        验证会话是否可以生成报告
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否可以生成报告
        """
        try:
            return self.data_collector.validate_session_data(session_id)
        except Exception as e:
            self.logger.error(f"验证会话失败: {e}")
            return False
    
    def get_report_preview(self, session_id: int) -> Dict[str, Any]:
        """
        获取报告预览信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict: 预览信息
        """
        try:
            if not self.validate_session(session_id):
                return {'valid': False, 'error': '会话数据无效'}
            
            # 收集基本信息
            report_data = self.data_collector.collect_session_data(session_id)
            
            # 构建预览信息
            preview = {
                'valid': True,
                'session_name': report_data.session_info.name,
                'packet_count': report_data.session_info.packet_count,
                'duration': report_data.session_info.duration,
                'protocol_count': len(report_data.protocol_stats.get('distribution', {}).get('protocol_counts', {})),
                'estimated_size': self._estimate_report_size(report_data),
                'estimated_time': self._estimate_generation_time(report_data)
            }
            
            return preview
            
        except Exception as e:
            self.logger.error(f"获取报告预览失败: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _estimate_report_size(self, report_data: ReportData) -> Dict[str, str]:
        """估算报告大小"""
        try:
            packet_count = report_data.session_info.packet_count
            
            # 基于数据包数量估算文件大小
            pdf_size_kb = max(100, packet_count * 0.01)  # 最小100KB
            html_size_kb = max(50, packet_count * 0.005)  # 最小50KB
            csv_size_kb = max(10, packet_count * 0.001)   # 最小10KB
            
            return {
                'pdf': f"{pdf_size_kb:.0f} KB",
                'html': f"{html_size_kb:.0f} KB", 
                'csv': f"{csv_size_kb:.0f} KB"
            }
            
        except Exception as e:
            self.logger.error(f"估算报告大小失败: {e}")
            return {'pdf': '未知', 'html': '未知', 'csv': '未知'}
    
    def _estimate_generation_time(self, report_data: ReportData) -> str:
        """估算生成时间"""
        try:
            packet_count = report_data.session_info.packet_count
            
            # 基于数据包数量估算生成时间
            if packet_count < 1000:
                return "< 5 秒"
            elif packet_count < 10000:
                return "5-15 秒"
            elif packet_count < 50000:
                return "15-30 秒"
            else:
                return "30-60 秒"
                
        except Exception as e:
            self.logger.error(f"估算生成时间失败: {e}")
            return "未知"
    
    def cleanup_old_reports(self, keep_days: int = 7):
        """
        清理旧的报告文件
        
        Args:
            keep_days: 保留天数
        """
        try:
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (keep_days * 24 * 3600)
            
            # 清理各种格式的报告文件
            patterns = ['*.pdf', '*.html', '*.csv']
            
            for pattern in patterns:
                for file_path in self.output_dir.glob(pattern):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        self.logger.debug(f"删除旧报告文件: {file_path}")
            
            # 清理图表文件
            self.chart_generator.cleanup_old_charts(keep_days)
            
            self.logger.info(f"清理了 {keep_days} 天前的旧报告文件")
            
        except Exception as e:
            self.logger.error(f"清理旧报告失败: {e}")
    
    def get_generation_status(self) -> Dict[str, Any]:
        """
        获取生成器状态信息
        
        Returns:
            Dict: 状态信息
        """
        try:
            return {
                'output_dir': str(self.output_dir),
                'output_dir_exists': self.output_dir.exists(),
                'available_sessions': len(self.get_available_sessions()),
                'submodules_initialized': all([
                    self.data_collector is not None,
                    self.chart_generator is not None,
                    self.pdf_generator is not None,
                    self.html_generator is not None,
                    self.csv_generator is not None
                ])
            }
            
        except Exception as e:
            self.logger.error(f"获取生成器状态失败: {e}")
            return {'error': str(e)}
    
    def test_generation_pipeline(self, session_id: int) -> Dict[str, Any]:
        """
        测试生成流水线
        
        Args:
            session_id: 测试会话ID
            
        Returns:
            Dict: 测试结果
        """
        try:
            test_results = {
                'data_collection': False,
                'chart_generation': False,
                'pdf_generation': False,
                'html_generation': False,
                'csv_generation': False,
                'overall': False
            }
            
            # 测试数据收集
            try:
                report_data = self.data_collector.collect_session_data(session_id)
                test_results['data_collection'] = True
            except Exception as e:
                self.logger.error(f"数据收集测试失败: {e}")
                return test_results
            
            # 测试图表生成
            try:
                protocol_counts = report_data.protocol_stats.get('distribution', {}).get('protocol_counts', {})
                if protocol_counts:
                    chart_path = self.chart_generator.generate_protocol_pie_chart(
                        protocol_counts, "测试图表"
                    )
                    if os.path.exists(chart_path):
                        test_results['chart_generation'] = True
                        # 清理测试图表
                        os.remove(chart_path)
            except Exception as e:
                self.logger.error(f"图表生成测试失败: {e}")
            
            # 测试各种格式生成
            test_data = {
                'session_info': report_data.session_info.__dict__,
                'protocol_stats': report_data.protocol_stats,
                'traffic_trends': report_data.traffic_trends,
                'summary_stats': report_data.summary_stats,
                'generation_time': datetime.now()
            }
            
            # 测试PDF生成
            try:
                pdf_path = self.pdf_generator.generate_report(test_data, "test_report.pdf")
                if os.path.exists(pdf_path):
                    test_results['pdf_generation'] = True
                    os.remove(pdf_path)  # 清理测试文件
            except Exception as e:
                self.logger.error(f"PDF生成测试失败: {e}")
            
            # 测试HTML生成
            try:
                html_path = self.html_generator.generate_report(test_data, "test_report.html")
                if os.path.exists(html_path):
                    test_results['html_generation'] = True
                    os.remove(html_path)  # 清理测试文件
            except Exception as e:
                self.logger.error(f"HTML生成测试失败: {e}")
            
            # 测试CSV生成
            try:
                csv_path = self.csv_generator.export_report_data(test_data, "test_report.csv")
                if os.path.exists(csv_path):
                    test_results['csv_generation'] = True
                    os.remove(csv_path)  # 清理测试文件
            except Exception as e:
                self.logger.error(f"CSV生成测试失败: {e}")
            
            # 整体测试结果
            test_results['overall'] = all([
                test_results['data_collection'],
                test_results['chart_generation'],
                test_results['pdf_generation'],
                test_results['html_generation'],
                test_results['csv_generation']
            ])
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"测试生成流水线失败: {e}")
            return {'error': str(e)}