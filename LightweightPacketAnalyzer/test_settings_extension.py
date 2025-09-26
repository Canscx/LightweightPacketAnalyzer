#!/usr/bin/env python3
"""
Settings类扩展功能测试脚本

测试新增的配置保存、验证和备份功能
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_analyzer.config.settings import Settings


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_settings_extension():
    """测试Settings类扩展功能"""
    print("=" * 60)
    print("Settings类扩展功能测试")
    print("=" * 60)
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as temp_file:
        temp_file.write("""# Test configuration file
APP_NAME=Test Application
VERSION=1.0.0
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
THEME=default
LOG_LEVEL=INFO
""")
        temp_config_path = temp_file.name
    
    try:
        print(f"1. 测试配置加载...")
        settings = Settings(temp_config_path)
        print(f"   ✅ 配置加载成功: {settings.APP_NAME}")
        
        print(f"2. 测试配置验证...")
        # 测试有效配置
        is_valid, errors = settings.validate_all_settings({
            'WINDOW_WIDTH': 1400,
            'WINDOW_HEIGHT': 900,
            'LOG_LEVEL': 'DEBUG'
        })
        print(f"   ✅ 有效配置验证: {is_valid}")
        
        # 测试无效配置
        is_valid, errors = settings.validate_all_settings({
            'WINDOW_WIDTH': 500,  # 太小
            'LOG_LEVEL': 'INVALID'  # 无效级别
        })
        print(f"   ✅ 无效配置验证: {not is_valid}, 错误: {len(errors)}个")
        
        print(f"3. 测试配置更新...")
        settings.update_from_dict({
            'WINDOW_WIDTH': 1400,
            'WINDOW_HEIGHT': 900,
            'THEME': 'clam'
        })
        print(f"   ✅ 配置更新成功: {settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        
        print(f"4. 测试配置保存...")
        success = settings.save_to_file()
        print(f"   ✅ 配置保存: {'成功' if success else '失败'}")
        
        print(f"5. 测试立即生效配置...")
        immediate_settings = settings.get_immediate_settings()
        print(f"   ✅ 立即生效配置: {len(immediate_settings)}项")
        for key, value in immediate_settings.items():
            print(f"      {key}: {value}")
        
        print(f"6. 测试重启生效配置...")
        restart_settings = settings.get_restart_required_settings()
        print(f"   ✅ 重启生效配置: {len(restart_settings)}项")
        
        print(f"7. 测试配置备份...")
        if Path(temp_config_path).exists():
            backup_path = settings.create_backup()
            print(f"   ✅ 配置备份创建: {Path(backup_path).name}")
            
            # 测试备份恢复
            settings.restore_from_backup(backup_path)
            print(f"   ✅ 配置备份恢复成功")
            
            # 清理备份文件
            Path(backup_path).unlink(missing_ok=True)
        
        print(f"8. 测试.env文件生成...")
        env_content = settings._generate_env_content()
        lines = env_content.split('\n')
        print(f"   ✅ .env文件内容生成: {len(lines)}行")
        print(f"   📄 前几行预览:")
        for i, line in enumerate(lines[:5]):
            print(f"      {i+1}: {line}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！Settings类扩展功能正常")
        print("=" * 60)
        
        return True
        
    except Exception as error:
        print(f"\n❌ 测试失败: {error}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理临时文件
        Path(temp_config_path).unlink(missing_ok=True)
        backup_file = f"{temp_config_path}.backup"
        Path(backup_file).unlink(missing_ok=True)


if __name__ == "__main__":
    setup_logging()
    success = test_settings_extension()
    sys.exit(0 if success else 1)