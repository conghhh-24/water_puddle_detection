import os
import numpy as np
import scipy.io as sio


def create_test_mat_files(output_dir, num_files=5, size=(100, 100)):
    """
    生成测试用的 .mat 格式路面高程数据文件
    
    参数:
    - output_dir: 输出目录路径
    - num_files: 生成的文件数量
    - size: 每个矩阵的尺寸 (行, 列)
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📂 正在生成 {num_files} 个测试 .mat 文件到目录: {output_dir}")
    
    for i in range(1, num_files + 1):
        # 生成文件名，格式为 0001.mat, 0002.mat, ...
        filename = f"{i:04d}.mat"
        filepath = os.path.join(output_dir, filename)
        
        # 创建模拟的路面高程数据
        # 使用随机噪声加上一些地形特征来模拟真实路面
        np.random.seed(i)  # 设置随机种子以确保可重现性
        
        # 基础高程（假设平均高程为100mm）
        base_elevation = 100.0
        
        # 添加随机噪声（标准差为5mm）
        noise = np.random.normal(0, 5, size)
        
        # 添加一些洼地特征（模拟积水区域）
        rows, cols = size
        depression_center_row = rows // 2
        depression_center_col = cols // 2
        depression_radius = min(rows, cols) // 6
        
        # 创建洼地
        y_coords, x_coords = np.ogrid[:rows, :cols]
        depression_mask = (x_coords - depression_center_col)**2 + (y_coords - depression_center_row)**2 <= depression_radius**2
        depression_depth = -np.random.uniform(2, 8)  # 洼地深度2-8mm
        
        # 组合所有特征
        elevation_data = base_elevation + noise
        elevation_data[depression_mask] += depression_depth
        
        # 确保没有负值（实际路面高程不会为负）
        elevation_data = np.maximum(elevation_data, 0)
        
        # 保存为 .mat 文件
        # 使用 'im' 作为变量名，与转换脚本兼容
        sio.savemat(filepath, {'im': elevation_data})
        
        print(f"✅ 已生成: {filename} (尺寸: {size[0]}x{size[1]})")
    
    print(f"🎉 测试数据生成完成！共生成 {num_files} 个文件。")
    print(f"👉 测试文件保存在: {output_dir}")


if __name__ == "__main__":
    # 设置输出目录
    test_mat_dir = "data/mat2"
    
    # 生成5个测试文件，每个文件尺寸为100x100
    create_test_mat_files(test_mat_dir, num_files=5, size=(100, 100))
    
   