#!/usr/bin/env python3
"""
简化的MainWindow测试脚本
"""

import sys
import traceback
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, 'src')

def main():
    """主测试函数"""
    print("开始测试MainWindow...")
    
    try:
        # 导入必要模块
        from network_analyzer.config.settings import Settings
        from network_analyzer.gui.main_window import MainWindow
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        
        # 加载配置
        settings = Settings()
        print(f"配置加载成功: {settings.APP_NAME}")
        
        # 创建MainWindow
        print("创建MainWindow实例...")
        app = MainWindow(settings)
        print("✓ MainWindow创建成功")
        
        # 显示窗口5秒后自动关闭
        print("显示窗口5秒...")
        app.root.after(5000, app.root.quit)
        
        # 运行主循环
        app.run()
        print("✓ 窗口显示完成")
        
        return 0
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())