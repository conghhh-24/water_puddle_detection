import h5py
import os
import numpy as np

def explore_h5_structure(filepath):
    """探索 HDF5 文件结构"""
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
        
    with h5py.File(filepath, 'r') as f:
        print("=== HDF5文件结构 ===")
        print(f"文件路径: {filepath}")
        
        def print_structure(name, obj):
            if isinstance(obj, h5py.Group):
                print(f"Group: {name}")
                for key, val in obj.attrs.items():
                    print(f"  Attribute: {key} = {val}")
            elif isinstance(obj, h5py.Dataset):
                print(f"Dataset: {name} - Shape: {obj.shape}, Dtype: {obj.dtype}")
                
        f.visititems(print_structure)

def visualize_segment(filepath, dataset_path):
    """可视化指定数据集
    
    Args:
        filepath: HDF5文件路径
        dataset_path: 数据集的完整路径（如 'road_segments/0001'）或简单名称
    """
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
        
    with h5py.File(filepath, 'r') as f:
        # 首先检查文件结构
        print("\n=== 可用的数据集 ===")
        available_datasets = []
        
        def collect_datasets(name, obj):
            if isinstance(obj, h5py.Dataset):
                available_datasets.append(name)
                print(f"  - {name}")
                
        f.visititems(collect_datasets)
        #当 visititems() 遍历 HDF5 文件时，会为每个对象自动调用这个 回调函数 ，并传入两个参数：
        # name: 对象在 HDF5 文件中的路径名（字符串）
        # obj: 实际的对象本身（可能是 h5py.Group 或 h5py.Dataset）
        # 由于你的回调函数只处理 h5py.Dataset 类型的对象，所以只会收集到 'road_segments/0001' 和 'road_segments/0002'。

def analyze_h5_metadata(filepath):
    """分析 HDF5 文件的完整元数据"""
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
    
    print(f"\n=== HDF5 文件元数据分析 ===")
    
    with h5py.File(filepath, 'r') as f:
        # 分析根组属性
        road_segments = f.get('road_segments')
        if road_segments is not None:
            print("📁 根组信息:")
            print(f"  - 描述: {road_segments.attrs.get('description', 'N/A')}")
            print(f"  - 单位: {road_segments.attrs.get('unit', 'N/A')}")
            print()
        
        # 获取所有数据集名称
        dataset_names = []
        def collect_datasets(name, obj):
            if isinstance(obj, h5py.Dataset):
                dataset_names.append(name)
        
        f.visititems(collect_datasets)
        if not dataset_names:
            print("未找到任何数据集")
            return
            
        dataset_names.sort()
        
        print(f"📊 数据集统计 (共 {len(dataset_names)} 个):")
        print(f"{'数据集':<15} {'形状':<12} {'dtype':<10} {'有效点%':<8} {'均值':<10} {'标准差':<8} {'范围'}")
        print("-" * 80)
        
        all_valid_ratios = []
        all_means = []
        all_stds = []
        
        for name in dataset_names:
            data = f[name][:]
            
            # 创建有效掩码（排除零值）
            valid_mask = data != 0
            valid_ratio = np.mean(valid_mask) * 100 if data.size > 0 else 0
            
            # 仅基于有效数据计算统计量
            if np.any(valid_mask):
                valid_data = data[valid_mask]
                mean_val = np.mean(valid_data)
                std_val = np.std(valid_data)
                min_val = np.min(data)
                max_val = np.max(data)
            else:
                mean_val = std_val = min_val = max_val = 0.0
            
            # 检查异常值
            has_nan = np.any(np.isnan(data))
            has_inf = np.any(np.isinf(data))
            anomaly_flags = ""
            if has_nan:
                anomaly_flags += "NaN "
            if has_inf:
                anomaly_flags += "Inf "
            
            range_str = f"{min_val:.1f} ~ {max_val:.1f}"
            if anomaly_flags:
                range_str += f" ({anomaly_flags.strip()})"
            
            print(f"{name:<15} {str(data.shape):<12} {str(data.dtype):<10} {valid_ratio:<7.1f}% {mean_val:<9.1f} {std_val:<7.2f} {range_str}")
            
            all_valid_ratios.append(valid_ratio)
            all_means.append(mean_val)
            all_stds.append(std_val)
        
        print()
        print("📈 全局统计:")
        if all_valid_ratios:
            print(f"  - 平均有效点比例: {np.mean(all_valid_ratios):.1f}% ± {np.std(all_valid_ratios):.1f}%")
            print(f"  - 平均高程: {np.mean(all_means):.1f} ± {np.std(all_means):.1f}")
            print(f"  - 平均标准差: {np.mean(all_stds):.2f} ± {np.std(all_stds):.2f}")

def visualize_segment(filepath, dataset_path):
    """可视化指定数据集
    
    Args:
        filepath: HDF5文件路径
        dataset_path: 数据集的完整路径（如 'road_segments/0001'）或简单名称
    """
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
        
    with h5py.File(filepath, 'r') as f:
        # 首先检查文件结构
        print("\n=== 可用的数据集 ===")
        available_datasets = []
        
        def collect_datasets(name, obj):
            if isinstance(obj, h5py.Dataset):
                available_datasets.append(name)
               
                
        f.visititems(collect_datasets)
        
        # 尝试访问指定的数据集路径
        if dataset_path in available_datasets:
            data = f[dataset_path][:]
            try:
                import matplotlib.pyplot as plt
                plt.figure(figsize=(12, 6))
                plt.imshow(data, cmap='terrain')
                plt.colorbar(label='高程 (m)')
                plt.title(f'数据集: {dataset_path}')
                plt.xlabel('横向位置')
                plt.ylabel('纵向位置')
                plt.show()
            except ImportError:
                print("matplotlib 未安装，无法显示图像")
                print(f"数据形状: {data.shape}, 数据类型: {data.dtype}")
        else:
            print(f"\n错误: 找不到数据集 '{dataset_path}'")
            print("请从上面列出的可用数据集中选择一个")

# 使用项目内的示例数据
sample_data_path = os.path.join(os.path.dirname(__file__), 'assets', 'sample_data.h5')
# 1. __file__
# 这是一个特殊的Python变量，表示当前文件的完整路径。
#
# 2. os.path.dirname(__file__)
# os.path.dirname() 函数用于获取路径中的目录部分
# 它会去掉文件名，只返回目录路径
# 3. os.path.join()
# 这是一个跨平台的路径拼接函数
# 它会根据操作系统的不同自动使用正确的路径分隔符
# Windows使用 \，Unix/Linux/Mac使用 /
# 实际执行过程
# 假设你的文件位置是：e:\code_all\Github\water_puddle_detection\explore_h5.py
#
# __file__ = 'e:\\code_all\\Github\\water_puddle_detection\\explore_h5.py'
#
# os.path.dirname(__file__) = 'e:\\code_all\\Github\\water_puddle_detection'
#
# os.path.join('e:\\code_all\\Github\\water_puddle_detection', 'assets', 'sample_data.h5') = 'e:\\code_all\\Github\\water_puddle_detection\\assets\\sample_data.h5'
if os.path.exists(sample_data_path):
    print("使用项目内的示例数据:")
    explore_h5_structure(sample_data_path)
    analyze_h5_metadata(sample_data_path)
    # 可视化第1-3个路段数据
    for i in range(1, 4):
        print(f"\n可视化第{i}个路段数据: road_segments/000{i}")
        visualize_segment(sample_data_path, f'road_segments/000{i}')

    
else:
    print("项目内未找到 sample_data.h5 文件")
    print("请将你的 HDF5 文件放在 assets 目录下")