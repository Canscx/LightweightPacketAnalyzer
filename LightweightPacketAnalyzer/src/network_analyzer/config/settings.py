"""
配置管理模块

处理应用程序的配置加载和管理。
"""

import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv


class Settings:
    """应用程序配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 可选的配置文件路径，默认使用.env
        """
        self.env_file = config_file or ".env"
        self._load_env_file()
        self._init_default_settings()
    
    def _load_env_file(self):
        """加载环境变量文件"""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
    
    def _init_default_settings(self):
        """初始化默认配置"""
        # 应用程序基本信息
        self.VERSION = os.getenv("VERSION", "0.1.0")
        self.APP_NAME = os.getenv("APP_NAME", "网络流量统计")
        self.DESCRIPTION = os.getenv("DESCRIPTION", "轻量级网络数据包分析工具")
        
        # 数据包捕获配置
        self.CAPTURE_INTERFACE = os.getenv("CAPTURE_INTERFACE", "auto")
        self.CAPTURE_FILTER = os.getenv("CAPTURE_FILTER", "")
        self.CAPTURE_TIMEOUT = int(os.getenv("CAPTURE_TIMEOUT", "1"))
        self.MAX_PACKET_COUNT = int(os.getenv("MAX_PACKET_COUNT", "10000"))
        
        # 数据存储配置
        self.DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", "data")
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "data/network_analyzer.db")
        self.DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))
        self.AUTO_CLEANUP = os.getenv("AUTO_CLEANUP", "true").lower() == "true"
        
        # GUI配置
        self.WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1200"))
        self.WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "800"))
        self.THEME = os.getenv("THEME", "default")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/network_analyzer.log")
        self.LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # 性能配置
        self.BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "65536"))
        self.WORKER_THREADS = int(os.getenv("WORKER_THREADS", "4"))
        
        # 安全配置
        self.ENABLE_PROMISCUOUS_MODE = os.getenv("ENABLE_PROMISCUOUS_MODE", "false").lower() == "true"
        self.REQUIRE_ADMIN = os.getenv("REQUIRE_ADMIN", "true").lower() == "true"
        
        # 开发配置
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.TESTING = os.getenv("TESTING", "false").lower() == "true"
        self.ENABLE_PROFILING = os.getenv('ENABLE_PROFILING', 'False').lower() == 'true'
        
        # 捕获选项设置
        self.CAPTURE_OPTIONS = {
            'default_interface': os.getenv('DEFAULT_CAPTURE_INTERFACE', ''),
            'default_filter': os.getenv('DEFAULT_BPF_FILTER', ''),
            'default_packet_count': int(os.getenv('DEFAULT_PACKET_COUNT', '1000')),
            'default_timeout': int(os.getenv('DEFAULT_CAPTURE_TIMEOUT', '60')),
            'promiscuous_mode': os.getenv('PROMISCUOUS_MODE', 'True').lower() == 'true',
            'buffer_size': int(os.getenv('CAPTURE_BUFFER_SIZE', '1048576')),  # 1MB
            'filter_templates_file': os.getenv('FILTER_TEMPLATES_FILE', 'filter_templates.json'),
            'save_capture_history': os.getenv('SAVE_CAPTURE_HISTORY', 'True').lower() == 'true',
            'max_history_entries': int(os.getenv('MAX_HISTORY_ENTRIES', '50')),
            'validate_filters': os.getenv('VALIDATE_BPF_FILTERS', 'True').lower() == 'true',
            'show_interface_details': os.getenv('SHOW_INTERFACE_DETAILS', 'True').lower() == 'true',
            'auto_detect_interfaces': os.getenv('AUTO_DETECT_INTERFACES', 'True').lower() == 'true',
            'interface_refresh_interval': int(os.getenv('INTERFACE_REFRESH_INTERVAL', '30')),  # 秒
        }
    
    def _get_env(self, key: str, default: str) -> str:
        """获取环境变量字符串值"""
        return os.getenv(key, default)
    
    def _get_env_int(self, key: str, default: int) -> int:
        """获取环境变量整数值"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """获取环境变量布尔值"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def get_database_path(self) -> Path:
        """
        获取数据库文件的绝对路径
        
        Returns:
            Path: 数据库文件的绝对路径
        """
        db_path = Path(self.DATABASE_PATH)
        if not db_path.is_absolute():
            # 相对于项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / db_path
        
        # 确保目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path.resolve()
    
    def get_log_path(self) -> Path:
        """
        获取日志文件的绝对路径
        
        Returns:
            Path: 日志文件的绝对路径
        """
        log_path = Path(self.LOG_FILE)
        if not log_path.is_absolute():
            # 相对于项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            log_path = project_root / log_path
        
        # 确保目录存在
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path.resolve()
    
    def get_data_dir(self) -> Path:
        """
        获取数据目录的绝对路径
        
        Returns:
            Path: 数据目录的绝对路径
        """
        data_path = Path(self.DATA_DIRECTORY)
        if not data_path.is_absolute():
            # 相对于项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            data_path = project_root / data_path
        
        # 确保目录存在
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path.resolve()
    
    def validate_settings(self) -> bool:
        """
        验证配置设置的有效性
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证数值配置
            if self.CAPTURE_TIMEOUT <= 0:
                return False
            if self.MAX_PACKET_COUNT <= 0:
                return False
            if self.WINDOW_WIDTH <= 0 or self.WINDOW_HEIGHT <= 0:
                return False
            if self.LOG_MAX_SIZE <= 0:
                return False
            if self.LOG_BACKUP_COUNT < 0:
                return False
            if self.BUFFER_SIZE <= 0:
                return False
            if self.WORKER_THREADS <= 0:
                return False
            if self.DATA_RETENTION_DAYS < 0:
                return False
            
            # 验证日志级别
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if self.LOG_LEVEL not in valid_log_levels:
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> dict:
        """
        将配置转换为字典格式
        
        Returns:
            dict: 配置字典
        """
        return {
            # 应用程序基本信息
            "VERSION": self.VERSION,
            "APP_NAME": self.APP_NAME,
            "DESCRIPTION": self.DESCRIPTION,
            
            # 数据包捕获配置
            "CAPTURE_INTERFACE": self.CAPTURE_INTERFACE,
            "CAPTURE_FILTER": self.CAPTURE_FILTER,
            "CAPTURE_TIMEOUT": self.CAPTURE_TIMEOUT,
            "MAX_PACKET_COUNT": self.MAX_PACKET_COUNT,
            
            # 数据存储配置
            "DATABASE_PATH": self.DATABASE_PATH,
            "DATA_RETENTION_DAYS": self.DATA_RETENTION_DAYS,
            "AUTO_CLEANUP": self.AUTO_CLEANUP,
            
            # GUI配置
            "WINDOW_WIDTH": self.WINDOW_WIDTH,
            "WINDOW_HEIGHT": self.WINDOW_HEIGHT,
            "THEME": self.THEME,
            
            # 日志配置
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FILE": self.LOG_FILE,
            "LOG_MAX_SIZE": self.LOG_MAX_SIZE,
            "LOG_BACKUP_COUNT": self.LOG_BACKUP_COUNT,
            
            # 性能配置
            "BUFFER_SIZE": self.BUFFER_SIZE,
            "WORKER_THREADS": self.WORKER_THREADS,
            
            # 安全配置
            "ENABLE_PROMISCUOUS_MODE": self.ENABLE_PROMISCUOUS_MODE,
            "REQUIRE_ADMIN": self.REQUIRE_ADMIN,
            
            # 开发配置
            "DEBUG": self.DEBUG,
            "TESTING": self.TESTING,
        }
    
    def __repr__(self) -> str:
        """配置的字符串表示"""
        return f"Settings(version={self.VERSION}, debug={self.DEBUG})"