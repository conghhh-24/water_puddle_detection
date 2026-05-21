import h5py
import os

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

if os.path.exists(sample_data_path):
    print("使用项目内的示例数据:")
    explore_h5_structure(sample_data_path)
    # 可视化第一个路段数据
    print(f"\n可视化第一个路段数据: road_segments/0001")
    visualize_segment(sample_data_path, 'road_segments/0001')
else:
    print("项目内未找到 sample_data.h5 文件")
    print("请将你的 HDF5 文件放在 assets 目录下")