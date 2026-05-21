# 🌧️ 第2课：点云数据处理与HDF5格式详解

> **课时**：2.5小时  
> **学习目标**：掌握点云数据的存储、读取、转换和预处理技术  
> **先修要求**：完成第1课，熟悉Python基础和NumPy数组操作

---

## 📚 课程内容概览

### 本课学习路线
1. **点云数据基础**（30分钟）- 理解数据格式和特点
2. **HDF5格式深度解析**（45分钟）- 掌握高效数据存储技术  
3. **数据转换实战**（60分钟）- 实现.mat到.h5的转换工具
4. **数据预处理技术**（45分钟）- 异常值检测与修复

---

## 🔍 第一部分：点云数据基础（30分钟）

### 2.1 什么是点云数据？

**定义**：点云是由大量三维空间点组成的数据集合，每个点包含(x, y, z)坐标信息。

**在道路检测中的应用**：
- **无人机LiDAR扫描**：获取路面高程信息
- **高精度地形建模**：毫米级精度的路表形貌
- **病害识别基础**：积水、坑槽、车辙等特征提取

### 2.2 点云数据格式对比

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| **.mat (MATLAB)** | 二进制矩阵，兼容性好 | 科研数据交换 |
| **.h5 (HDF5)** | 分层结构，高压缩比 | 大规模数据存储 |
| **.las/.laz** | LiDAR专用格式 | 专业测绘软件 |
| **.ply** | 简单文本/二进制 | 3D模型交换 |

### 2.3 道路点云数据特点

#### 数据结构特征
```python
# 典型的道路点云数据结构
# 形状: (rows, cols) = (纵向采样点数, 横向采样点数)
# 单位: 米(m) 或 毫米(mm)
# 示例: 1000×500 的矩阵表示 100m×50m 的路面区域

import numpy as np
road_matrix = np.array([[0.001, 0.002, ...],  # 第一行高程数据
                       [0.003, 0.001, ...],   # 第二行高程数据
                       ...])
```

#### 数据质量挑战
- **异常值**：传感器噪声、遮挡导致的错误测量
- **缺失值**：通常用0或NaN表示
- **分辨率不一致**：不同设备采集的精度差异
- **数据量巨大**：单个路段可能包含百万级数据点

### 2.4 为什么选择HDF5格式？

**HDF5的优势**：
- ✅ **高效压缩**：gzip压缩可减少70%+存储空间
- ✅ **分层组织**：类似文件系统的组(Group)和数据集(Dataset)
- ✅ **快速访问**：支持部分读取，无需加载整个文件
- ✅ **跨平台兼容**：支持多种编程语言
- ✅ **元数据支持**：可存储描述信息和单位

**项目中的具体应用**：
```python
# 项目HDF5文件结构
road_segments/           # 主组(Group)
├── segment_001         # 数据集(Dataset): 路段1的高程矩阵
├── segment_002         # 数据集(Dataset): 路段2的高程矩阵  
└── ...                 # 更多路段数据
```

---

## 💾 第二部分：HDF5格式深度解析（45分钟）

### 3.1 HDF5核心概念

#### 基本组件
- **File**：HDF5文件本身
- **Group**：类似文件夹，用于组织数据
- **Dataset**：实际的数据数组
- **Attributes**：元数据，描述数据的属性

#### 层次结构示例
```
pavement_data.h5
└── road_segments (Group)
    ├── description: "路面三维高程矩阵集合" (Attribute)
    ├── unit: "mm" (Attribute)
    ├── segment_001 (Dataset) → shape=(1000, 500), dtype=float64
    ├── segment_002 (Dataset) → shape=(1000, 500), dtype=float64
    └── ...
```

### 3.2 h5py库基础操作

#### 安装和导入
```python
# 安装
pip install h5py

# 导入
import h5py
import numpy as np
```

#### 创建HDF5文件
```python
# 写入模式创建新文件
with h5py.File('test_data.h5', 'w') as f:
    # 创建组
    road_group = f.create_group("road_segments")
    
    # 添加元数据
    road_group.attrs['description'] = "测试路面数据"
    road_group.attrs['unit'] = "mm"
    
    # 创建数据集
    test_matrix = np.random.rand(100, 50) * 0.1
    road_group.create_dataset(
        'segment_001',
        data=test_matrix,
        compression="gzip",      # 启用压缩
        compression_opts=4       # 压缩级别(0-9)
    )
```

#### 读取HDF5文件
```python
# 读取模式打开文件
with h5py.File('test_data.h5', 'r') as f:
    # 访问组
    road_group = f['road_segments']
    
    # 读取元数据
    description = road_group.attrs['description']
    unit = road_group.attrs['unit']
    
    # 列出所有数据集
    segment_names = list(road_group.keys())
    print(f"路段列表: {segment_names}")
    
    # 读取具体数据
    segment_data = road_group['segment_001'][:]
    print(f"数据形状: {segment_data.shape}")
```

#### 高级特性
```python
# 部分读取（节省内存）
with h5py.File('large_data.h5', 'r') as f:
    # 只读取前100行
    partial_data = f['road_segments/segment_001'][0:100, :]
    
# 动态创建数据集
def add_new_segment(h5_file, segment_name, matrix_data):
    with h5py.File(h5_file, 'a') as f:  # 'a' = append模式
        f['road_segments'].create_dataset(
            segment_name,
            data=matrix_data,
            compression="gzip"
        )
```

### 3.3 实战练习：探索内置示例数据

#### 步骤1：查看文件结构
```python
# 创建 explore_h5.py
import h5py

def explore_h5_structure(filepath):
    with h5py.File(filepath, 'r') as f:
        print("=== HDF5文件结构 ===")
        print(f"文件路径: {filepath}")
        
        # 递归打印结构
        def print_structure(name, obj):
            if isinstance(obj, h5py.Group):
                print(f"Group: {name}")
                for key, val in obj.attrs.items():
                    print(f"  Attribute: {key} = {val}")
            elif isinstance(obj, h5py.Dataset):
                print(f"Dataset: {name} - Shape: {obj.shape}, Dtype: {obj.dtype}")
                
        f.visititems(print_structure)

# 使用示例
explore_h5_structure('assets/sample_data.h5')
```

#### 步骤2：读取并可视化单个路段
```python
import matplotlib.pyplot as plt

def visualize_segment(filepath, segment_name):
    with h5py.File(filepath, 'r') as f:
        data = f['road_segments'][segment_name][:]
        
    plt.figure(figsize=(12, 6))
    plt.imshow(data, cmap='terrain')
    plt.colorbar(label='高程 (m)')
    plt.title(f'路段: {segment_name}')
    plt.xlabel('横向位置')
    plt.ylabel('纵向位置')
    plt.show()

# 使用示例
visualize_segment('assets/sample_data.h5', 'segment_001')
```

---

## 🔄 第三部分：数据转换实战（60分钟）

### 4.1 分析现有转换脚本

让我们深入分析项目中的 `assets/data_convert_to_h5.py`：

```python
# assets/data_convert_to_h5.py 关键代码解析
import os
import numpy as np
import scipy.io as sio  # 用于读取.mat文件
import h5py

def convert_mat_to_h5(src_folder, h5_filepath):
    """
    将文件夹下的所有 .mat 高程矩阵打包进一个 HDF5 数据库文件
    """
    print(f"📂 正在扫描目录: {src_folder}")
    
    # 1. 获取所有.mat文件并排序
    files = [f for f in os.listdir(src_folder) if f.endswith('.mat')]
    files.sort()  # 确保 0001, 0002 顺序正确
    
    # 2. 创建HDF5文件
    with h5py.File(h5_filepath, 'w') as h5f:
        road_group = h5f.create_group("road_segments")
        
        # 3. 添加元数据
        road_group.attrs['description'] = "路面三维高程矩阵集合"
        road_group.attrs['unit'] = "mm"
        
        # 4. 逐个处理.mat文件
        for f in files:
            mat_path = os.path.join(src_folder, f)
            try:
                # 加载.mat文件
                mat_data = sio.loadmat(mat_path)
                
                # 提取矩阵数据（支持'im'或'z'键名）
                matrix_data = None
                if 'im' in mat_data:
                    matrix_data = mat_data['im']
                elif 'z' in mat_data:
                    matrix_data = mat_data['z']
                    
                if matrix_data is None:
                    continue
                    
                # 创建数据集名称（去掉.mat后缀）
                dataset_name = f.replace('.mat', '')
                
                # 存入HDF5（启用压缩）
                road_group.create_dataset(
                    dataset_name,
                    data=matrix_data,
                    compression="gzip",
                    compression_opts=4
                )
                
            except Exception as e:
                print(f"❌ 转换 {f} 时出错: {e}")
```

### 4.2 创建自己的测试数据

#### 步骤1：生成模拟.mat文件
```python
# create_test_mat.py
import scipy.io as sio
import numpy as np

def create_test_mat_files(output_dir, num_files=5):
    """创建测试用的.mat文件"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(1, num_files + 1):
        # 创建模拟路面数据（包含一些凹陷区域模拟积水）
        rows, cols = 200, 100
        base_height = 0.05  # 基础高程5cm
        
        # 添加随机噪声
        data = np.random.normal(base_height, 0.001, (rows, cols))
        
        # 添加人工凹陷（模拟积水坑）
        if i % 2 == 0:  # 偶数文件添加凹陷
            center_row, center_col = rows//2, cols//2
            for r in range(center_row-10, center_row+10):
                for c in range(center_col-10, center_col+10):
                    if 0 <= r < rows and 0 <= c < cols:
                        distance = np.sqrt((r-center_row)**2 + (c-center_col)**2)
                        data[r, c] -= 0.005 * np.exp(-distance/5)  # 高斯凹陷
        
        # 保存为.mat文件
        filename = f"{output_dir}/segment_{i:04d}.mat"
        sio.savemat(filename, {'im': data})
        print(f"创建文件: {filename}")

# 使用示例
create_test_mat_files('test_mat_data', 3)
```

#### 步骤2：使用转换脚本
```python
# test_conversion.py
from assets.data_convert_to_h5 import convert_mat_to_h5

# 转换测试数据
convert_mat_to_h5('test_mat_data', 'test_output.h5')
```

### 4.3 改进转换脚本

#### 添加功能：支持多种数据键名
```python
def extract_matrix_from_mat(mat_data):
    """从.mat文件中提取高程矩阵，支持多种键名"""
    possible_keys = ['im', 'z', 'height', 'elevation', 'data']
    
    for key in possible_keys:
        if key in mat_data:
            matrix = mat_data[key]
            # 确保是2D数组
            if matrix.ndim == 2:
                return matrix
            elif matrix.ndim == 3 and matrix.shape[2] == 1:
                return matrix[:, :, 0]  # 去掉单通道维度
    
    # 如果没有找到标准键名，尝试第一个2D数组
    for key, value in mat_data.items():
        if isinstance(value, np.ndarray) and value.ndim == 2:
            return value
    
    return None
```

#### 添加功能：数据验证
```python
def validate_matrix(matrix, min_size=100):
    """验证矩阵数据的有效性"""
    if matrix is None:
        return False, "矩阵为空"
    
    if matrix.size < min_size:
        return False, f"数据量过小 ({matrix.size} < {min_size})"
    
    if np.all(matrix == 0):
        return False, "所有值都为零"
    
    # 检查是否有有效数据（非零值）
    valid_mask = matrix != 0
    if np.sum(valid_mask) == 0:
        return False, "无有效数据点"
    
    return True, "数据有效"
```

### 4.4 完整的改进版转换脚本
```python
# improved_data_convert.py
import os
import numpy as np
import scipy.io as sio
import h5py

def improved_convert_mat_to_h5(src_folder, h5_filepath, compression_level=4):
    """
    改进版的.mat到.h5转换脚本
    """
    print(f"📂 扫描目录: {src_folder}")
    
    files = [f for f in os.listdir(src_folder) if f.endswith('.mat')]
    files.sort()
    
    if not files:
        print("❌ 未找到任何 .mat 文件！")
        return
    
    print(f"⏳ 开始转换 {len(files)} 个文件...")
    
    success_count = 0
    with h5py.File(h5_filepath, 'w') as h5f:
        road_group = h5f.create_group("road_segments")
        road_group.attrs['description'] = "路面三维高程矩阵集合"
        road_group.attrs['unit'] = "mm"
        road_group.attrs['conversion_date'] = str(np.datetime64('now'))
        
        for f in files:
            mat_path = os.path.join(src_folder, f)
            try:
                mat_data = sio.loadmat(mat_path, squeeze_me=True)
                matrix_data = extract_matrix_from_mat(mat_data)
                
                is_valid, message = validate_matrix(matrix_data)
                if not is_valid:
                    print(f"⚠️ 跳过 {f}: {message}")
                    continue
                
                dataset_name = f.replace('.mat', '')
                road_group.create_dataset(
                    dataset_name,
                    data=matrix_data,
                    compression="gzip",
                    compression_opts=compression_level
                )
                success_count += 1
                print(f"✅ 转换成功: {f}")
                
            except Exception as e:
                print(f"❌ 转换 {f} 失败: {e}")
    
    print(f"🎉 转换完成！成功: {success_count}/{len(files)}")

# 辅助函数（前面定义的）
def extract_matrix_from_mat(mat_data):
    possible_keys = ['im', 'z', 'height', 'elevation', 'data']
    for key in possible_keys:
        if key in mat_data:
            matrix = mat_data[key]
            if matrix.ndim == 2:
                return matrix
            elif matrix.ndim == 3 and matrix.shape[2] == 1:
                return matrix[:, :, 0]
    
    for key, value in mat_data.items():
        if isinstance(value, np.ndarray) and value.ndim == 2:
            return value
    return None

def validate_matrix(matrix, min_size=100):
    if matrix is None:
        return False, "矩阵为空"
    if matrix.size < min_size:
        return False, f"数据量过小 ({matrix.size} < {min_size})"
    if np.all(matrix == 0):
        return False, "所有值都为零"
    valid_mask = matrix != 0
    if np.sum(valid_mask) == 0:
        return False, "无有效数据点"
    return True, "数据有效"
```

---

## 🛠️ 第四部分：数据预处理技术（45分钟）

### 5.1 异常值检测与修复

#### 3σ原则异常值检测
```python
def detect_outliers_3sigma(data, sigma_threshold=3):
    """使用3σ原则检测异常值"""
    valid_mask = data != 0  # 假设0表示无效数据
    if np.sum(valid_mask) == 0:
        return np.zeros_like(data, dtype=bool)
    
    valid_data = data[valid_mask]
    mean_val = np.mean(valid_data)
    std_val = np.std(valid_data)
    
    # 异常值阈值
    lower_bound = mean_val - sigma_threshold * std_val
    upper_bound = mean_val + sigma_threshold * std_val
    
    # 标记异常值（超出范围且非零的点）
    outlier_mask = (data < lower_bound) | (data > upper_bound)
    outlier_mask &= (data != 0)
    
    return outlier_mask
```

#### 中值滤波去噪
```python
from scipy.ndimage import median_filter

def remove_outliers_median_filter(data, filter_size=5):
    """使用中值滤波修复异常值"""
    # 创建有效数据掩码
    valid_mask = data != 0
    
    # 用中位数填充零值
    median_val = np.median(data[valid_mask])
    data_filled = np.where(data == 0, median_val, data)
    
    # 应用中值滤波
    filtered_data = median_filter(data_filled, size=filter_size)
    
    # 检测并修复异常值
    diff = np.abs(data_filled - filtered_data)
    mu, sigma = np.mean(diff), np.std(diff)
    outlier_mask = diff > (mu + 3 * sigma)
    
    # 用滤波结果替换异常值
    cleaned_data = np.where(outlier_mask, filtered_data, data_filled)
    
    return cleaned_data, outlier_mask
```

### 5.2 在项目中的实际应用

回顾 `app.py` 中的预处理函数：
```python
# app.py 中的 load_and_preprocess_h5 函数关键部分
def load_and_preprocess_h5(h5_path, start_segment, num_blocks, max_std=15.0, overlap_rows=8):
    with h5py.File(h5_path, 'r') as h5f:
        group = h5f['road_segments']
        # ... 数据加载逻辑 ...
        
        # 异常值跳过
        current_std = np.std(data[valid_mask])
        if current_std > max_std:
            st.toast(f"⚠️ 触发保护机制: 自动跳过坏死路段 [{name}]")
            continue
        
        # 中值填充零值
        data_median = np.median(data[valid_mask])
        data = np.where(data == 0, data_median, data)
        
        # 中值滤波去噪
        ref_matrix = median_filter(data, size=5)
        diff = np.abs(data - ref_matrix)
        mu, sigma = np.mean(diff), np.std(diff)
        outlier_mask = diff > (mu + 3 * sigma)
        data[outlier_mask] = ref_matrix[outlier_mask]
```

### 5.3 实战练习：实现完整的预处理管道

```python
# preprocessing_pipeline.py
import numpy as np
from scipy.ndimage import median_filter

class RoadDataPreprocessor:
    def __init__(self, max_std=15.0, filter_size=5, sigma_threshold=3):
        self.max_std = max_std
        self.filter_size = filter_size
        self.sigma_threshold = sigma_threshold
    
    def preprocess_single_segment(self, data):
        """预处理单个路段数据"""
        # 1. 检查数据有效性
        valid_mask = data != 0
        if np.sum(valid_mask) < 100:
            return None, "数据量不足"
        
        # 2. 标准差检查
        current_std = np.std(data[valid_mask])
        if current_std > self.max_std:
            return None, f"标准差过大 ({current_std:.2f} > {self.max_std})"
        
        # 3. 零值填充
        data_median = np.median(data[valid_mask])
        data_filled = np.where(data == 0, data_median, data)
        
        # 4. 中值滤波去噪
        ref_matrix = median_filter(data_filled, size=self.filter_size)
        diff = np.abs(data_filled - ref_matrix)
        mu, sigma = np.mean(diff), np.std(diff)
        outlier_mask = diff > (mu + self.sigma_threshold * sigma)
        cleaned_data = np.where(outlier_mask, ref_matrix, data_filled)
        
        # 5. 数据裁剪（去除极端值）
        z_min, z_max = np.percentile(cleaned_data, [0.1, 99.9])
        final_data = np.clip(cleaned_data, z_min, z_max)
        
        return final_data, "预处理成功"
    
    def process_multiple_segments(self, segments_data):
        """批量处理多个路段"""
        processed_segments = {}
        skipped_segments = {}
        
        for name, data in segments_data.items():
            result, message = self.preprocess_single_segment(data)
            if result is not None:
                processed_segments[name] = result
            else:
                skipped_segments[name] = message
        
        return processed_segments, skipped_segments
```

---

## 📝 第五部分：课后作业与实践

### 6.1 基础作业

#### 作业1：HDF5文件探索
- [ ] 使用提供的脚本探索 `assets/sample_data.h5`
- [ ] 记录文件结构、数据形状和元数据信息
- [ ] 可视化至少3个不同路段的数据

#### 作业2：数据转换实践
- [ ] 使用 `create_test_mat.py` 生成测试数据
- [ ] 运行转换脚本生成HDF5文件
- [ ] 验证转换结果的正确性

### 6.2 进阶作业

#### 作业3：预处理管道实现
- [ ] 实现完整的 `RoadDataPreprocessor` 类
- [ ] 测试不同参数对预处理结果的影响
- [ ] 比较预处理前后的数据质量差异

#### 作业4：性能优化实验
- [ ] 测试不同压缩级别的文件大小和读取速度
- [ ] 分析大数据集的部分读取性能优势
- [ ] 记录内存使用情况的变化

### 6.3 思考题

1. **数据格式选择**：除了HDF5，还有哪些适合大规模科学数据的存储格式？各自的优缺点是什么？

2. **异常值处理**：3σ原则在什么情况下可能失效？有哪些替代的异常值检测方法？

3. **工程实践**：在实际项目中，如何平衡数据质量、处理速度和存储成本？

4. **扩展应用**：如何将这套数据处理流程应用到其他类型的传感器数据（如温度、湿度）？

---

## 🔍 第六部分：常见问题FAQ

### Q1：读取.mat文件时出现版本兼容性问题怎么办？
**解决方案**：
```python
# 使用squeeze_me和struct_as_record参数
mat_data = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
```

### Q2：HDF5文件过大，内存不足怎么办？
**解决方案**：
```python
# 使用chunks参数启用分块存储
road_group.create_dataset(
    dataset_name,
    data=matrix_data,
    chunks=True,  # 自动选择块大小
    compression="gzip"
)

# 读取时使用切片
partial_data = dataset[100:200, 200:300]  # 只读取需要的部分
```

### Q3：如何处理不同坐标系的点云数据？
**解决方案**：
```python
# 添加坐标系转换函数
def transform_coordinates(data, source_crs, target_crs):
    """坐标系转换（需要安装pyproj库）"""
    from pyproj import Transformer
    transformer = Transformer.from_crs(source_crs, target_crs)
    # 实现具体的坐标转换逻辑
    pass
```

---

## 📚 第七部分：延伸学习资源

### 推荐文档
- [h5py官方文档](https://docs.h5py.org/) - HDF5 Python接口
- [SciPy I/O文档](https://docs.scipy.org/doc/scipy/reference/io.html) - 数据格式处理
- [NumPy数组操作指南](https://numpy.org/doc/stable/user/quickstart.html)

### 相关技术
- **点云处理库**：Open3D, PCL (Point Cloud Library)
- **地理信息系统**：GDAL, rasterio
- **数据压缩**：了解不同压缩算法的适用场景

### 下节课预告
**第3课：3D地形重构与可视化技术**
- 超分辨率插值算法实现
- 多路段拼接技术详解
- Plotly 3D可视化高级配置
- 地形剖面图和网格线控制

---

> **学习提示**：数据处理是整个项目的基础，确保您完全理解HDF5的操作和预处理技术。这些技能在后续课程中会反复用到。

**祝您学习愉快！** 🚀

---
*第二课内容最后更新：2026年5月19日*