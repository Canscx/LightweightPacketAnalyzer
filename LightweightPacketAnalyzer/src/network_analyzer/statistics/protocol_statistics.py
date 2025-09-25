"""
协议统计核心类

提供协议分布统计、流量分析、时间序列分析等功能
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class StatisticsFilter:
    """统计过滤器"""
    session_id: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    protocols: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'protocols': self.protocols
        }


@dataclass
class ProtocolDistribution:
    """协议分布统计结果"""
    protocol_counts: Dict[str, int]
    protocol_bytes: Dict[str, int]
    protocol_percentages: Dict[str, float]
    total_packets: int
    total_bytes: int
    time_range: Dict[str, Optional[float]]
    
    def get_top_protocols(self, limit: int = 5, by_packets: bool = True) -> List[Tuple[str, int]]:
        """获取Top协议列表"""
        data = self.protocol_counts if by_packets else self.protocol_bytes
        return sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_protocol_percentage(self, protocol: str, by_packets: bool = True) -> float:
        """获取指定协议的百分比"""
        if by_packets:
            total = self.total_packets
            count = self.protocol_counts.get(protocol, 0)
        else:
            total = self.total_bytes
            count = self.protocol_bytes.get(protocol, 0)
        
        return (count / total * 100) if total > 0 else 0.0


@dataclass
class TimeSeriesData:
    """时间序列数据"""
    timestamps: List[float]
    values: List[int]
    protocol: str
    interval: int  # 时间间隔（秒）
    
    def get_peak_time(self) -> Optional[float]:
        """获取峰值时间"""
        if not self.values:
            return None
        max_index = self.values.index(max(self.values))
        return self.timestamps[max_index]
    
    def get_average_rate(self) -> float:
        """获取平均速率"""
        if not self.values or len(self.timestamps) < 2:
            return 0.0
        
        total_time = self.timestamps[-1] - self.timestamps[0]
        total_packets = sum(self.values)
        return total_packets / total_time if total_time > 0 else 0.0


class ProtocolStatistics:
    """协议统计核心类"""
    
    def __init__(self, data_manager):
        """
        初始化协议统计类
        
        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
    def get_protocol_distribution(self, filter_params: Optional[StatisticsFilter] = None) -> ProtocolDistribution:
        """
        获取协议分布统计
        
        Args:
            filter_params: 过滤参数
            
        Returns:
            ProtocolDistribution: 协议分布统计结果
        """
        try:
            # 构建查询参数
            query_params = {}
            if filter_params:
                if filter_params.session_id is not None:
                    query_params['session_id'] = filter_params.session_id
                if filter_params.start_time is not None:
                    query_params['start_time'] = filter_params.start_time
                if filter_params.end_time is not None:
                    query_params['end_time'] = filter_params.end_time
            
            # 获取统计数据
            stats = self.data_manager.get_protocol_statistics(**query_params)
            
            protocol_counts = stats['protocol_counts']
            protocol_bytes = stats['protocol_bytes']
            total_packets = stats['total_packets']
            total_bytes = stats['total_bytes'] or 0
            time_range = stats['time_range']
            
            # 过滤指定协议
            if filter_params and filter_params.protocols:
                filtered_counts = {p: protocol_counts.get(p, 0) for p in filter_params.protocols}
                filtered_bytes = {p: protocol_bytes.get(p, 0) for p in filter_params.protocols}
                protocol_counts = filtered_counts
                protocol_bytes = filtered_bytes
                total_packets = sum(filtered_counts.values())
                total_bytes = sum(filtered_bytes.values())
            
            # 计算百分比
            protocol_percentages = {}
            if total_packets > 0:
                for protocol, count in protocol_counts.items():
                    protocol_percentages[protocol] = (count / total_packets) * 100
            
            return ProtocolDistribution(
                protocol_counts=protocol_counts,
                protocol_bytes=protocol_bytes,
                protocol_percentages=protocol_percentages,
                total_packets=total_packets,
                total_bytes=total_bytes,
                time_range=time_range
            )
            
        except Exception as e:
            self.logger.error(f"获取协议分布统计失败: {e}")
            # 返回空结果
            return ProtocolDistribution(
                protocol_counts={},
                protocol_bytes={},
                protocol_percentages={},
                total_packets=0,
                total_bytes=0,
                time_range={'start': None, 'end': None}
            )
    
    def get_time_series_data(self, 
                           protocol: str, 
                           interval: int = 60,
                           filter_params: Optional[StatisticsFilter] = None) -> TimeSeriesData:
        """
        获取协议时间序列数据
        
        Args:
            protocol: 协议名称
            interval: 时间间隔（秒）
            filter_params: 过滤参数
            
        Returns:
            TimeSeriesData: 时间序列数据
        """
        try:
            # 构建查询参数
            query_params = {}
            if filter_params:
                if filter_params.session_id is not None:
                    query_params['session_id'] = filter_params.session_id
                if filter_params.start_time is not None:
                    query_params['start_time'] = filter_params.start_time
                if filter_params.end_time is not None:
                    query_params['end_time'] = filter_params.end_time
            
            # 获取数据包
            packets = self.data_manager.get_packets(**query_params)
            
            # 过滤指定协议的数据包
            protocol_packets = [p for p in packets if p.get('protocol') == protocol]
            
            if not protocol_packets:
                return TimeSeriesData(
                    timestamps=[],
                    values=[],
                    protocol=protocol,
                    interval=interval
                )
            
            # 获取时间范围
            timestamps = [p['timestamp'] for p in protocol_packets]
            min_time = min(timestamps)
            max_time = max(timestamps)
            
            # 生成时间序列
            time_slots = []
            current_time = min_time
            while current_time <= max_time:
                time_slots.append(current_time)
                current_time += interval
            
            # 如果只有一个时间槽，添加一个结束时间槽
            if len(time_slots) == 1:
                time_slots.append(time_slots[0] + interval)
            
            # 统计每个时间槽的数据包数量
            slot_counts = [0] * len(time_slots)
            
            for packet in protocol_packets:
                packet_time = packet['timestamp']
                # 找到对应的时间槽
                slot_index = int((packet_time - min_time) // interval)
                if 0 <= slot_index < len(slot_counts):
                    slot_counts[slot_index] += 1
            
            return TimeSeriesData(
                timestamps=time_slots,
                values=slot_counts,
                protocol=protocol,
                interval=interval
            )
            
        except Exception as e:
            self.logger.error(f"获取时间序列数据失败: {e}")
            return TimeSeriesData(
                timestamps=[],
                values=[],
                protocol=protocol,
                interval=interval
            )
    
    def get_protocol_comparison(self, 
                              protocols: List[str],
                              filter_params: Optional[StatisticsFilter] = None) -> Dict[str, ProtocolDistribution]:
        """
        获取多协议对比统计
        
        Args:
            protocols: 协议列表
            filter_params: 过滤参数
            
        Returns:
            Dict[str, ProtocolDistribution]: 各协议的统计结果
        """
        try:
            results = {}
            
            for protocol in protocols:
                # 为每个协议创建过滤器
                protocol_filter = StatisticsFilter(
                    session_id=filter_params.session_id if filter_params else None,
                    start_time=filter_params.start_time if filter_params else None,
                    end_time=filter_params.end_time if filter_params else None,
                    protocols=[protocol]
                )
                
                # 获取该协议的统计数据
                distribution = self.get_protocol_distribution(protocol_filter)
                results[protocol] = distribution
            
            return results
            
        except Exception as e:
            self.logger.error(f"获取协议对比统计失败: {e}")
            return {}
    
    def get_traffic_summary(self, filter_params: Optional[StatisticsFilter] = None) -> Dict[str, Any]:
        """
        获取流量摘要统计
        
        Args:
            filter_params: 过滤参数
            
        Returns:
            Dict[str, Any]: 流量摘要数据
        """
        try:
            # 获取协议分布
            distribution = self.get_protocol_distribution(filter_params)
            
            # 获取Top协议
            top_protocols_by_packets = distribution.get_top_protocols(limit=5, by_packets=True)
            top_protocols_by_bytes = distribution.get_top_protocols(limit=5, by_packets=False)
            
            # 计算平均包大小
            avg_packet_size = 0
            if distribution.total_packets > 0:
                avg_packet_size = distribution.total_bytes / distribution.total_packets
            
            # 计算时间跨度和速率
            time_span = 0
            packet_rate = 0
            byte_rate = 0
            
            if (distribution.time_range['start'] is not None and 
                distribution.time_range['end'] is not None):
                time_span = distribution.time_range['end'] - distribution.time_range['start']
                if time_span > 0:
                    packet_rate = distribution.total_packets / time_span
                    byte_rate = distribution.total_bytes / time_span
            
            return {
                'total_packets': distribution.total_packets,
                'total_bytes': distribution.total_bytes,
                'protocol_count': len(distribution.protocol_counts),
                'avg_packet_size': avg_packet_size,
                'time_span': time_span,
                'packet_rate': packet_rate,  # 包/秒
                'byte_rate': byte_rate,      # 字节/秒
                'top_protocols_by_packets': top_protocols_by_packets,
                'top_protocols_by_bytes': top_protocols_by_bytes,
                'time_range': distribution.time_range
            }
            
        except Exception as e:
            self.logger.error(f"获取流量摘要失败: {e}")
            return {
                'total_packets': 0,
                'total_bytes': 0,
                'protocol_count': 0,
                'avg_packet_size': 0,
                'time_span': 0,
                'packet_rate': 0,
                'byte_rate': 0,
                'top_protocols_by_packets': [],
                'top_protocols_by_bytes': [],
                'time_range': {'start': None, 'end': None}
            }
    
    def export_statistics(self, 
                         filter_params: Optional[StatisticsFilter] = None,
                         include_time_series: bool = False,
                         time_interval: int = 60) -> Dict[str, Any]:
        """
        导出统计数据
        
        Args:
            filter_params: 过滤参数
            include_time_series: 是否包含时间序列数据
            time_interval: 时间序列间隔（秒）
            
        Returns:
            Dict[str, Any]: 导出的统计数据
        """
        try:
            # 获取基础统计
            distribution = self.get_protocol_distribution(filter_params)
            summary = self.get_traffic_summary(filter_params)
            
            export_data = {
                'export_time': time.time(),
                'filter_params': filter_params.to_dict() if filter_params else {},
                'protocol_distribution': {
                    'protocol_counts': distribution.protocol_counts,
                    'protocol_bytes': distribution.protocol_bytes,
                    'protocol_percentages': distribution.protocol_percentages,
                    'total_packets': distribution.total_packets,
                    'total_bytes': distribution.total_bytes,
                    'time_range': distribution.time_range
                },
                'traffic_summary': summary
            }
            
            # 添加时间序列数据
            if include_time_series and distribution.protocol_counts:
                time_series_data = {}
                for protocol in distribution.protocol_counts.keys():
                    ts_data = self.get_time_series_data(protocol, time_interval, filter_params)
                    time_series_data[protocol] = {
                        'timestamps': ts_data.timestamps,
                        'values': ts_data.values,
                        'interval': ts_data.interval,
                        'peak_time': ts_data.get_peak_time(),
                        'average_rate': ts_data.get_average_rate()
                    }
                export_data['time_series'] = time_series_data
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"导出统计数据失败: {e}")
            return {
                'export_time': time.time(),
                'error': str(e),
                'filter_params': filter_params.to_dict() if filter_params else {},
                'protocol_distribution': {},
                'traffic_summary': {}
            }