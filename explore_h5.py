import h5py

def explore_h5_structure(filepath):
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

# 直接使用绝对路径  r用来表示原始字符串，避免转义字符的处理
explore_h5_structure(r'd:\QQ文件\2026020846-02素材与源码\2026020846-02素材与源码\assets\sample_data.h5')