"""
网络流量统计系统主程序入口

提供应用程序的启动和初始化逻辑。
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from network_analyzer.config.settings import Settings
from network_analyzer.gui.main_window import MainWindow


def setup_logging(settings: Settings) -> None:
    """设置日志配置"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建日志目录
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_permissions() -> bool:
    """检查是否有足够的权限进行数据包捕获"""
    try:
        # 在Windows上检查是否以管理员身份运行
        if sys.platform == "win32":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # 在Unix系统上检查是否为root用户
            return os.geteuid() == 0
    except Exception as e:
        logging.warning(f"权限检查失败: {e}")
        return False


def main(config_file: Optional[str] = None) -> int:
    """
    主程序入口点
    
    Args:
        config_file: 可选的配置文件路径
        
    Returns:
        程序退出码
    """
    try:
        # 加载配置
        settings = Settings(config_file)
        
        # 设置日志
        setup_logging(settings)
        logger = logging.getLogger(__name__)
        
        logger.info("启动网络流量统计系统...")
        logger.info(f"版本: {settings.VERSION}")
        
        # 检查权限
        if settings.REQUIRE_ADMIN and not check_permissions():
            logger.error("需要管理员权限才能捕获网络数据包")
            if sys.platform == "win32":
                print("请以管理员身份运行此程序")
            else:
                print("请使用sudo运行此程序")
            return 1
        
        # 创建必要的目录
        data_dir = Path(settings.DATA_DIRECTORY)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 启动GUI应用程序
        logger.info("启动图形界面...")
        app = MainWindow(settings)
        return app.run()
        
    except KeyboardInterrupt:
        logging.info("用户中断程序")
        return 0
    except Exception as e:
        logging.error(f"程序运行出错: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="网络流量统计系统")
    parser.add_argument(
        "--config", 
        type=str, 
        help="配置文件路径"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 2.0"
    )
    
    args = parser.parse_args()
    sys.exit(main(args.config))