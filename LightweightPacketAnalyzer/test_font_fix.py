"""
字体测试脚本 - 诊断matplotlib中文字体问题
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

def test_system_fonts():
    """测试系统可用字体"""
    print("=== 系统字体检测 ===")
    
    # 获取所有可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 查找中文字体
    chinese_fonts = [
        'Microsoft YaHei',
        'SimHei', 
        'SimSun',
        'Microsoft YaHei UI',
        'PingFang SC',
        'Hiragino Sans GB',
        'Source Han Sans CN',
        'Noto Sans CJK SC',
        'WenQuanYi Micro Hei'
    ]
    
    print("可用的中文字体:")
    found_fonts = []
    for font in chinese_fonts:
        if font in available_fonts:
            print(f"  ✓ {font}")
            found_fonts.append(font)
        else:
            print(f"  ✗ {font}")
    
    return found_fonts

def test_font_rendering():
    """测试字体渲染效果"""
    print("\n=== 字体渲染测试 ===")
    
    # 清除matplotlib缓存
    plt.rcdefaults()
    
    # 测试不同的字体设置方法
    test_methods = [
        {
            'name': '方法1: 直接设置font.sans-serif',
            'setup': lambda: plt.rcParams.update({
                'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
                'axes.unicode_minus': False
            })
        },
        {
            'name': '方法2: 设置font.family',
            'setup': lambda: plt.rcParams.update({
                'font.family': 'sans-serif',
                'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
                'axes.unicode_minus': False
            })
        },
        {
            'name': '方法3: 强制刷新字体缓存',
            'setup': lambda: setup_font_with_cache_refresh()
        }
    ]
    
    for i, method in enumerate(test_methods):
        try:
            print(f"\n测试 {method['name']}:")
            
            # 重置matplotlib
            plt.rcdefaults()
            
            # 应用字体设置
            method['setup']()
            
            # 创建测试图表
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 测试数据
            protocols = ['TCP', 'UDP', 'ICMP', 'HTTP']
            counts = [337, 146, 50, 30]
            
            # 绘制饼图
            ax.pie(counts, labels=protocols, autopct='%1.1f%%')
            ax.set_title('协议分布统计')
            
            # 保存测试图表
            filename = f'font_test_{i+1}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"  测试图表已保存: {filename}")
            
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

def setup_font_with_cache_refresh():
    """设置字体并刷新缓存"""
    # 清除字体缓存
    fm._rebuild()
    
    # 重新获取字体列表
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 查找中文字体
    chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun']
    selected_font = None
    
    for font in chinese_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': [selected_font, 'DejaVu Sans'],
            'axes.unicode_minus': False
        })
        print(f"  使用字体: {selected_font}")
    else:
        print("  未找到中文字体")

def test_direct_font_path():
    """测试直接使用字体文件路径"""
    print("\n=== 直接字体路径测试 ===")
    
    import os
    from matplotlib.font_manager import FontProperties
    
    # Windows系统字体路径
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf",  # 黑体
        r"C:\Windows\Fonts\simsun.ttc",  # 宋体
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"找到字体文件: {font_path}")
            try:
                # 创建字体属性
                font_prop = FontProperties(fname=font_path)
                
                # 测试绘图
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.text(0.5, 0.5, '中文测试：协议统计', 
                       fontproperties=font_prop, 
                       fontsize=16, 
                       ha='center', va='center')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                
                filename = f'direct_font_test_{os.path.basename(font_path)}.png'
                plt.savefig(filename, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"  ✓ 直接字体测试成功: {filename}")
                return font_path
                
            except Exception as e:
                print(f"  ✗ 直接字体测试失败: {e}")
        else:
            print(f"字体文件不存在: {font_path}")
    
    return None

if __name__ == "__main__":
    print("开始字体诊断测试...")
    
    # 测试系统字体
    found_fonts = test_system_fonts()
    
    # 测试字体渲染
    test_font_rendering()
    
    # 测试直接字体路径
    working_font_path = test_direct_font_path()
    
    print(f"\n=== 诊断结果 ===")
    print(f"找到的中文字体: {found_fonts}")
    print(f"可用的字体文件路径: {working_font_path}")
    
    if working_font_path:
        print(f"\n建议使用字体文件: {working_font_path}")
    elif found_fonts:
        print(f"\n建议使用系统字体: {found_fonts[0]}")
    else:
        print("\n需要安装中文字体!")