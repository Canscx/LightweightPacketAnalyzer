"""
配置管理模块

处理应用程序的配置加载和管理。
"""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional, Any, Dict, Tuple, List
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
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        保存配置到.env文件
        
        Args:
            file_path: 可选的文件路径，默认使用self.env_file
            
        Returns:
            bool: 保存是否成功
            
        Raises:
            OSError: 文件操作失败
            ValueError: 配置验证失败
        """
        target_file = file_path or self.env_file
        logger = logging.getLogger(__name__)
        
        try:
            # 验证配置
            if not self.validate_settings():
                raise ValueError("配置验证失败，无法保存")
            
            # 创建备份
            backup_file = f"{target_file}.backup"
            if Path(target_file).exists():
                shutil.copy2(target_file, backup_file)
                logger.info(f"已创建配置备份: {backup_file}")
            
            # 生成配置内容
            config_content = self._generate_env_content()
            
            # 原子写入：先写入临时文件，再重命名
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                           suffix='.env', delete=False) as temp_file:
                temp_file.write(config_content)
                temp_file_path = temp_file.name
            
            # 重命名为目标文件
            shutil.move(temp_file_path, target_file)
            logger.info(f"配置已保存到: {target_file}")
            
            return True
            
        except Exception as error:
            logger.error(f"保存配置失败: {error}")
            # 尝试恢复备份
            if Path(backup_file).exists():
                try:
                    shutil.copy2(backup_file, target_file)
                    logger.info("已从备份恢复配置文件")
                except Exception as restore_error:
                    logger.error(f"恢复备份失败: {restore_error}")
            raise
    
    def _generate_env_content(self) -> str:
        """
        生成.env文件内容
        
        Returns:
            str: 格式化的配置文件内容
        """
        content_lines = [
            "# 网络流量统计分析工具配置文件",
            "# 此文件由设置功能自动生成",
            "",
            "# 应用程序基本信息",
            f"APP_NAME={self.APP_NAME}",
            f"VERSION={self.VERSION}",
            f"DESCRIPTION={self.DESCRIPTION}",
            "",
            "# GUI配置",
            f"WINDOW_WIDTH={self.WINDOW_WIDTH}",
            f"WINDOW_HEIGHT={self.WINDOW_HEIGHT}",
            f"THEME={self.THEME}",
            "",
            "# 数据包捕获配置",
            f"CAPTURE_INTERFACE={self.CAPTURE_INTERFACE}",
            f"CAPTURE_FILTER={self.CAPTURE_FILTER}",
            f"CAPTURE_TIMEOUT={self.CAPTURE_TIMEOUT}",
            f"MAX_PACKET_COUNT={self.MAX_PACKET_COUNT}",
            "",
            "# 数据存储配置",
            f"DATA_DIRECTORY={self.DATA_DIRECTORY}",
            f"DATABASE_PATH={self.DATABASE_PATH}",
            f"DATA_RETENTION_DAYS={self.DATA_RETENTION_DAYS}",
            f"AUTO_CLEANUP={'true' if self.AUTO_CLEANUP else 'false'}",
            "",
            "# 日志配置",
            f"LOG_LEVEL={self.LOG_LEVEL}",
            f"LOG_FILE={self.LOG_FILE}",
            f"LOG_MAX_SIZE={self.LOG_MAX_SIZE}",
            f"LOG_BACKUP_COUNT={self.LOG_BACKUP_COUNT}",
            "",
            "# 性能配置",
            f"BUFFER_SIZE={self.BUFFER_SIZE}",
            f"WORKER_THREADS={self.WORKER_THREADS}",
            "",
            "# 安全配置",
            f"ENABLE_PROMISCUOUS_MODE={'true' if self.ENABLE_PROMISCUOUS_MODE else 'false'}",
            f"REQUIRE_ADMIN={'true' if self.REQUIRE_ADMIN else 'false'}",
            "",
            "# 开发配置",
            f"DEBUG={'true' if self.DEBUG else 'false'}",
            f"TESTING={'true' if self.TESTING else 'false'}",
            f"ENABLE_PROFILING={'true' if self.ENABLE_PROFILING else 'false'}",
            "",
            "# 捕获选项设置",
            f"DEFAULT_CAPTURE_INTERFACE={self.CAPTURE_OPTIONS.get('default_interface', '')}",
            f"DEFAULT_BPF_FILTER={self.CAPTURE_OPTIONS.get('default_filter', '')}",
            f"DEFAULT_PACKET_COUNT={self.CAPTURE_OPTIONS.get('default_packet_count', 1000)}",
            f"DEFAULT_CAPTURE_TIMEOUT={self.CAPTURE_OPTIONS.get('default_timeout', 60)}",
            f"PROMISCUOUS_MODE={'true' if self.CAPTURE_OPTIONS.get('promiscuous_mode', True) else 'false'}",
            f"CAPTURE_BUFFER_SIZE={self.CAPTURE_OPTIONS.get('buffer_size', 1048576)}",
            f"FILTER_TEMPLATES_FILE={self.CAPTURE_OPTIONS.get('filter_templates_file', 'filter_templates.json')}",
            f"SAVE_CAPTURE_HISTORY={'true' if self.CAPTURE_OPTIONS.get('save_capture_history', True) else 'false'}",
            f"MAX_HISTORY_ENTRIES={self.CAPTURE_OPTIONS.get('max_history_entries', 50)}",
            f"VALIDATE_BPF_FILTERS={'true' if self.CAPTURE_OPTIONS.get('validate_filters', True) else 'false'}",
            f"SHOW_INTERFACE_DETAILS={'true' if self.CAPTURE_OPTIONS.get('show_interface_details', True) else 'false'}",
            f"AUTO_DETECT_INTERFACES={'true' if self.CAPTURE_OPTIONS.get('auto_detect_interfaces', True) else 'false'}",
            f"INTERFACE_REFRESH_INTERVAL={self.CAPTURE_OPTIONS.get('interface_refresh_interval', 30)}",
            ""
        ]
        
        return "\n".join(content_lines)
    
    def get_immediate_settings(self) -> Dict[str, Any]:
        """
        获取需要立即生效的配置项
        
        Returns:
            Dict: 立即生效的配置字典
        """
        return {
            'WINDOW_WIDTH': self.WINDOW_WIDTH,
            'WINDOW_HEIGHT': self.WINDOW_HEIGHT,
            'THEME': self.THEME,
        }
    
    def get_restart_required_settings(self) -> Dict[str, Any]:
        """
        获取需要重启才能生效的配置项
        
        Returns:
            Dict: 需要重启的配置字典
        """
        return {
            'DATABASE_PATH': self.DATABASE_PATH,
            'LOG_FILE': self.LOG_FILE,
            'LOG_LEVEL': self.LOG_LEVEL,
            'LOG_MAX_SIZE': self.LOG_MAX_SIZE,
            'LOG_BACKUP_COUNT': self.LOG_BACKUP_COUNT,
            'BUFFER_SIZE': self.BUFFER_SIZE,
            'WORKER_THREADS': self.WORKER_THREADS,
            'DATA_DIRECTORY': self.DATA_DIRECTORY,
            'DATA_RETENTION_DAYS': self.DATA_RETENTION_DAYS,
        }
    
    def create_backup(self) -> str:
        """
        创建配置备份
        
        Returns:
            str: 备份文件路径
            
        Raises:
            OSError: 备份创建失败
        """
        if not Path(self.env_file).exists():
            raise OSError(f"配置文件不存在: {self.env_file}")
        
        backup_path = f"{self.env_file}.backup.{int(os.path.getmtime(self.env_file))}"
        shutil.copy2(self.env_file, backup_path)
        
        logger = logging.getLogger(__name__)
        logger.info(f"已创建配置备份: {backup_path}")
        
        return backup_path
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从备份恢复配置
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 恢复是否成功
            
        Raises:
            OSError: 备份文件不存在或恢复失败
        """
        if not Path(backup_path).exists():
            raise OSError(f"备份文件不存在: {backup_path}")
        
        try:
            shutil.copy2(backup_path, self.env_file)
            # 重新加载配置
            self._load_env_file()
            self._init_default_settings()
            
            logger = logging.getLogger(__name__)
            logger.info(f"已从备份恢复配置: {backup_path}")
            
            return True
            
        except Exception as error:
            logger = logging.getLogger(__name__)
            logger.error(f"从备份恢复配置失败: {error}")
            raise
    
    def validate_setting_value(self, key: str, value: Any) -> Tuple[bool, str]:
        """
        验证单个配置项的值
        
        Args:
            key: 配置项名称
            value: 配置项值
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            if key == 'WINDOW_WIDTH':
                if not isinstance(value, int) or not (800 <= value <= 1920):
                    return False, "窗口宽度必须在800-1920之间"
            elif key == 'WINDOW_HEIGHT':
                if not isinstance(value, int) or not (600 <= value <= 1080):
                    return False, "窗口高度必须在600-1080之间"
            elif key == 'DATA_RETENTION_DAYS':
                if not isinstance(value, int) or not (1 <= value <= 365):
                    return False, "数据保留天数必须在1-365之间"
            elif key == 'LOG_LEVEL':
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if value not in valid_levels:
                    return False, f"日志级别必须是{', '.join(valid_levels)}之一"
            elif key == 'LOG_MAX_SIZE':
                if not isinstance(value, int) or value <= 0:
                    return False, "日志文件最大大小必须大于0"
            elif key == 'LOG_BACKUP_COUNT':
                if not isinstance(value, int) or value < 0:
                    return False, "日志备份文件数量不能为负数"
            elif key == 'BUFFER_SIZE':
                if not isinstance(value, int) or not (1024 <= value <= 1048576):
                    return False, "缓冲区大小必须在1KB-1MB之间"
            elif key == 'WORKER_THREADS':
                if not isinstance(value, int) or not (1 <= value <= 16):
                    return False, "工作线程数必须在1-16之间"
            elif key == 'MAX_PACKET_COUNT':
                if not isinstance(value, int) or not (100 <= value <= 100000):
                    return False, "最大数据包数量必须在100-100000之间"
            elif key == 'CAPTURE_TIMEOUT':
                if not isinstance(value, int) or not (1 <= value <= 300):
                    return False, "捕获超时时间必须在1-300秒之间"
            elif key == 'THEME':
                valid_themes = ['default', 'clam', 'alt', 'classic']
                if value not in valid_themes:
                    return False, f"主题必须是{', '.join(valid_themes)}之一"
            
            return True, ""
            
        except Exception as error:
            return False, f"验证配置项时发生错误: {error}"
    
    def validate_all_settings(self, settings_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证所有配置项
        
        Args:
            settings_dict: 配置字典
            
        Returns:
            Tuple[bool, List[str]]: (是否全部有效, 错误信息列表)
        """
        errors = []
        
        for key, value in settings_dict.items():
            is_valid, error_msg = self.validate_setting_value(key, value)
            if not is_valid:
                errors.append(f"{key}: {error_msg}")
        
        return len(errors) == 0, errors
    
    def update_from_dict(self, settings_dict: Dict[str, Any]) -> None:
        """
        从字典更新配置
        
        Args:
            settings_dict: 配置字典
            
        Raises:
            ValueError: 配置验证失败
        """
        # 验证所有配置
        is_valid, errors = self.validate_all_settings(settings_dict)
        if not is_valid:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
        
        # 更新配置
        for key, value in settings_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 更新CAPTURE_OPTIONS字典中的配置
        capture_option_mappings = {
            'DEFAULT_CAPTURE_INTERFACE': 'default_interface',
            'DEFAULT_BPF_FILTER': 'default_filter',
            'DEFAULT_PACKET_COUNT': 'default_packet_count',
            'DEFAULT_CAPTURE_TIMEOUT': 'default_timeout',
            'PROMISCUOUS_MODE': 'promiscuous_mode',
            'CAPTURE_BUFFER_SIZE': 'buffer_size',
            'FILTER_TEMPLATES_FILE': 'filter_templates_file',
            'SAVE_CAPTURE_HISTORY': 'save_capture_history',
            'MAX_HISTORY_ENTRIES': 'max_history_entries',
            'VALIDATE_BPF_FILTERS': 'validate_filters',
            'SHOW_INTERFACE_DETAILS': 'show_interface_details',
            'AUTO_DETECT_INTERFACES': 'auto_detect_interfaces',
            'INTERFACE_REFRESH_INTERVAL': 'interface_refresh_interval',
        }
        
        for env_key, option_key in capture_option_mappings.items():
            if env_key in settings_dict:
                self.CAPTURE_OPTIONS[option_key] = settings_dict[env_key]

    def __repr__(self) -> str:
        """配置的字符串表示"""
        return f"Settings(version={self.VERSION}, debug={self.DEBUG})"