"""
数据管理模块

提供数据的存储、检索和管理功能。
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading


class DataManager:
    """数据管理类，负责数据的持久化存储"""
    
    def __init__(self, db_path: str):
        """
        初始化数据管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # 确保数据库目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建数据包表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    src_ip TEXT,
                    dst_ip TEXT,
                    src_port INTEGER,
                    dst_port INTEGER,
                    protocol TEXT NOT NULL,
                    length INTEGER NOT NULL,
                    raw_data BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建统计数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_type TEXT NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    packet_count INTEGER DEFAULT 0,
                    total_bytes INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_packets_timestamp ON packets(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_packets_protocol ON packets(protocol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_statistics_type ON statistics(stat_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_name ON sessions(session_name)")
            
            conn.commit()
            self.logger.info("数据库初始化完成")
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_packet(self, packet_data: Dict[str, Any]) -> int:
        """
        保存数据包信息
        
        Args:
            packet_data: 数据包信息字典
            
        Returns:
            插入的记录ID
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO packets (
                        timestamp, src_ip, dst_ip, src_port, dst_port,
                        protocol, length, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    packet_data.get('timestamp', datetime.now().timestamp()),
                    packet_data.get('src_ip'),
                    packet_data.get('dst_ip'),
                    packet_data.get('src_port'),
                    packet_data.get('dst_port'),
                    packet_data.get('protocol', 'Unknown'),
                    packet_data.get('length', 0),
                    packet_data.get('raw_data')
                ))
                conn.commit()
                return cursor.lastrowid
    
    def save_packets_batch(self, packets: List[Dict[str, Any]]) -> List[int]:
        """
        批量保存数据包
        
        Args:
            packets: 数据包列表
            
        Returns:
            插入的记录ID列表
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                packet_tuples = [
                    (
                        packet.get('timestamp', datetime.now().timestamp()),
                        packet.get('src_ip'),
                        packet.get('dst_ip'),
                        packet.get('src_port'),
                        packet.get('dst_port'),
                        packet.get('protocol', 'Unknown'),
                        packet.get('length', 0),
                        packet.get('raw_data')
                    )
                    for packet in packets
                ]
                
                cursor.executemany("""
                    INSERT INTO packets (
                        timestamp, src_ip, dst_ip, src_port, dst_port,
                        protocol, length, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, packet_tuples)
                
                conn.commit()
                
                # 获取插入的ID范围
                last_id = cursor.lastrowid
                first_id = last_id - len(packets) + 1
                return list(range(first_id, last_id + 1))
    
    def get_packets(self, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   protocol: Optional[str] = None,
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """
        获取数据包列表
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            protocol: 协议过滤
            limit: 返回记录数限制
            
        Returns:
            数据包列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM packets WHERE 1=1"
            params = []
            
            if start_time is not None:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            if protocol:
                query += " AND protocol = ?"
                params.append(protocol)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def save_statistics(self, stat_type: str, stats: Dict[str, float], timestamp: Optional[float] = None) -> None:
        """
        保存统计数据
        
        Args:
            stat_type: 统计类型
            stats: 统计数据字典
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stat_tuples = [
                    (stat_type, key, value, timestamp)
                    for key, value in stats.items()
                ]
                
                cursor.executemany("""
                    INSERT INTO statistics (stat_type, stat_key, stat_value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, stat_tuples)
                
                conn.commit()
    
    def get_statistics(self, 
                      stat_type: str,
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        获取统计数据
        
        Args:
            stat_type: 统计类型
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            统计数据列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM statistics WHERE stat_type = ?"
            params = [stat_type]
            
            if start_time is not None:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def create_session(self, session_name: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        创建新的捕获会话
        
        Args:
            session_name: 会话名称
            metadata: 会话元数据
            
        Returns:
            会话ID
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_name, start_time, metadata)
                    VALUES (?, ?, ?)
                """, (
                    session_name,
                    datetime.now().timestamp(),
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                return cursor.lastrowid
    
    def update_session(self, session_id: int, packet_count: int, total_bytes: int) -> None:
        """
        更新会话统计信息
        
        Args:
            session_id: 会话ID
            packet_count: 数据包数量
            total_bytes: 总字节数
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET packet_count = ?, total_bytes = ?, end_time = ?
                    WHERE id = ?
                """, (packet_count, total_bytes, datetime.now().timestamp(), session_id))
                conn.commit()
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                session = dict(row)
                if session['metadata']:
                    session['metadata'] = json.loads(session['metadata'])
                sessions.append(session)
            
            return sessions
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        清理旧数据
        
        Args:
            days: 保留天数
            
        Returns:
            删除的记录数
        """
        cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
        
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 删除旧的数据包记录
                cursor.execute("DELETE FROM packets WHERE timestamp < ?", (cutoff_time,))
                packet_count = cursor.rowcount
                
                # 删除旧的统计记录
                cursor.execute("DELETE FROM statistics WHERE timestamp < ?", (cutoff_time,))
                stat_count = cursor.rowcount
                
                conn.commit()
                
                total_deleted = packet_count + stat_count
                self.logger.info(f"清理了 {total_deleted} 条旧记录")
                
                return total_deleted
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取表的记录数
            cursor.execute("SELECT COUNT(*) FROM packets")
            packet_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM statistics")
            stat_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]
            
            # 获取数据库文件大小
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                'database_path': str(self.db_path),
                'database_size': db_size,
                'packet_count': packet_count,
                'statistics_count': stat_count,
                'session_count': session_count
            }