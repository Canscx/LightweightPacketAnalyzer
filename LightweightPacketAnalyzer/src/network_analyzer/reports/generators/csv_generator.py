"""
CSV数据导出器

提供CSV格式的数据导出功能，支持：
- 协议统计数据导出
- 流量趋势数据导出
- 数据包详情导出
- Excel兼容格式
"""

import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import io


logger = logging.getLogger(__name__)


class CSVGenerator:
    """CSV数据导出器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化CSV导出器
        
        Args:
            output_dir: 输出目录
        """
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    def export_report_data(self, report_data: Dict[str, Any], 
                          output_filename: Optional[str] = None) -> str:
        """
        导出完整的报告数据为CSV文件
        
        Args:
            report_data: 报告数据
            output_filename: 输出文件名
            
        Returns:
            str: 生成的CSV文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"network_analysis_data_{timestamp}.csv"
            
            filepath = self.output_dir / output_filename
            
            # 准备CSV数据
            csv_data = self._prepare_comprehensive_data(report_data)
            
            # 写入CSV文件
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入数据
                for row in csv_data:
                    writer.writerow(row)
            
            self.logger.info(f"CSV报告导出成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"导出CSV报告失败: {e}")
            raise
    
    def export_protocol_statistics(self, protocol_stats: Dict[str, Any], 
                                 output_filename: Optional[str] = None) -> str:
        """
        导出协议统计数据
        
        Args:
            protocol_stats: 协议统计数据
            output_filename: 输出文件名
            
        Returns:
            str: 生成的CSV文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"protocol_statistics_{timestamp}.csv"
            
            filepath = self.output_dir / output_filename
            
            # 准备协议统计数据
            distribution = protocol_stats.get('distribution', {})
            protocol_counts = distribution.get('protocol_counts', {})
            protocol_bytes = distribution.get('protocol_bytes', {})
            total_packets = distribution.get('total_packets', 1)
            total_bytes = distribution.get('total_bytes', 1)
            
            # 写入CSV文件
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入表头
                writer.writerow([
                    '协议类型', '数据包数量', '数据包占比(%)', 
                    '字节数', '字节占比(%)', '平均包大小(字节)'
                ])
                
                # 写入数据行
                for protocol, count in protocol_counts.items():
                    bytes_count = protocol_bytes.get(protocol, 0)
                    packet_percentage = (count / total_packets) * 100 if total_packets > 0 else 0
                    bytes_percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                    avg_size = bytes_count / count if count > 0 else 0
                    
                    writer.writerow([
                        protocol,
                        count,
                        f"{packet_percentage:.2f}",
                        bytes_count,
                        f"{bytes_percentage:.2f}",
                        f"{avg_size:.1f}"
                    ])
            
            self.logger.info(f"协议统计CSV导出成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"导出协议统计CSV失败: {e}")
            raise
    
    def export_traffic_trends(self, traffic_trends: Dict[str, Any], 
                            output_filename: Optional[str] = None) -> str:
        """
        导出流量趋势数据
        
        Args:
            traffic_trends: 流量趋势数据
            output_filename: 输出文件名
            
        Returns:
            str: 生成的CSV文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"traffic_trends_{timestamp}.csv"
            
            filepath = self.output_dir / output_filename
            
            # 获取时间序列数据
            time_series = traffic_trends.get('time_series', [])
            
            # 写入CSV文件
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入表头
                writer.writerow([
                    '时间戳', '时间', '数据包数量', '字节数', '累计包数', '累计字节数'
                ])
                
                # 写入数据行
                cumulative_packets = 0
                cumulative_bytes = 0
                
                for item in time_series:
                    timestamp = item.get('timestamp', 0)
                    packet_count = item.get('packet_count', 0)
                    byte_count = item.get('byte_count', 0)
                    
                    cumulative_packets += packet_count
                    cumulative_bytes += byte_count
                    
                    time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    
                    writer.writerow([
                        timestamp,
                        time_str,
                        packet_count,
                        byte_count,
                        cumulative_packets,
                        cumulative_bytes
                    ])
            
            self.logger.info(f"流量趋势CSV导出成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"导出流量趋势CSV失败: {e}")
            raise
    
    def export_session_summary(self, session_info: Dict[str, Any], 
                             summary_stats: Dict[str, Any],
                             output_filename: Optional[str] = None) -> str:
        """
        导出会话汇总数据
        
        Args:
            session_info: 会话信息
            summary_stats: 汇总统计
            output_filename: 输出文件名
            
        Returns:
            str: 生成的CSV文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"session_summary_{timestamp}.csv"
            
            filepath = self.output_dir / output_filename
            
            # 准备汇总数据
            advanced_stats = summary_stats.get('advanced_stats', {})
            
            # 写入CSV文件
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入会话基本信息
                writer.writerow(['会话信息'])
                writer.writerow(['项目', '值'])
                writer.writerow(['会话ID', session_info.get('session_id', 'N/A')])
                writer.writerow(['会话名称', session_info.get('name', 'N/A')])
                writer.writerow(['创建时间', session_info.get('created_time', 'N/A')])
                writer.writerow(['数据包数量', session_info.get('packet_count', 0)])
                writer.writerow(['持续时间(秒)', session_info.get('duration', 0)])
                writer.writerow([])  # 空行
                
                # 写入高级统计
                writer.writerow(['高级统计'])
                writer.writerow(['指标', '值'])
                writer.writerow(['总数据包数', advanced_stats.get('total_packets', 0)])
                writer.writerow(['总字节数', advanced_stats.get('total_bytes', 0)])
                writer.writerow(['平均包大小(字节)', f"{advanced_stats.get('avg_packet_size', 0):.1f}"])
                writer.writerow(['协议多样性', advanced_stats.get('protocol_diversity', 0)])
                writer.writerow(['时间跨度(秒)', f"{advanced_stats.get('time_span', 0):.1f}"])
                writer.writerow(['平均速率(包/秒)', f"{advanced_stats.get('avg_packet_rate', 0):.1f}"])
                writer.writerow(['唯一源IP数', advanced_stats.get('unique_src_ips', 0)])
                writer.writerow(['唯一目标IP数', advanced_stats.get('unique_dst_ips', 0)])
            
            self.logger.info(f"会话汇总CSV导出成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"导出会话汇总CSV失败: {e}")
            raise
    
    def _prepare_comprehensive_data(self, report_data: Dict[str, Any]) -> List[List[str]]:
        """准备综合数据表格"""
        try:
            data = []
            
            # 添加标题行
            data.append(['网络流量分析报告 - 综合数据'])
            data.append([])  # 空行
            
            # 会话信息部分
            session_info = report_data.get('session_info', {})
            data.append(['会话信息'])
            data.append(['项目', '值'])
            data.append(['会话ID', str(session_info.get('session_id', 'N/A'))])
            data.append(['会话名称', session_info.get('name', 'N/A')])
            data.append(['创建时间', str(session_info.get('created_time', 'N/A'))])
            data.append(['数据包数量', str(session_info.get('packet_count', 0))])
            data.append(['持续时间(秒)', str(session_info.get('duration', 0))])
            data.append([])  # 空行
            
            # 协议统计部分
            protocol_stats = report_data.get('protocol_stats', {})
            distribution = protocol_stats.get('distribution', {})
            protocol_counts = distribution.get('protocol_counts', {})
            
            if protocol_counts:
                data.append(['协议统计'])
                data.append(['协议类型', '数据包数量', '字节数', '包占比(%)', '字节占比(%)'])
                
                protocol_bytes = distribution.get('protocol_bytes', {})
                total_packets = distribution.get('total_packets', 1)
                total_bytes = distribution.get('total_bytes', 1)
                
                for protocol, count in protocol_counts.items():
                    bytes_count = protocol_bytes.get(protocol, 0)
                    packet_pct = (count / total_packets) * 100 if total_packets > 0 else 0
                    bytes_pct = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                    
                    data.append([
                        protocol,
                        str(count),
                        str(bytes_count),
                        f"{packet_pct:.2f}",
                        f"{bytes_pct:.2f}"
                    ])
                
                data.append([])  # 空行
            
            # 汇总统计部分
            summary_stats = report_data.get('summary_stats', {})
            advanced_stats = summary_stats.get('advanced_stats', {})
            
            if advanced_stats:
                data.append(['汇总统计'])
                data.append(['指标', '值'])
                data.append(['总数据包数', str(advanced_stats.get('total_packets', 0))])
                data.append(['总字节数', str(advanced_stats.get('total_bytes', 0))])
                data.append(['平均包大小(字节)', f"{advanced_stats.get('avg_packet_size', 0):.1f}"])
                data.append(['协议多样性', str(advanced_stats.get('protocol_diversity', 0))])
                data.append(['时间跨度(秒)', f"{advanced_stats.get('time_span', 0):.1f}"])
                data.append(['平均速率(包/秒)', f"{advanced_stats.get('avg_packet_rate', 0):.1f}"])
                data.append(['唯一源IP数', str(advanced_stats.get('unique_src_ips', 0))])
                data.append(['唯一目标IP数', str(advanced_stats.get('unique_dst_ips', 0))])
            
            return data
            
        except Exception as e:
            self.logger.error(f"准备综合数据失败: {e}")
            return []
    
    def export_to_multiple_files(self, report_data: Dict[str, Any], 
                               base_filename: Optional[str] = None) -> Dict[str, str]:
        """
        导出为多个CSV文件
        
        Args:
            report_data: 报告数据
            base_filename: 基础文件名
            
        Returns:
            Dict[str, str]: 文件类型到路径的映射
        """
        try:
            if base_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"network_analysis_{timestamp}"
            
            exported_files = {}
            
            # 导出协议统计
            protocol_file = self.export_protocol_statistics(
                report_data.get('protocol_stats', {}),
                f"{base_filename}_protocols.csv"
            )
            exported_files['protocols'] = protocol_file
            
            # 导出流量趋势
            traffic_file = self.export_traffic_trends(
                report_data.get('traffic_trends', {}),
                f"{base_filename}_traffic.csv"
            )
            exported_files['traffic'] = traffic_file
            
            # 导出会话汇总
            summary_file = self.export_session_summary(
                report_data.get('session_info', {}),
                report_data.get('summary_stats', {}),
                f"{base_filename}_summary.csv"
            )
            exported_files['summary'] = summary_file
            
            self.logger.info(f"多文件CSV导出完成: {len(exported_files)} 个文件")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"多文件CSV导出失败: {e}")
            raise
    
    def create_csv_string(self, data: List[List[str]]) -> str:
        """
        创建CSV字符串
        
        Args:
            data: 表格数据
            
        Returns:
            str: CSV格式字符串
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            for row in data:
                writer.writerow(row)
            
            csv_string = output.getvalue()
            output.close()
            
            return csv_string
            
        except Exception as e:
            self.logger.error(f"创建CSV字符串失败: {e}")
            return ""
    
    def validate_csv_data(self, data: List[List[str]]) -> bool:
        """
        验证CSV数据的有效性
        
        Args:
            data: 表格数据
            
        Returns:
            bool: 数据是否有效
        """
        try:
            if not data:
                return False
            
            # 检查是否有表头
            if len(data) < 2:
                return False
            
            # 检查列数一致性
            header_cols = len(data[0])
            for row in data[1:]:
                if len(row) != header_cols:
                    self.logger.warning(f"行列数不一致: 期望{header_cols}列，实际{len(row)}列")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证CSV数据失败: {e}")
            return False
    
    def format_data_for_excel(self, data: List[List[Any]]) -> List[List[str]]:
        """
        格式化数据以兼容Excel
        
        Args:
            data: 原始数据
            
        Returns:
            List[List[str]]: 格式化后的数据
        """
        try:
            formatted_data = []
            
            for row in data:
                formatted_row = []
                for cell in row:
                    if isinstance(cell, (int, float)):
                        # 数字类型保持原样
                        formatted_row.append(str(cell))
                    elif isinstance(cell, datetime):
                        # 日期时间格式化
                        formatted_row.append(cell.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        # 其他类型转为字符串
                        formatted_row.append(str(cell) if cell is not None else '')
                
                formatted_data.append(formatted_row)
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"格式化Excel数据失败: {e}")
            return data
    
    def get_export_info(self, filepath: str) -> Dict[str, Any]:
        """
        获取导出文件信息
        
        Args:
            filepath: 文件路径
            
        Returns:
            Dict: 文件信息
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return {'exists': False}
            
            # 读取文件统计行数
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                row_count = sum(1 for row in reader)
            
            stat = path.stat()
            return {
                'exists': True,
                'filename': path.name,
                'size': stat.st_size,
                'size_kb': stat.st_size / 1024,
                'row_count': row_count,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime)
            }
            
        except Exception as e:
            self.logger.error(f"获取导出文件信息失败: {e}")
            return {'exists': False, 'error': str(e)}
    
    def cleanup_old_exports(self, keep_days: int = 30):
        """
        清理旧的导出文件
        
        Args:
            keep_days: 保留天数
        """
        try:
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (keep_days * 24 * 3600)
            
            for file_path in self.output_dir.glob("*.csv"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    self.logger.debug(f"删除旧CSV文件: {file_path}")
            
        except Exception as e:
            self.logger.error(f"清理旧CSV文件失败: {e}")