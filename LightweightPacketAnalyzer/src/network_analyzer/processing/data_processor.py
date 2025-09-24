"""
网络数据处理模块

提供数据包分析、统计计算和流量分析功能。
"""

import threading
import queue
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import statistics
import time

from ..config.settings import Settings
from ..storage.data_manager import DataManager


class DataProcessor:
    """网络数据处理类"""
    
    def __init__(self, settings: Settings, data_manager: DataManager):
        """
        初始化数据处理器
        
        Args:
            settings: 配置对象
            data_manager: 数据管理器
        """
        self.settings = settings
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # 线程安全锁
        self._lock = threading.RLock()
        
        # 异步数据库写入相关
        self._db_queue = queue.Queue(maxsize=1000)  # 限制队列大小防止内存溢出
        self._db_thread = None
        self._db_thread_running = False
        self._batch_size = 50  # 批量写入大小
        self._batch_timeout = 2.0  # 批量写入超时时间（秒）
        
        # 实时统计数据
        self._packet_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'protocol_counts': defaultdict(int),
            'protocol_bytes': defaultdict(int),
            'ip_counts': defaultdict(int),
            'port_counts': defaultdict(int),
            'start_time': None,
            'last_update': None
        }
        
        # 流量统计（时间窗口）
        self._traffic_window = deque(maxlen=300)  # 保留5分钟的数据（每秒一个点）
        self._current_second_stats = {
            'timestamp': None,
            'packet_count': 0,
            'byte_count': 0
        }
        
        # 连接跟踪
        self._connections = {}  # (src_ip, dst_ip, src_port, dst_port, protocol) -> connection_info
        
        # 异常检测
        self._baseline_stats = {
            'avg_packet_rate': 0.0,
            'avg_byte_rate': 0.0,
            'protocol_distribution': {},
            'port_distribution': {}
        }
        
        # 启动数据库写入线程
        self._start_db_thread()

    def _start_db_thread(self) -> None:
        """启动数据库写入线程"""
        if self._db_thread is None or not self._db_thread.is_alive():
            self._db_thread_running = True
            self._db_thread = threading.Thread(target=self._db_worker, daemon=True)
            self._db_thread.start()
            self.logger.info("数据库写入线程已启动")

    def _stop_db_thread(self) -> None:
        """停止数据库写入线程"""
        if self._db_thread_running:
            self._db_thread_running = False
            # 发送停止信号
            try:
                self._db_queue.put(None, timeout=1.0)
            except queue.Full:
                pass
            
            # 等待线程结束
            if self._db_thread and self._db_thread.is_alive():
                self._db_thread.join(timeout=5.0)
            
            self.logger.info("数据库写入线程已停止")

    def _db_worker(self) -> None:
        """数据库写入工作线程"""
        batch = []
        last_batch_time = time.time()
        
        while self._db_thread_running:
            try:
                # 尝试获取数据包数据
                timeout = max(0.1, self._batch_timeout - (time.time() - last_batch_time))
                packet_data = self._db_queue.get(timeout=timeout)
                
                # 检查停止信号
                if packet_data is None:
                    break
                
                batch.append(packet_data)
                
                # 检查是否需要批量写入
                current_time = time.time()
                should_flush = (
                    len(batch) >= self._batch_size or 
                    (current_time - last_batch_time) >= self._batch_timeout
                )
                
                if should_flush and batch:
                    self._flush_batch(batch)
                    batch.clear()
                    last_batch_time = current_time
                    
            except queue.Empty:
                # 超时，检查是否有待写入的数据
                if batch:
                    self._flush_batch(batch)
                    batch.clear()
                    last_batch_time = time.time()
            except Exception as e:
                self.logger.error(f"数据库写入线程错误: {e}")
        
        # 线程结束前写入剩余数据
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch: List[Dict[str, Any]]) -> None:
        """批量写入数据到数据库"""
        try:
            if len(batch) == 1:
                # 单个数据包直接写入
                self.data_manager.save_packet(batch[0])
            else:
                # 批量写入（如果数据管理器支持）
                if hasattr(self.data_manager, 'save_packets_batch'):
                    self.data_manager.save_packets_batch(batch)
                else:
                    # 逐个写入
                    for packet_data in batch:
                        self.data_manager.save_packet(packet_data)
            
            self.logger.debug(f"成功写入 {len(batch)} 个数据包到数据库")
            
        except Exception as e:
            self.logger.error(f"批量写入数据库失败: {e}")

    def process_packet(self, packet_info: Dict[str, Any]) -> None:
        """
        处理单个数据包
        
        Args:
            packet_info: 数据包信息字典
        """
        with self._lock:
            try:
                # 更新基础统计（快速操作，保留在主线程）
                self._update_basic_stats(packet_info)
                
                # 更新流量统计
                self._update_traffic_stats(packet_info)
                
                # 更新连接跟踪
                self._update_connection_tracking(packet_info)
                
                # 异步存储数据包到数据库
                self._store_packet_async(packet_info)
                
                # 检测异常
                self._detect_anomalies(packet_info)
                
            except Exception as e:
                self.logger.error(f"处理数据包失败: {e}")

    def _store_packet_async(self, packet_info: Dict[str, Any]) -> None:
        """异步存储数据包到数据库"""
        try:
            # 构造数据包数据
            packet_data = {
                'timestamp': packet_info.get('timestamp', datetime.now().timestamp()),
                'src_ip': packet_info.get('src_ip', ''),
                'dst_ip': packet_info.get('dst_ip', ''),
                'src_port': packet_info.get('src_port', 0),
                'dst_port': packet_info.get('dst_port', 0),
                'protocol': packet_info.get('protocol', 'Unknown'),
                'length': packet_info.get('length', 0),
                'summary': packet_info.get('summary', '')
            }
            
            # 添加到异步写入队列
            try:
                self._db_queue.put_nowait(packet_data)
            except queue.Full:
                # 队列满时丢弃最旧的数据包
                try:
                    self._db_queue.get_nowait()  # 移除一个旧数据包
                    self._db_queue.put_nowait(packet_data)  # 添加新数据包
                    self.logger.warning("数据库队列已满，丢弃旧数据包")
                except queue.Empty:
                    pass
            
        except Exception as e:
            self.logger.error(f"异步存储数据包失败: {e}")

    def _update_basic_stats(self, packet_info: Dict[str, Any]) -> None:
        """更新基础统计信息"""
        timestamp = packet_info.get('timestamp', datetime.now())
        # 确保timestamp是datetime对象
        if isinstance(timestamp, datetime):
            timestamp_dt = timestamp
        else:
            # 如果是时间戳，转换为datetime对象
            timestamp_dt = datetime.fromtimestamp(timestamp)
        length = packet_info.get('length', 0)
        protocol = packet_info.get('protocol', 'Unknown')
        src_ip = packet_info.get('src_ip')
        dst_ip = packet_info.get('dst_ip')
        src_port = packet_info.get('src_port')
        dst_port = packet_info.get('dst_port')
        
        # 更新总计数
        self._packet_stats['total_packets'] += 1
        self._packet_stats['total_bytes'] += length
        self._packet_stats['last_update'] = timestamp_dt
        
        if self._packet_stats['start_time'] is None:
            self._packet_stats['start_time'] = timestamp_dt
        
        # 更新协议统计
        self._packet_stats['protocol_counts'][protocol] += 1
        self._packet_stats['protocol_bytes'][protocol] += length
        
        # 更新IP统计
        if src_ip:
            self._packet_stats['ip_counts'][src_ip] += 1
        if dst_ip:
            self._packet_stats['ip_counts'][dst_ip] += 1
        
        # 更新端口统计
        if src_port:
            self._packet_stats['port_counts'][src_port] += 1
        if dst_port:
            self._packet_stats['port_counts'][dst_port] += 1
    
    def _update_traffic_stats(self, packet_info: Dict[str, Any]) -> None:
        """更新流量统计信息"""
        timestamp = packet_info.get('timestamp', datetime.now().timestamp())
        length = packet_info.get('length', 0)
        
        # 如果timestamp是float，转换为datetime对象
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp)
        
        # 获取当前秒的时间戳
        current_second = timestamp.replace(microsecond=0)
        
        # 如果是新的一秒，保存上一秒的数据并重置
        if (self._current_second_stats['timestamp'] is None or 
            current_second != self._current_second_stats['timestamp']):
            
            if self._current_second_stats['timestamp'] is not None:
                self._traffic_window.append({
                    'timestamp': self._current_second_stats['timestamp'],
                    'packet_count': self._current_second_stats['packet_count'],
                    'byte_count': self._current_second_stats['byte_count']
                })
            
            self._current_second_stats = {
                'timestamp': current_second,
                'packet_count': 0,
                'byte_count': 0
            }
        
        # 更新当前秒的统计
        self._current_second_stats['packet_count'] += 1
        self._current_second_stats['byte_count'] += length
    
    def _update_connection_tracking(self, packet_info: Dict[str, Any]) -> None:
        """更新连接跟踪信息"""
        src_ip = packet_info.get('src_ip')
        dst_ip = packet_info.get('dst_ip')
        src_port = packet_info.get('src_port')
        dst_port = packet_info.get('dst_port')
        protocol = packet_info.get('protocol')
        timestamp = packet_info.get('timestamp', datetime.now().timestamp())
        length = packet_info.get('length', 0)
        
        if not all([src_ip, dst_ip, protocol]):
            return
        
        # 创建连接键（双向）
        conn_key1 = (src_ip, dst_ip, src_port, dst_port, protocol)
        conn_key2 = (dst_ip, src_ip, dst_port, src_port, protocol)
        
        # 查找现有连接
        conn_key = None
        if conn_key1 in self._connections:
            conn_key = conn_key1
        elif conn_key2 in self._connections:
            conn_key = conn_key2
        else:
            conn_key = conn_key1
            self._connections[conn_key] = {
                'start_time': timestamp,
                'last_seen': timestamp,
                'packet_count': 0,
                'byte_count': 0,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': protocol
            }
        
        # 更新连接信息
        conn_info = self._connections[conn_key]
        conn_info['last_seen'] = timestamp
        conn_info['packet_count'] += 1
        conn_info['byte_count'] += length
    
    def _store_packet(self, packet_info: Dict[str, Any]) -> None:
        """存储数据包到数据库"""
        try:
            # 构造数据包数据
            packet_data = {
                'timestamp': packet_info.get('timestamp', datetime.now().timestamp()),
                'src_ip': packet_info.get('src_ip', ''),
                'dst_ip': packet_info.get('dst_ip', ''),
                'src_port': packet_info.get('src_port', 0),
                'dst_port': packet_info.get('dst_port', 0),
                'protocol': packet_info.get('protocol', 'Unknown'),
                'length': packet_info.get('length', 0),
                'summary': packet_info.get('summary', '')
            }
            
            # 保存到数据库
            self.data_manager.save_packet(packet_data)
            
        except Exception as e:
            self.logger.error(f"存储数据包失败: {e}")
    
    def _detect_anomalies(self, packet_info: Dict[str, Any]) -> None:
        """检测网络异常"""
        # 简单的异常检测逻辑
        # 可以根据需要扩展更复杂的检测算法
        
        try:
            # 检测异常大的数据包
            length = packet_info.get('length', 0)
            if length > 9000:  # 超过标准MTU
                self.logger.warning(f"检测到异常大的数据包: {length} 字节")
            
            # 检测异常端口
            src_port = packet_info.get('src_port')
            dst_port = packet_info.get('dst_port')
            
            suspicious_ports = [1234, 31337, 12345, 54321]  # 常见恶意软件端口
            if src_port in suspicious_ports or dst_port in suspicious_ports:
                self.logger.warning(f"检测到可疑端口活动: {src_port} -> {dst_port}")
                
        except Exception as e:
            self.logger.debug(f"异常检测失败: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        获取当前统计信息
        
        Returns:
            当前统计信息字典
        """
        with self._lock:
            stats = self._packet_stats.copy()
            
            # 计算速率
            if stats['start_time'] and stats['last_update']:
                # 使用datetime对象计算时间差
                duration = (stats['last_update'] - stats['start_time']).total_seconds()
                if duration > 0:
                    stats['packet_rate'] = stats['total_packets'] / duration
                    stats['byte_rate'] = stats['total_bytes'] / duration
                else:
                    stats['packet_rate'] = 0.0
                    stats['byte_rate'] = 0.0
            else:
                stats['packet_rate'] = 0.0
                stats['byte_rate'] = 0.0
            
            # 转换defaultdict为普通dict
            stats['protocol_counts'] = dict(stats['protocol_counts'])
            stats['protocol_bytes'] = dict(stats['protocol_bytes'])
            stats['ip_counts'] = dict(stats['ip_counts'])
            stats['port_counts'] = dict(stats['port_counts'])
            
            return stats
    
    def get_traffic_history(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """
        获取流量历史数据
        
        Args:
            minutes: 获取最近几分钟的数据
            
        Returns:
            流量历史数据列表
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            history = []
            for data_point in self._traffic_window:
                if data_point['timestamp'] >= cutoff_time:
                    history.append(data_point.copy())
            
            return history
    
    def get_top_talkers(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        获取流量最大的IP地址
        
        Args:
            limit: 返回的数量限制
            
        Returns:
            (IP地址, 数据包数量) 的列表，按数量降序排列
        """
        with self._lock:
            sorted_ips = sorted(
                self._packet_stats['ip_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_ips[:limit]
    
    def get_protocol_distribution(self) -> Dict[str, float]:
        """
        获取协议分布百分比
        
        Returns:
            协议分布字典，键为协议名，值为百分比
        """
        with self._lock:
            total_packets = self._packet_stats['total_packets']
            if total_packets == 0:
                return {}
            
            distribution = {}
            for protocol, count in self._packet_stats['protocol_counts'].items():
                distribution[protocol] = (count / total_packets) * 100
            
            return distribution
    
    def get_active_connections(self, timeout_minutes: int = 5) -> List[Dict[str, Any]]:
        """
        获取活跃连接列表
        
        Args:
            timeout_minutes: 连接超时时间（分钟）
            
        Returns:
            活跃连接列表
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
            
            active_connections = []
            for conn_key, conn_info in self._connections.items():
                if conn_info['last_seen'] >= cutoff_time:
                    active_connections.append(conn_info.copy())
            
            # 按字节数排序
            active_connections.sort(key=lambda x: x['byte_count'], reverse=True)
            
            return active_connections
    
    def reset_stats(self) -> None:
        """重置所有统计信息"""
        with self._lock:
            self._packet_stats = {
                'total_packets': 0,
                'total_bytes': 0,
                'protocol_counts': defaultdict(int),
                'protocol_bytes': defaultdict(int),
                'ip_counts': defaultdict(int),
                'port_counts': defaultdict(int),
                'start_time': None,
                'last_update': None
            }
            
            self._traffic_window.clear()
            self._current_second_stats = {
                'timestamp': None,
                'packet_count': 0,
                'byte_count': 0
            }
            
            self._connections.clear()
            
            self.logger.info("统计信息已重置")
    
    def calculate_baseline(self, hours: int = 1) -> Dict[str, Any]:
        """
        计算基线统计信息
        
        Args:
            hours: 计算基线的时间范围（小时）
            
        Returns:
            基线统计信息
        """
        try:
            # 从数据库获取历史数据
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            packets = self.data_manager.get_packets_by_time_range(start_time, end_time)
            
            if not packets:
                return {}
            
            # 计算基线指标
            total_packets = len(packets)
            total_bytes = sum(p.get('length', 0) for p in packets)
            duration_hours = hours
            
            baseline = {
                'avg_packet_rate': total_packets / (duration_hours * 3600),
                'avg_byte_rate': total_bytes / (duration_hours * 3600),
                'total_packets': total_packets,
                'total_bytes': total_bytes,
                'time_range': f"{start_time.isoformat()} - {end_time.isoformat()}"
            }
            
            # 计算协议分布
            protocol_counts = defaultdict(int)
            for packet in packets:
                protocol_counts[packet.get('protocol', 'Unknown')] += 1
            
            baseline['protocol_distribution'] = {
                protocol: (count / total_packets) * 100
                for protocol, count in protocol_counts.items()
            }
            
            self._baseline_stats = baseline
            return baseline
            
        except Exception as e:
            self.logger.error(f"计算基线统计失败: {e}")
            return {}
    
    # 兼容性方法 - 为了与GUI代码保持一致
    def get_statistics(self) -> Dict[str, Any]:
        """
        兼容性方法：获取统计信息
        
        这是为了与GUI代码中的方法调用保持一致而添加的兼容性方法。
        实际功能由 get_current_stats() 方法提供。
        
        Returns:
            当前统计信息字典
        """
        return self.get_current_stats()
    
    def reset_statistics(self) -> None:
        """
        兼容性方法：重置统计信息
        
        这是为了与GUI代码中的方法调用保持一致而添加的兼容性方法。
        实际功能由 reset_stats() 方法提供。
        """
        self.reset_stats()

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态信息"""
        return {
            'queue_size': self._db_queue.qsize(),
            'queue_maxsize': self._db_queue.maxsize,
            'thread_running': self._db_thread_running,
            'thread_alive': self._db_thread.is_alive() if self._db_thread else False
        }

    def shutdown(self) -> None:
        """关闭数据处理器，清理资源"""
        self.logger.info("正在关闭数据处理器...")
        self._stop_db_thread()
        self.logger.info("数据处理器已关闭")

    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.shutdown()
        except:
            pass