#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_analyzer.storage.data_manager import DataManager

def main():
    # 检查多个数据库
    db_files = ['network_analyzer.db', 'test_traffic_trends.db', 'test.db']
    
    for db_file in db_files:
        print(f'\n=== 检查 {db_file} ===')
        try:
            dm = DataManager(db_file)
            sessions = dm.get_sessions()
            print(f'找到 {len(sessions)} 个会话:')
            
            for s in sessions:
                session_id = s['id']
                packets = dm.get_packets_by_session(session_id)
                print(f'会话 {session_id}: {s.get("name", "N/A")} - {len(packets)} 个数据包')
        except Exception as e:
            print(f'检查 {db_file} 失败: {e}')

if __name__ == "__main__":
    main()