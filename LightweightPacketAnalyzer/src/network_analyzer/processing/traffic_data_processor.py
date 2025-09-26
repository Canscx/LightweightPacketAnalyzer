"""
流量数据处理器

提供流量数据的聚合、分组和计算功能。
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict


class TrafficDataProcessor:
    """流量数据处理器，负责数据聚合和统计计算"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.logger = logging.getLogger(__name__)
    
    def aggregate_by_seconds(self, packets: List[Dict[str, Any]]) -> Dict[int, Dict[str, Dict[str, int]]]:
        """
        按秒聚合数据包统计
        
        Args:
            packets: 数据包列表
            
        Returns:
            {
                timestamp_int: {
                    'TCP': {'count': 10, 'bytes': 1024},
                    'UDP': {'count': 5, 'bytes': 512},
                    ...
                }
            }
        """
        try:
            aggregated = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'bytes': 0}))
            
            for packet in packets:
                # 获取时间戳（秒级）
                timestamp = packet.get('timestamp', 0)
                time_bucket = int(timestamp)
                
                # 获取协议和长度
                protocol = packet.get('protocol', 'Unknown')
                length = packet.get('length', 0)
                
                # 聚合统计
                aggregated[time_bucket][protocol]['count'] += 1
                aggregated[time_bucket][protocol]['bytes'] += length
            
            return dict(aggregated)
            
        except Exception as e:
            self.logger.error(f"按秒聚合数据失败: {e}")
            return {}
    
    def calculate_bandwidth(self, packets: List[Dict[str, Any]], 
                          time_window: int = 1) -> Dict[str, float]:
        """
        计算带宽（字节/秒）
        
        Args:
            packets: 数据包列表
            time_window: 时间窗口（秒）
            
        Returns:
            {'TCP': 1024.5, 'UDP': 512.0, ...}
        """
        try:
            if not packets:
                return {}
            
            # 按协议分组计算总字节数
            protocol_bytes = defaultdict(int)
            
            # 获取时间范围
            timestamps = [packet.get('timestamp', 0) for packet in packets]
            if not timestamps:
                return {}
            
            min_time = min(timestamps)
            max_time = max(timestamps)
            duration = max(max_time - min_time, time_window)
            
            # 计算每个协议的总字节数
            for packet in packets:
                protocol = packet.get('protocol', 'Unknown')
                length = packet.get('length', 0)
                protocol_bytes[protocol] += length
            
            # 计算带宽（字节/秒）
            bandwidth = {}
            for protocol, total_bytes in protocol_bytes.items():
                bandwidth[protocol] = total_bytes / duration
            
            return bandwidth
            
        except Exception as e:
            self.logger.error(f"计算带宽失败: {e}")
            return {}
    
    def group_by_protocol(self, packets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        按协议分组数据包
        
        Args:
            packets: 数据包列表
            
        Returns:
            {
                'TCP': [packet1, packet2, ...],
                'UDP': [packet3, packet4, ...],
                ...
            }
        """
        try:
            grouped = defaultdict(list)
            
            for packet in packets:
                protocol = packet.get('protocol', 'Unknown')
                grouped[protocol].append(packet)
            
            return dict(grouped)
            
        except Exception as e:
            self.logger.error(f"按协议分组失败: {e}")
            return {}
    
    def calculate_protocol_statistics(self, packets: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        计算协议统计信息
        
        Args:
            packets: 数据包列表
            
        Returns:
            {
                'TCP': {
                    'count': 100,
                    'bytes': 10240,
                    'percentage': 66.7,
                    'avg_size': 102.4
                },
                ...
            }
        """
        try:
            if not packets:
                return {}
            
            # 按协议分组
            protocol_groups = self.group_by_protocol(packets)
            
            # 计算总数
            total_packets = len(packets)
            total_bytes = sum(packet.get('length', 0) for packet in packets)
            
            # 计算每个协议的统计信息
            statistics = {}
            for protocol, protocol_packets in protocol_groups.items():
                packet_count = len(protocol_packets)
                protocol_bytes = sum(packet.get('length', 0) for packet in protocol_packets)
                
                statistics[protocol] = {
                    'count': packet_count,
                    'bytes': protocol_bytes,
                    'percentage': (packet_count / total_packets * 100) if total_packets > 0 else 0,
                    'avg_size': (protocol_bytes / packet_count) if packet_count > 0 else 0
                }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"计算协议统计失败: {e}")
            return {}
    
    def generate_time_series(self, 
                           start_time: datetime, 
                           end_time: datetime, 
                           interval_seconds: int = 1) -> List[datetime]:
        """
        生成时间序列
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            interval_seconds: 间隔秒数
            
        Returns:
            时间点列表
        """
        try:
            timestamps = []
            current_time = start_time
            
            while current_time <= end_time:
                timestamps.append(current_time)
                current_time += timedelta(seconds=interval_seconds)
            
            return timestamps
            
        except Exception as e:
            self.logger.error(f"生成时间序列失败: {e}")
            return []
    
    def fill_missing_data_points(self, 
                                data: Dict[str, List[int]], 
                                timestamps: List[datetime],
                                fill_value: int = 0) -> Dict[str, List[int]]:
        """
        填充缺失的数据点
        
        Args:
            data: 原始数据
            timestamps: 完整时间序列
            fill_value: 填充值
            
        Returns:
            填充后的数据
        """
        try:
            filled_data = {}
            expected_length = len(timestamps)
            
            for protocol, values in data.items():
                if len(values) < expected_length:
                    # 扩展到期望长度
                    filled_values = values + [fill_value] * (expected_length - len(values))
                    filled_data[protocol] = filled_values
                else:
                    filled_data[protocol] = values[:expected_length]
            
            return filled_data
            
        except Exception as e:
            self.logger.error(f"填充缺失数据点失败: {e}")
            return data
    
    def smooth_data(self, 
                   data: List[float], 
                   window_size: int = 3) -> List[float]:
        """
        数据平滑处理（移动平均）
        
        Args:
            data: 原始数据
            window_size: 窗口大小
            
        Returns:
            平滑后的数据
        """
        try:
            if len(data) < window_size:
                return data
            
            smoothed = []
            half_window = window_size // 2
            
            for i in range(len(data)):
                start_idx = max(0, i - half_window)
                end_idx = min(len(data), i + half_window + 1)
                
                window_data = data[start_idx:end_idx]
                avg_value = sum(window_data) / len(window_data)
                smoothed.append(avg_value)
            
            return smoothed
            
        except Exception as e:
            self.logger.error(f"数据平滑处理失败: {e}")
            return data
    
    def detect_anomalies(self, 
                        data: List[float], 
                        threshold_factor: float = 2.0) -> List[bool]:
        """
        检测异常数据点
        
        Args:
            data: 数据序列
            threshold_factor: 阈值因子
            
        Returns:
            异常标记列表（True表示异常）
        """
        try:
            if len(data) < 3:
                return [False] * len(data)
            
            # 计算均值和标准差
            mean_value = sum(data) / len(data)
            variance = sum((x - mean_value) ** 2 for x in data) / len(data)
            std_dev = variance ** 0.5
            
            # 检测异常
            anomalies = []
            threshold = threshold_factor * std_dev
            
            for value in data:
                is_anomaly = abs(value - mean_value) > threshold
                anomalies.append(is_anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
            return [False] * len(data)