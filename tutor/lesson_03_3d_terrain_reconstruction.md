# 🌧️ 第3课：3D地形重构与可视化技术

> **课时**：2.5小时  
> **学习目标**：掌握超分辨率插值、多路段拼接和交互式3D可视化技术  
> **先修要求**：完成第1-2课，熟悉NumPy数组操作和HDF5数据处理

---

## 📚 课程内容概览

### 本课学习路线
1. **3D地形重构基础**（30分钟）- 理解插值算法和多路段拼接
2. **超分辨率技术详解**（45分钟）- 掌握scipy.ndimage.zoom的高级用法  
3. **Plotly 3D可视化**（60分钟）- 实现交互式地形渲染
4. **性能优化实践**（45分钟）- 大数据集的内存管理和渲染优化

---

## 🗺️ 第一部分：3D地形重构基础（30分钟）

### 3.1 插值算法原理

#### 为什么需要插值？
原始点云数据通常具有固定的采样间隔（如10cm×10cm），但在水膜推演等精细计算中，需要更高的空间分辨率来获得准确结果。

**插值的作用**：
- ✅ 提高空间分辨率（超分辨率）
- ✅ 平滑地形表面
- ✅ 改善数值计算稳定性

#### 常见插值方法对比

| 方法 | 特点 | 适用场景 |
|------|------|----------|
| **最近邻插值** | 速度快，保持原值 | 分类数据、离散值 |
| **线性插值** | 连续但不光滑 | 一般连续数据 |
| **三次样条插值** | 光滑连续，计算复杂 | 高精度地形建模 |
| **三次卷积插值** | 平衡速度和质量 | 图像/地形处理 |

### 3.2 多路段拼接技术

#### 拼接挑战
- **高程偏差**：相邻路段可能存在系统性高程差异
- **重叠区域**：需要平滑过渡避免台阶效应
- **数据完整性**：确保拼接后数据连续无缺失

#### 项目中的拼接策略
```python
# app.py 中的多路段拼接关键代码
def load_and_preprocess_h5(h5_path, start_segment, num_blocks, overlap_rows=8):
    # ... 数据加载 ...
    
    while blocks_loaded < num_blocks:
        # ... 加载当前路段 ...
        
        if zz is not None:  # 不是第一个路段
            # 1. 计算高程偏差并校正
            gaocha = np.mean(edge_zz) - np.mean(edge_data)
            data += gaocha
            
            # 2. 余弦加权融合重叠区域
            x = np.linspace(0, 1, overlap_rows)
            weights_1d = (1 + np.cos(np.pi * x)) / 2.0
            weights = weights_1d.reshape(-1, 1)
            
            overlap_A = zz[-overlap_rows:, :]
            overlap_B = data[:overlap_rows, :]
            zz[-overlap_rows:, :] = overlap_A * weights + overlap_B * (1.0 - weights)
            
            # 3. 拼接非重叠部分
            zz = np.vstack((zz, data[overlap_rows:, :]))
```

### 3.3 超分辨率的实际需求

#### 水膜推演对分辨率的要求
- **物理精度**：水膜厚度变化通常在毫米级别
- **数值稳定性**：高分辨率减少数值误差累积
- **细节保留**：准确捕捉微小凹陷和凸起

#### 项目中的超分辨率实现
```python
# app.py 中的超分辨率代码
scale_factor = 2
original_dx_mm = 100.0  # 原始采样间隔100mm
fine_dx_mm = original_dx_mm / scale_factor  # 超分辨率后50mm

with st.spinner("⏳ 正在进行超分辨率地图插值..."):
    fine_matrix_crop = zoom(matrix_crop, scale_factor, order=3)
```

---

## 🔍 第二部分：超分辨率技术详解（45分钟）

### 4.1 scipy.ndimage.zoom 深度解析

#### 基本语法
```python
from scipy.ndimage import zoom

# 基本用法
zoomed_array = zoom(input_array, zoom_factor, order=3)

# 参数详解
zoomed_array = zoom(
    input,           # 输入数组
    zoom,            # 缩放因子（标量或元组）
    order=3,         # 插值阶数（0-5）
    mode='constant', # 边界处理模式
    cval=0.0,        # 边界填充值
    prefilter=True   # 是否预滤波
)
```

#### order参数详解
- **order=0**: 最近邻插值
- **order=1**: 双线性插值  
- **order=2**: 二次样条插值
- **order=3**: 三次样条插值（默认，推荐用于地形）
- **order=4,5**: 更高阶样条（计算开销大）

### 4.2 实战练习：不同插值方法对比

#### 创建测试脚本
```python
# interpolation_comparison.py
import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt

def create_test_terrain():
    """创建测试地形数据"""
    x = np.linspace(0, 10, 50)
    y = np.linspace(0, 5, 25)
    X, Y = np.meshgrid(x, y)
    
    # 创建包含多种特征的地形
    terrain = (
        0.1 * np.sin(X) +           # 大尺度起伏
        0.05 * np.cos(2*Y) +        # 中尺度起伏  
        0.02 * np.random.rand(25, 50) +  # 小尺度噪声
        -0.03 * np.exp(-((X-5)**2 + (Y-2.5)**2)/2)  # 局部凹陷
    )
    return terrain

def compare_interpolation_methods():
    """比较不同插值方法的效果"""
    original = create_test_terrain()
    zoom_factor = 3
    
    methods = [
        (0, '最近邻插值'),
        (1, '双线性插值'), 
        (3, '三次样条插值'),
        (5, '五次样条插值')
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for i, (order, title) in enumerate(methods):
        zoomed = zoom(original, zoom_factor, order=order)
        
        axes[i].imshow(zoomed, cmap='terrain', aspect='auto')
        axes[i].set_title(f'{title} (order={order})')
        axes[i].set_xlabel('X方向')
        axes[i].set_ylabel('Y方向')
    
    plt.tight_layout()
    plt.show()
    
    return original, [zoom(original, zoom_factor, order=order) for order, _ in methods]

# 运行比较
original, zoomed_results = compare_interpolation_methods()
```

### 4.3 边界处理和预滤波

#### 边界处理模式
```python
# 不同边界处理模式的效果
boundary_modes = ['constant', 'nearest', 'reflect', 'wrap']

for mode in boundary_modes:
    result = zoom(original_data, 2, order=3, mode=mode, cval=-999)
    # 观察边界区域的处理效果
```

#### 预滤波的作用
- **prefilter=True**（默认）：应用抗混叠滤波器，减少高频噪声
- **prefilter=False**：跳过预滤波，速度更快但可能产生伪影

```python
# 性能对比
import time

data = np.random.rand(1000, 500)

# 带预滤波
start = time.time()
result1 = zoom(data, 2, order=3, prefilter=True)
time1 = time.time() - start

# 无预滤波  
start = time.time()
result2 = zoom(data, 2, order=3, prefilter=False)
time2 = time.time() - start

print(f"预滤波时间: {time1:.3f}s")
print(f"无预滤波时间: {time2:.3f}s")
print(f"加速比: {time1/time2:.2f}x")
```

### 4.4 自定义超分辨率函数

#### 改进版超分辨率函数
```python
# enhanced_zoom.py
import numpy as np
from scipy.ndimage import zoom, gaussian_filter

def enhanced_super_resolution(data, scale_factor, method='cubic', smooth_sigma=None):
    """
    增强版超分辨率函数
    
    Parameters:
    -----------
    data : array-like
        输入数据
    scale_factor : float or tuple
        缩放因子
    method : str
        插值方法 ('nearest', 'linear', 'cubic', 'quintic')
    smooth_sigma : float, optional
        高斯平滑标准差，用于后处理
        
    Returns:
    --------
    zoomed_data : array
        超分辨率后的数据
    """
    # 方法映射
    order_map = {
        'nearest': 0,
        'linear': 1, 
        'cubic': 3,
        'quintic': 5
    }
    
    if method not in order_map:
        raise ValueError(f"不支持的方法: {method}")
    
    order = order_map[method]
    
    # 执行超分辨率
    zoomed = zoom(data, scale_factor, order=order, prefilter=True)
    
    # 可选的后处理平滑
    if smooth_sigma is not None:
        zoomed = gaussian_filter(zoomed, sigma=smooth_sigma)
    
    return zoomed

# 使用示例
original_data = np.random.rand(200, 100)
high_res = enhanced_super_resolution(
    original_data, 
    scale_factor=2, 
    method='cubic', 
    smooth_sigma=0.5
)
```

---

## 🎨 第三部分：Plotly 3D可视化（60分钟）

### 5.1 Plotly 3D Surface基础

#### 基本3D地形图
```python
import plotly.graph_objects as go
import numpy as np

def create_basic_3d_terrain(matrix, dx_mm=100.0):
    """创建基本的3D地形图"""
    # 创建坐标轴
    x_dm = np.arange(matrix.shape[1]) * (dx_mm / 100.0)  # 转换为分米
    y_dm = np.arange(matrix.shape[0]) * (dx_mm / 100.0)
    z_m = matrix  # 高程已经是米
    
    fig = go.Figure()
    fig.add_trace(go.Surface(
        z=z_m, x=x_dm, y=y_dm,
        colorscale='Portland',  # 地形专用色谱
        showscale=False
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis_title='车道宽度(dm)',
            yaxis_title='路线长度(dm)', 
            zaxis_title='路表高程(m)'
        ),
        height=500
    )
    
    return fig
```

### 5.2 项目中的高级可视化

#### 分析 `create_3d_figure` 函数
```python
# app.py 中的 create_3d_figure 函数关键部分
def create_3d_figure(matrix, water_surf=None, water_depth=None, dx_mm=100.0, show_grid=True, dark_mode=False):
    x_dm = np.arange(matrix.shape[1]) * (dx_mm / 100.0)
    y_dm = np.arange(matrix.shape[0]) * (dx_mm / 100.0)
    z_m = matrix

    # 主题设置
    template = "plotly_dark" if dark_mode else "plotly_white"
    font_color = "#c9d1d9" if dark_mode else "#2c3e50"
    grid_color = "rgba(255, 255, 255, 0.2)" if dark_mode else "rgba(0, 0, 0, 0.5)"

    fig = go.Figure()
    
    # 1. 添加路表高程
    fig.add_trace(go.Surface(
        z=z_m, x=x_dm, y=y_dm,
        colorscale='Portland', name='路表高程', showscale=False,
        contours=dict(
            x=dict(show=show_grid, color=grid_color, width=1),
            y=dict(show=show_grid, color=grid_color, width=1)
        )
    ))

    # 2. 添加水膜（如果存在）
    if water_surf is not None and water_depth is not None:
        water_only = np.where(water_depth > 1e-4, water_surf, np.nan)
        if not np.all(np.isnan(water_only)):
            fig.add_trace(go.Surface(
                z=water_only, x=x_dm, y=y_dm,
                colorscale=[[0, 'aqua'], [1, 'aqua']], opacity=0.65,
                name='水膜', showscale=False, hoverinfo='skip'
            ))

    # 3. 相机视角和比例设置
    x_physical_length = x_dm[-1] - x_dm[0]
    y_physical_length = y_dm[-1] - y_dm[0]
    true_y_ratio = y_physical_length / x_physical_length if x_physical_length > 0 else 1

    fig.update_layout(
        template=template,
        scene=dict(
            aspectmode='manual', 
            aspectratio=dict(x=1, y=true_y_ratio, z=0.4),
            camera=dict(eye=dict(x=0.9, y=-0.9, z=0.9))
        ),
        margin=dict(l=0, r=0, b=0, t=30), height=420,
        font=dict(family="微软雅黑, Arial, sans-serif", size=15, color=font_color)
    )
    
    return fig
```

### 5.3 关键可视化技术详解

#### 技术1：透明水膜叠加
```python
# 水膜可视化的关键技巧
water_only = np.where(water_depth > 1e-4, water_surf, np.nan)
fig.add_trace(go.Surface(
    z=water_only,
    colorscale=[[0, 'aqua'], [1, 'aqua']],  # 单一颜色
    opacity=0.65,                           # 透明度
    hoverinfo='skip'                        # 禁用悬停信息
))
```

#### 技术2：动态网格线控制
```python
# 网格线的动态显示/隐藏
contours=dict(
    x=dict(show=show_grid, color=grid_color, width=1),
    y=dict(show=show_grid, color=grid_color, width=1)
)
```

#### 技术3：真实比例保持
```python
# 根据实际物理尺寸调整显示比例
true_y_ratio = y_physical_length / x_physical_length
aspectratio=dict(x=1, y=true_y_ratio, z=0.4)
```

### 5.4 实战练习：自定义3D可视化

#### 创建交互式地形浏览器
```python
# interactive_terrain_viewer.py
import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_interactive_terrain_viewer(matrix, dx_mm=100.0):
    """创建交互式地形查看器"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        colormap = st.selectbox("颜色方案", 
                               ["Portland", "Viridis", "Plasma", "Terrain"])
    
    with col2:
        show_water = st.checkbox("显示水膜", value=False)
        
    with col3:
        opacity = st.slider("水膜透明度", 0.1, 1.0, 0.65)
    
    # 创建3D图
    x = np.arange(matrix.shape[1]) * (dx_mm / 100.0)
    y = np.arange(matrix.shape[0]) * (dx_mm / 100.0)
    
    fig = go.Figure()
    fig.add_trace(go.Surface(z=matrix, x=x, y=y, colorscale=colormap))
    
    if show_water:
        # 模拟一些积水区域
        water_mask = matrix < np.percentile(matrix, 10)  # 最低10%区域
        water_surface = np.where(water_mask, matrix + 0.005, np.nan)
        fig.add_trace(go.Surface(z=water_surface, x=x, y=y, 
                                colorscale=[[0, 'blue'], [1, 'blue']], 
                                opacity=opacity))
    
    fig.update_layout(height=500, scene=dict(aspectmode='manual', 
                                           aspectratio=dict(x=1, y=2, z=0.3)))
    
    st.plotly_chart(fig, use_container_width=True)

# 使用示例（在Streamlit应用中）
# create_interactive_terrain_viewer(your_matrix_data)
```

---

## ⚡ 第四部分：性能优化实践（45分钟）

### 6.1 内存管理策略

#### 大矩阵处理的最佳实践
```python
# memory_optimization.py
import numpy as np

class MemoryEfficientProcessor:
    def __init__(self, max_memory_mb=1000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
    
    def estimate_memory_usage(self, array_shape, dtype=np.float64):
        """估算数组内存使用"""
        itemsize = np.dtype(dtype).itemsize
        return np.prod(array_shape) * itemsize
    
    def can_process_safely(self, input_shape, scale_factor):
        """检查是否可以安全处理"""
        output_shape = tuple(int(s * scale_factor) for s in input_shape)
        memory_needed = self.estimate_memory_usage(output_shape)
        return memory_needed < self.max_memory_bytes
    
    def process_in_chunks(self, data, scale_factor, chunk_size=1000):
        """分块处理大数据"""
        if self.can_process_safely(data.shape, scale_factor):
            # 直接处理
            from scipy.ndimage import zoom
            return zoom(data, scale_factor, order=3)
        else:
            # 分块处理
            chunks = []
            for i in range(0, data.shape[0], chunk_size):
                chunk = data[i:i+chunk_size, :]
                zoomed_chunk = zoom(chunk, scale_factor, order=3)
                chunks.append(zoomed_chunk)
            return np.vstack(chunks)
```

### 6.2 渲染性能优化

#### Plotly渲染优化技巧
```python
# plotly_optimization.py
def optimize_plotly_rendering(fig, max_points=100000):
    """优化Plotly渲染性能"""
    
    # 获取当前数据点数量
    total_points = 0
    for trace in fig.data:
        if hasattr(trace, 'z'):
            total_points += trace.z.size
    
    if total_points > max_points:
        # 降采样处理
        reduction_factor = int(np.sqrt(total_points / max_points))
        if reduction_factor > 1:
            for trace in fig.data:
                if hasattr(trace, 'z'):
                    trace.z = trace.z[::reduction_factor, ::reduction_factor]
                    if hasattr(trace, 'x'):
                        trace.x = trace.x[::reduction_factor]
                    if hasattr(trace, 'y'):
                        trace.y = trace.y[::reduction_factor]
    
    return fig
```

### 6.3 缓存机制实现

#### Streamlit缓存装饰器
```python
# caching_strategies.py
import streamlit as st
import numpy as np
from scipy.ndimage import zoom

@st.cache_data
def cached_super_resolution(matrix, scale_factor):
    """缓存超分辨率结果"""
    return zoom(matrix, scale_factor, order=3)

@st.cache_data
def cached_3d_visualization(matrix, water_surf, water_depth, dx_mm, show_grid):
    """缓存3D可视化结果（返回Plotly figure的JSON）"""
    # 这里需要将figure转换为可缓存的格式
    # 实际项目中可能需要更复杂的缓存策略
    pass

# 在app.py中的实际应用
def get_fine_matrix(matrix_crop, scale_factor=2):
    """获取超分辨率矩阵（带缓存）"""
    return cached_super_resolution(matrix_crop, scale_factor)
```

### 6.4 实战性能测试

#### 创建性能基准测试
```python
# performance_benchmark.py
import time
import psutil
import numpy as np
from scipy.ndimage import zoom

def benchmark_super_resolution():
    """超分辨率性能基准测试"""
    
    test_sizes = [(100, 50), (500, 250), (1000, 500), (2000, 1000)]
    scale_factors = [2, 3, 4]
    
    results = []
    
    for size in test_sizes:
        for scale in scale_factors:
            # 创建测试数据
            test_data = np.random.rand(*size).astype(np.float32)
            
            # 测量内存使用
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 测量时间
            start_time = time.time()
            result = zoom(test_data, scale, order=3)
            end_time = time.time()
            
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            
            results.append({
                'input_size': size,
                'scale_factor': scale,
                'output_size': result.shape,
                'processing_time': end_time - start_time,
                'memory_usage_mb': mem_after - mem_before,
                'memory_peak_mb': mem_after
            })
            
            print(f"Size {size} × {scale} → {result.shape}: "
                  f"{end_time-start_time:.3f}s, {mem_after-mem_before:.1f}MB")
    
    return results
```

---

## 📝 第五部分：课后作业与实践

### 7.1 基础作业

#### 作业1：插值方法实验
- [ ] 实现不同order值的插值效果对比
- [ ] 测试不同边界处理模式的影响
- [ ] 记录各种方法的处理时间和内存使用

#### 作业2：3D可视化定制
- [ ] 修改颜色方案和透明度参数
- [ ] 添加自定义相机视角控制
- [ ] 实现网格线开关功能

### 7.2 进阶作业

#### 作业3：性能优化实现
- [ ] 实现分块处理大数据的函数
- [ ] 添加内存使用监控和警告
- [ ] 测试不同数据规模下的性能表现

#### 作业4：交互式地形浏览器
- [ ] 创建完整的Streamlit交互界面
- [ ] 支持多种可视化选项
- [ ] 添加性能指标显示

### 7.3 思考题

1. **插值选择**：在什么情况下应该选择低阶插值而不是高阶插值？

2. **内存权衡**：如何在内存使用和计算精度之间找到最佳平衡点？

3. **可视化设计**：3D地形可视化中，哪些元素对工程决策最有帮助？

4. **扩展应用**：这套3D重构技术如何应用到其他领域（如医学影像、地质勘探）？

---

## 🔍 第六部分：常见问题FAQ

### Q1：超分辨率后出现奇怪的伪影怎么办？
**解决方案**：
- 检查原始数据是否有异常值（先进行预处理）
- 尝试降低插值阶数（order=1或2）
- 启用预滤波（prefilter=True，默认已启用）
- 考虑添加后处理平滑

### Q2：3D图渲染很慢怎么办？
**解决方案**：
```python
# 1. 降采样显示
if matrix.shape[0] * matrix.shape[1] > 100000:
    display_matrix = matrix[::2, ::2]  # 降采样
else:
    display_matrix = matrix

# 2. 简化图形属性
fig.update_layout(
    scene=dict(
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        zaxis=dict(showticklabels=False)
    )
)
```

### Q3：如何处理超大矩阵（>1GB）？
**解决方案**：
- 使用内存映射文件（numpy.memmap）
- 实现分块处理和流式处理
- 考虑使用Dask等分布式计算库
- 优化数据类型（float32代替float64）

---

## 📚 第七部分：延伸学习资源

### 推荐文档
- [Plotly 3D Charts](https://plotly.com/python/3d-charts/) - 官方3D图表文档
- [SciPy ndimage Documentation](https://docs.scipy.org/doc/scipy/reference/ndimage.html) - 图像处理函数
- [NumPy Memory Layout](https://numpy.org/doc/stable/user/basics.indexing.html) - 内存布局优化

### 相关技术
- **WebGL可视化**：Three.js, CesiumJS（用于更大规模3D数据）
- **GPU加速**：CuPy, PyTorch（用于大规模数值计算）
- **地理信息系统**：GDAL, rasterio（用于地理空间数据）

### 下节课预告
**第4课：流体力学基础与水膜推演算法**
- 填洼算法（Depression Filling）原理
- 局部最小值检测技术
- 水体填充和溢出模拟
- 数值稳定性控制

---

> **学习提示**：3D可视化不仅是展示工具，更是理解数据和验证算法的重要手段。花时间优化可视化效果，将大大提升您的数据分析效率。

**祝您学习愉快！** 🚀

---
*第三课内容最后更新：2026年5月19日*