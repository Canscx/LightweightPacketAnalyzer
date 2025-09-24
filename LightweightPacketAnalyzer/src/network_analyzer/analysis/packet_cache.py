"""
数据包缓存模块
实现LRU缓存机制，优化数据包解析性能
"""

import hashlib
import time
from collections import OrderedDict
from typing import Optional, Dict, Any, Tuple
from threading import RLock

from .base_parser import ParsedPacket


class PacketCacheEntry:
    """缓存条目类"""
    
    def __init__(self, parsed_packet: ParsedPacket, timestamp: float):
        self.parsed_packet = parsed_packet
        self.timestamp = timestamp
        self.access_count = 1
        self.last_access = timestamp
    
    def update_access(self):
        """更新访问信息"""
        self.access_count += 1
        self.last_access = time.time()


class PacketCache:
    """
    数据包缓存类
    使用LRU算法管理缓存，提高重复数据包解析性能
    """
    
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, PacketCacheEntry] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _generate_key(self, raw_data: bytes) -> str:
        """
        生成数据包的缓存键
        
        Args:
            raw_data: 原始数据包数据
            
        Returns:
            缓存键字符串
        """
        # 使用SHA256哈希生成唯一键
        return hashlib.sha256(raw_data).hexdigest()
    
    def _is_expired(self, entry: PacketCacheEntry) -> bool:
        """
        检查缓存条目是否过期
        
        Args:
            entry: 缓存条目
            
        Returns:
            是否过期
        """
        return time.time() - entry.timestamp > self.ttl
    
    def _cleanup_expired(self):
        """清理过期的缓存条目"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time - entry.timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    def _evict_lru(self):
        """驱逐最近最少使用的缓存条目"""
        if self._cache:
            self._cache.popitem(last=False)  # 移除最旧的条目
            self._evictions += 1
    
    def get(self, raw_data: bytes) -> Optional[ParsedPacket]:
        """
        从缓存获取解析结果
        
        Args:
            raw_data: 原始数据包数据
            
        Returns:
            解析结果，如果不存在则返回None
        """
        with self._lock:
            key = self._generate_key(raw_data)
            
            if key in self._cache:
                entry = self._cache[key]
                
                # 检查是否过期
                if self._is_expired(entry):
                    del self._cache[key]
                    self._misses += 1
                    return None
                
                # 更新访问信息并移到末尾（最近使用）
                entry.update_access()
                self._cache.move_to_end(key)
                self._hits += 1
                return entry.parsed_packet
            
            self._misses += 1
            return None
    
    def put(self, raw_data: bytes, parsed_packet: ParsedPacket):
        """
        将解析结果放入缓存
        
        Args:
            raw_data: 原始数据包数据
            parsed_packet: 解析结果
        """
        with self._lock:
            key = self._generate_key(raw_data)
            current_time = time.time()
            
            # 如果已存在，更新条目
            if key in self._cache:
                entry = self._cache[key]
                entry.parsed_packet = parsed_packet
                entry.timestamp = current_time
                entry.update_access()
                self._cache.move_to_end(key)
                return
            
            # 清理过期条目
            self._cleanup_expired()
            
            # 如果缓存已满，驱逐最旧的条目
            while len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # 添加新条目
            entry = PacketCacheEntry(parsed_packet, current_time)
            self._cache[key] = entry
    
    def invalidate(self, raw_data: bytes) -> bool:
        """
        使特定数据包的缓存失效
        
        Args:
            raw_data: 原始数据包数据
            
        Returns:
            是否成功移除
        """
        with self._lock:
            key = self._generate_key(raw_data)
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate,
                'ttl': self.ttl
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取详细的缓存信息
        
        Returns:
            缓存详细信息
        """
        with self._lock:
            entries_info = []
            current_time = time.time()
            
            for key, entry in self._cache.items():
                age = current_time - entry.timestamp
                entries_info.append({
                    'key': key[:16] + '...',  # 只显示前16个字符
                    'age': age,
                    'access_count': entry.access_count,
                    'last_access': entry.last_access,
                    'expired': self._is_expired(entry)
                })
            
            return {
                'entries': entries_info,
                'stats': self.get_stats()
            }
    
    def resize(self, new_max_size: int):
        """
        调整缓存大小
        
        Args:
            new_max_size: 新的最大缓存大小
        """
        with self._lock:
            self.max_size = new_max_size
            
            # 如果新大小小于当前缓存大小，驱逐多余条目
            while len(self._cache) > self.max_size:
                self._evict_lru()
    
    def set_ttl(self, new_ttl: float):
        """
        设置新的TTL值
        
        Args:
            new_ttl: 新的生存时间（秒）
        """
        with self._lock:
            self.ttl = new_ttl
            # 立即清理现在过期的条目
            self._cleanup_expired()


# 全局缓存实例
packet_cache = PacketCache()