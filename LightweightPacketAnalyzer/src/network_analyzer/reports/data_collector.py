"""
报告数据收集器

统一收集报告生成所需的各种数据，包括：
- 会话信息
- 协议统计数据
- 流量趋势数据
- 数据包详情
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

import time
from ..storage.data_manager import DataManager
from ..statistics.protocol_statistics import ProtocolStatistics, StatisticsFilter
from ..processing.traffic_data_processor import TrafficDataProcessor


logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """会话信息数据类"""
    session_id: int
    name: str
    created_time: datetime
    packet_count: int
    duration: float
    file_path: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ReportData:
    """报告数据容器"""
    session_info: SessionInfo
    protocol_stats: Dict[str, Any]
    traffic_trends: Dict[str, Any]
    summary_stats: Dict[str, Any]
    generation_time: datetime


class DataCollector:
    """报告数据收集器"""
    
    def __init__(self, data_manager: DataManager):
        """
        初始化数据收集器
        
        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
        self.protocol_stats = ProtocolStatistics(data_manager)
        self.traffic_processor = TrafficDataProcessor()
        self.logger = logging.getLogger(__name__)
    
    def collect_session_data(self, session_id: int) -> ReportData:
        """
        收集指定会话的完整报告数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            ReportData: 完整的报告数据
            
        Raises:
            ValueError: 会话不存在或数据无效
            RuntimeError: 数据收集过程中出现错误
        """
        try:
            self.logger.info(f"开始收集会话 {session_id} 的报告数据")
            
            # 收集会话基本信息
            session_info = self._collect_session_info(session_id)
            
            # 收集协议统计数据
            protocol_stats = self._collect_protocol_statistics(session_id)
            
            # 收集流量趋势数据
            traffic_trends = self._collect_traffic_trends(session_id)
            
            # 收集汇总统计
            summary_stats = self._collect_summary_statistics(session_id)
            
            # 构建报告数据
            report_data = ReportData(
                session_info=session_info,
                protocol_stats=protocol_stats,
                traffic_trends=traffic_trends,
                summary_stats=summary_stats,
                generation_time=datetime.now()
            )
            
            self.logger.info(f"会话 {session_id} 数据收集完成")
            return report_data
            
        except Exception as e:
            self.logger.error(f"收集会话 {session_id} 数据时出错: {e}")
            raise RuntimeError(f"数据收集失败: {e}")
    
    def _collect_session_info(self, session_id: int) -> SessionInfo:
        """收集会话基本信息"""
        try:
            # 从数据库获取会话信息
            sessions = self.data_manager.get_sessions()
            session_data = None
            
            for session in sessions:
                if session.get('id') == session_id:
                    session_data = session
                    break
            
            if not session_data:
                raise ValueError(f"会话 {session_id} 不存在")
            
            # 获取数据包数量
            packets = self.data_manager.get_packets_by_session(session_id)
            packet_count = len(packets)
            
            # 计算会话持续时间
            duration = 0.0
            if packets:
                timestamps = [p.get('timestamp', 0) for p in packets if p.get('timestamp')]
                if timestamps:
                    duration = max(timestamps) - min(timestamps)
            
            # 安全处理时间戳
            created_at = session_data.get('created_at', time.time())
            if isinstance(created_at, str):
                try:
                    created_at = float(created_at)
                except (ValueError, TypeError):
                    created_at = time.time()
            
            return SessionInfo(
                session_id=session_id,
                name=session_data.get('name', f'会话_{session_id}'),
                created_time=datetime.fromtimestamp(created_at),
                packet_count=packet_count,
                duration=duration,
                file_path=session_data.get('file_path'),
                description=session_data.get('description')
            )
            
        except Exception as e:
            self.logger.error(f"收集会话信息失败: {e}")
            raise
    
    def _collect_protocol_statistics(self, session_id: int) -> Dict[str, Any]:
        """收集协议统计数据"""
        try:
            # 创建过滤器
            filter_obj = StatisticsFilter(session_id=session_id)
            
            # 获取协议分布
            distribution = self.protocol_stats.get_protocol_distribution(filter_obj)
            
            # 获取流量汇总
            traffic_summary = self.protocol_stats.get_traffic_summary(filter_obj)
            
            return {
                'distribution': asdict(distribution),
                'traffic_summary': traffic_summary,
                'top_protocols_by_count': distribution.get_top_protocols(limit=10, by_packets=True),
                'top_protocols_by_bytes': distribution.get_top_protocols(limit=10, by_packets=False)
            }
            
        except Exception as e:
            self.logger.error(f"收集协议统计数据失败: {e}")
            raise
    
    def _collect_traffic_trends(self, session_id: int) -> Dict[str, Any]:
        """收集流量趋势数据"""
        try:
            # 获取会话的数据包
            packets = self.data_manager.get_packets_by_session(session_id)
            
            if not packets:
                return {'trends_data': {}, 'peak_info': {}, 'time_series': []}
            
            # 使用流量处理器分析数据
            aggregated_data = self.traffic_processor.aggregate_by_seconds(packets)
            bandwidth_data = self.traffic_processor.calculate_bandwidth(packets)
            
            # 构建时间序列数据
            time_series = []
            for timestamp, protocol_data in aggregated_data.items():
                total_packets = sum(proto_stats['count'] for proto_stats in protocol_data.values())
                total_bytes = sum(proto_stats['bytes'] for proto_stats in protocol_data.values())
                
                time_series.append({
                    'timestamp': timestamp,
                    'packet_count': total_packets,
                    'byte_count': total_bytes
                })
            
            # 排序时间序列
            time_series.sort(key=lambda x: x['timestamp'])
            
            # 计算峰值信息
            peak_info = self._calculate_peak_info(time_series)
            
            return {
                'trends_data': aggregated_data,
                'peak_info': peak_info,
                'time_series': time_series,
                'bandwidth_data': bandwidth_data
            }
            
        except Exception as e:
            self.logger.error(f"收集流量趋势数据失败: {e}")
            raise
    
    def _collect_summary_statistics(self, session_id: int) -> Dict[str, Any]:
        """收集汇总统计数据"""
        try:
            # 获取基本统计（从数据库信息中获取）
            db_info = self.data_manager.get_database_info()
            basic_stats = {
                'total_packets_in_db': db_info.get('packet_count', 0),
                'total_sessions': db_info.get('session_count', 0)
            }
            
            # 计算高级统计指标
            advanced_stats = self._calculate_advanced_statistics(session_id)
            
            return {
                'basic_stats': basic_stats,
                'advanced_stats': advanced_stats
            }
            
        except Exception as e:
            self.logger.error(f"收集汇总统计数据失败: {e}")
            raise
    
    def _calculate_advanced_statistics(self, session_id: int) -> Dict[str, Any]:
        """计算高级统计指标"""
        try:
            # 获取数据包信息
            packets = self.data_manager.get_packets_by_session(session_id)
            
            if not packets:
                return {}
            
            # 计算各种统计指标
            total_packets = len(packets)
            total_bytes = sum(p.get('length', 0) for p in packets)
            
            # 计算平均包大小
            avg_packet_size = total_bytes / total_packets if total_packets > 0 else 0
            
            # 计算协议多样性
            protocols = set(p.get('protocol', 'Unknown') for p in packets)
            protocol_diversity = len(protocols)
            
            # 计算时间跨度
            timestamps = [p.get('timestamp', 0) for p in packets if p.get('timestamp')]
            time_span = max(timestamps) - min(timestamps) if timestamps else 0
            
            # 计算平均速率
            avg_rate = total_packets / time_span if time_span > 0 else 0
            
            return {
                'total_packets': total_packets,
                'total_bytes': total_bytes,
                'avg_packet_size': avg_packet_size,
                'protocol_diversity': protocol_diversity,
                'time_span': time_span,
                'avg_packet_rate': avg_rate,
                'unique_src_ips': len(set(p.get('src_ip', '') for p in packets if p.get('src_ip'))),
                'unique_dst_ips': len(set(p.get('dst_ip', '') for p in packets if p.get('dst_ip'))),
            }
            
        except Exception as e:
            self.logger.error(f"计算高级统计指标失败: {e}")
            return {}
    
    def _calculate_peak_info(self, time_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算峰值信息"""
        try:
            if not time_series:
                return {}
            
            # 找到峰值
            max_packets = max(item['packet_count'] for item in time_series)
            max_bytes = max(item['byte_count'] for item in time_series)
            
            # 找到峰值时间
            peak_time_item = max(time_series, key=lambda x: x['packet_count'])
            peak_time = datetime.fromtimestamp(peak_time_item['timestamp']).strftime('%H:%M:%S')
            
            # 计算平均值
            avg_packets = sum(item['packet_count'] for item in time_series) / len(time_series)
            avg_bytes = sum(item['byte_count'] for item in time_series) / len(time_series)
            
            return {
                'max_packets': max_packets,
                'max_bytes': max_bytes,
                'peak_time': peak_time,
                'avg_packets': avg_packets,
                'avg_bytes': avg_bytes
            }
            
        except Exception as e:
            self.logger.error(f"计算峰值信息失败: {e}")
            return {}
    
    def validate_session_data(self, session_id: int) -> bool:
        """
        验证会话数据的完整性
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 数据是否有效
        """
        try:
            # 检查会话是否存在
            sessions = self.data_manager.get_sessions()
            session_exists = any(s.get('id') == session_id for s in sessions)
            
            if not session_exists:
                return False
            
            # 检查是否有数据包
            packets = self.data_manager.get_packets_by_session(session_id)
            if len(packets) == 0:
                self.logger.warning(f"会话 {session_id} 没有数据包")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证会话数据失败: {e}")
            return False
    
    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的会话列表
        
        Returns:
            List[Dict]: 会话信息列表
        """
        try:
            return self.data_manager.get_sessions()
        except Exception as e:
            self.logger.error(f"获取会话列表失败: {e}")
            return []