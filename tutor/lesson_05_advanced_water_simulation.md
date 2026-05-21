# 🌧️ 第5课：高级水膜模拟与数值优化

> **课时**：3小时  
> **学习目标**：掌握动态降雨模拟、数值稳定性控制和算法性能优化技术  
> **先修要求**：完成第4课，理解基础填洼算法原理

---

## 📚 课程内容概览

### 本课学习路线
1. **动态降雨过程模拟**（60分钟）- 实现分步降雨推演动画
2. **数值稳定性控制**（60分钟）- 最大步长控制和收敛条件设计  
3. **算法性能优化**（45分钟）- 内存管理和计算效率提升
4. **工程参数调优**（15分钟）- 径流系数和物理参数优化

---

## 🌧️ 第一部分：动态降雨过程模拟（60分钟）

### 5.1 动态模拟的必要性

#### 为什么需要动态模拟？
静态填洼算法只能给出最终的积水状态，但实际工程中需要了解：
- **积水形成过程**：不同降雨量下的积水演化
- **临界点识别**：何时开始出现大面积积水
- **风险预警**：基于降雨强度的风险评估
- **可视化展示**：直观展示给用户看的过程动画

#### 项目中的动态模拟实现
```python
# app.py 中的动态模拟关键代码
anim_frames = st.slider("仿真动画帧数", 1, 10, 5)
target_rainfall = st.slider("目标总降雨量 (mm)", 0.0, 50.0, 10.0, step=0.5)

for step in range(1, anim_frames + 1):
    current_rain = target_rainfall * (step / anim_frames)
    effective_rain_m = (current_rain * runoff_coefficient) / 1000.0
    
    surf_crop, depth_crop = simulate_water_film_with_low_wall(
        fine_matrix_crop, effective_rain_m, wall_margin / 1000.0, max_h_step / 1000.0
    )
    
    # 更新UI显示
    plot3d_container.plotly_chart(create_3d_figure(...))
    metrics_container.container().markdown(render_metrics(...))
```

### 5.2 降雨模式设计

#### 线性降雨模式
```python
def linear_rainfall_pattern(total_rainfall, num_frames):
    """线性降雨：均匀分配到每个时间步"""
    return [total_rainfall * (i / num_frames) for i in range(1, num_frames + 1)]

# 示例：10mm总降雨量，5帧
rainfall_sequence = linear_rainfall_pattern(10.0, 5)
# 结果: [2.0, 4.0, 6.0, 8.0, 10.0]
```

#### 非线性降雨模式
```python
def exponential_rainfall_pattern(total_rainfall, num_frames, intensity=1.0):
    """指数降雨：前期慢，后期快"""
    base_sequence = np.linspace(0, 1, num_frames + 1)[1:]
    normalized = (np.exp(intensity * base_sequence) - 1) / (np.exp(intensity) - 1)
    return total_rainfall * normalized

def gaussian_rainfall_pattern(total_rainfall, num_frames, peak_frame=None):
    """高斯降雨：中间强，两头弱"""
    if peak_frame is None:
        peak_frame = num_frames // 2
    
    frames = np.arange(num_frames)
    gaussian_curve = np.exp(-0.5 * ((frames - peak_frame) / (num_frames/4))**2)
    normalized = np.cumsum(gaussian_curve) / np.sum(gaussian_curve)
    return total_rainfall * normalized
```

### 5.3 径流系数模型

#### 径流系数的物理意义
径流系数（Runoff Coefficient）表示降雨中形成地表径流的比例：
- **沥青路面**：0.85-0.95（几乎不渗透）
- **水泥路面**：0.80-0.90
- **透水路面**：0.10-0.30
- **草地**：0.05-0.20

#### 项目中的径流系数应用
```python
# app.py 中的径流系数处理
runoff_coefficient = st.slider("路面径流滞留系数", 0.01, 1.00, 0.01, step=0.01)
effective_rain_m = (current_rain * runoff_coefficient) / 1000.0
```

#### 动态径流系数模型
```python
def dynamic_runoff_coefficient(water_depth, base_coefficient=0.9):
    """
    动态径流系数：随着积水深度增加，径流系数可能变化
    """
    # 简单模型：积水越深，径流系数越高（水流更容易汇集）
    depth_factor = np.minimum(water_depth / 0.01, 1.0)  # 10mm为参考深度
    return base_coefficient * (1 + 0.1 * depth_factor)

def advanced_water_simulation(elevation_matrix, rainfall_sequence, 
                           base_runoff=0.9, dynamic_runoff=True):
    """
    高级水膜模拟：支持动态径流系数
    """
    results = []
    current_water_surface = elevation_matrix.copy()
    
    for i, rainfall in enumerate(rainfall_sequence):
        if dynamic_runoff:
            # 基于当前积水深度计算径流系数
            current_depth = current_water_surface - elevation_matrix
            runoff_coeff = dynamic_runoff_coefficient(current_depth, base_runoff)
        else:
            runoff_coeff = base_runoff
            
        effective_rain = rainfall * runoff_coeff / 1000.0
        
        # 执行填洼算法
        new_surface, new_depth = simulate_water_film_with_low_wall(
            elevation_matrix, effective_rain, wall_margin=0.001
        )
        
        results.append({
            'step': i + 1,
            'rainfall_mm': rainfall,
            'runoff_coeff': runoff_coeff,
            'water_surface': new_surface,
            'water_depth': new_depth
        })
        
        current_water_surface = new_surface
    
    return results
```

### 5.4 实战练习：自定义降雨模式

#### 创建交互式降雨模拟器
```python
# interactive_rainfall_simulator.py
import streamlit as st
import numpy as np

def create_rainfall_pattern_selector():
    """创建降雨模式选择器"""
    pattern_type = st.selectbox("降雨模式", ["线性", "指数增长", "高斯分布", "自定义"])
    
    if pattern_type == "线性":
        return linear_rainfall_pattern
    
    elif pattern_type == "指数增长":
        intensity = st.slider("降雨强度", 0.1, 3.0, 1.0)
        return lambda total, frames: exponential_rainfall_pattern(total, frames, intensity)
    
    elif pattern_type == "高斯分布":
        peak_ratio = st.slider("峰值位置", 0.1, 0.9, 0.5)
        return lambda total, frames: gaussian_rainfall_pattern(
            total, frames, int(frames * peak_ratio)
        )
    
    else:  # 自定义
        st.write("请输入每个时间步的降雨量（mm）:")
        custom_values = []
        for i in range(5):
            val = st.number_input(f"步骤 {i+1}", 0.0, 50.0, 2.0)
            custom_values.append(val)
        return lambda total, frames: np.array(custom_values[:frames])

# 使用示例
pattern_func = create_rainfall_pattern_selector()
rainfall_sequence = pattern_func(20.0, 5)  # 20mm总降雨，5个步骤
```

---

## ⚖️ 第二部分：数值稳定性控制（60分钟）

### 6.1 数值不稳定性的来源

#### 主要问题
1. **大步长导致振荡**：水位更新步长过大，导致数值振荡
2. **浮点精度误差**：多次迭代累积的浮点误差
3. **地形噪声干扰**：微小的地形起伏导致虚假洼地
4. **收敛条件不当**：过早或过晚停止迭代

#### 项目中的稳定性保障
```python
# app.py 中的关键稳定性参数
max_h_step = st.slider("最大水位爬升步长(mm)", 0.000, 0.100, 0.010, step=0.002, format="%.3f")

# 在simulate_water_film_with_low_wall函数中
h_dist = min(max_h_step, theoretical_h_dist)
```

### 6.2 最大步长控制策略

#### 自适应步长算法
```python
def adaptive_step_size_control(current_water_volume, num_minima, 
                            base_max_step=0.0001, min_step=1e-8):
    """
    自适应步长控制：根据当前状态动态调整步长
    """
    theoretical_step = current_water_volume / num_minima if num_minima > 0 else 0
    
    # 步长限制：不能超过基础最大步长，也不能小于最小步长
    adaptive_step = min(base_max_step, max(min_step, theoretical_step))
    
    # 额外的安全限制：避免极端情况
    if theoretical_step > base_max_step * 10:
        # 如果理论步长远大于限制，说明可能有数值问题
        adaptive_step = base_max_step * 0.5
    
    return adaptive_step
```

#### 多尺度步长控制
```python
def multi_scale_step_control(iteration_count, base_step=0.0001):
    """
    多尺度步长：早期用大步长快速收敛，后期用小步长精细调整
    """
    if iteration_count < 100:
        return base_step * 2.0  # 快速阶段
    elif iteration_count < 500:
        return base_step         # 正常阶段  
    else:
        return base_step * 0.5   # 精细阶段
```

### 6.3 收敛条件设计

#### 多重收敛判断
```python
def check_convergence_criteria(water_surface_old, water_surface_new, 
                            remaining_water, iteration_count,
                            tolerance=1e-6, max_iterations=5000):
    """
    多重收敛条件判断
    """
    # 条件1：剩余水量足够小
    if remaining_water < tolerance:
        return True, "水量耗尽"
    
    # 条件2：水位变化足够小
    surface_diff = np.max(np.abs(water_surface_new - water_surface_old))
    if surface_diff < tolerance:
        return True, "水位稳定"
    
    # 条件3：达到最大迭代次数
    if iteration_count >= max_iterations:
        return True, "达到最大迭代次数"
    
    # 条件4：没有找到新的洼地
    if not np.any(find_local_minima_8neighbor(water_surface_new)):
        return True, "无洼地可填充"
    
    return False, "继续迭代"
```

### 6.4 浮点精度处理

#### 数值稳定性技巧
```python
def numerically_stable_operations(matrix):
    """数值稳定的矩阵操作"""
    
    # 1. 避免极小值（可能导致除零错误）
    matrix = np.maximum(matrix, 1e-12)
    
    # 2. 使用相对容差比较
    def is_close(a, b, rtol=1e-5, atol=1e-8):
        return np.abs(a - b) <= (atol + rtol * np.abs(b))
    
    # 3. 累积和的稳定性（Kahan求和算法）
    def kahan_sum(arr):
        sum_val = 0.0
        c = 0.0  # 补偿项
        for x in arr.flat:
            y = x - c
            t = sum_val + y
            c = (t - sum_val) - y
            sum_val = t
        return sum_val
    
    return matrix
```

### 6.5 实战练习：稳定性测试

#### 创建稳定性基准测试
```python
# stability_benchmark.py
import time
import numpy as np

def benchmark_stability_parameters():
    """测试不同稳定性参数的效果"""
    
    test_terrain = create_complex_test_terrain()
    total_water = 50.0  # 大水量测试稳定性
    
    max_steps = [0.0001, 0.0005, 0.001, 0.005, 0.01]
    results = []
    
    for max_step in max_steps:
        start_time = time.time()
        try:
            surface, depth, iterations = simulate_water_film_with_low_wall(
                test_terrain, total_water, max_h_step=max_step
            )
            end_time = time.time()
            
            # 检查结果合理性
            max_depth = np.max(depth)
            is_reasonable = max_depth < 10.0  # 积水深度不应超过10米
            
            results.append({
                'max_step': max_step,
                'iterations': iterations,
                'time': end_time - start_time,
                'max_depth': max_depth,
                'stable': is_reasonable,
                'converged': iterations < 5000
            })
            
        except Exception as e:
            results.append({
                'max_step': max_step,
                'error': str(e),
                'stable': False
            })
    
    return results
```

---

## ⚡ 第三部分：算法性能优化（45分钟）

### 7.1 内存优化策略

#### 原地操作优化
```python
def memory_efficient_simulation(elevation_matrix, total_water_volume):
    """内存高效的模拟实现"""
    
    # 避免创建不必要的副本
    water_surface = elevation_matrix.copy()  # 只需要一个工作副本
    
    # 重用临时数组
    temp_array = np.empty_like(water_surface)
    
    iteration = 0
    while total_water_volume > 1e-6 and iteration < 1000:
        # 局部最小值检测（重用temp_array）
        is_min = find_local_minima_inplace(water_surface, temp_array)
        
        if not np.any(is_min):
            break
            
        # 水位更新（原地操作）
        num_minima = np.sum(is_min)
        water_per_cell = total_water_volume / num_minima
        water_surface[is_min] += water_per_cell
        total_water_volume = 0
        
        iteration += 1
    
    return water_surface
```

#### 分块处理大型地形
```python
def process_large_terrain_in_chunks(large_terrain, total_water, chunk_size=1000):
    """分块处理大型地形"""
    
    rows, cols = large_terrain.shape
    results = []
    
    # 计算每个块分配的水量（按面积比例）
    total_area = rows * cols
    water_per_chunk = {}
    
    for i in range(0, rows, chunk_size):
        for j in range(0, cols, chunk_size):
            chunk_rows = min(chunk_size, rows - i)
            chunk_cols = min(chunk_size, cols - j)
            chunk_area = chunk_rows * chunk_cols
            water_per_chunk[(i, j)] = total_water * (chunk_area / total_area)
    
    # 处理每个块
    for (i, j), chunk_water in water_per_chunk.items():
        chunk = large_terrain[i:i+chunk_size, j:j+chunk_size]
        chunk_result = simulate_water_film_with_low_wall(
            chunk, chunk_water, wall_margin=0.001
        )
        results.append(((i, j), chunk_result))
    
    return results
```

### 7.2 计算效率优化

#### 向量化操作
```python
# 优化前：使用循环
def slow_local_minima_detection(matrix):
    result = np.zeros_like(matrix, dtype=bool)
    for i in range(1, matrix.shape[0]-1):
        for j in range(1, matrix.shape[1]-1):
            center = matrix[i, j]
            neighbors = matrix[i-1:i+2, j-1:j+2].flatten()
            neighbors = np.delete(neighbors, 4)  # 移除中心点
            if np.all(center <= neighbors):
                result[i, j] = True
    return result

# 优化后：完全向量化
def fast_local_minima_detection(matrix):
    padded = np.pad(matrix, 1, constant_values=np.inf)
    center = padded[1:-1, 1:-1]
    is_min = np.ones_like(center, dtype=bool)
    
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            neighbor = padded[1+di:-1+di or None, 1+dj:-1+dj or None]
            is_min &= (center <= neighbor)
    
    return is_min
```

#### 缓存和预计算
```python
@st.cache_data
def cached_water_simulation(elevation_hash, total_water, wall_margin, max_step):
    """缓存水膜模拟结果"""
    # 注意：需要将矩阵转换为可哈希的形式
    return simulate_water_film_with_low_wall(
        elevation_hash, total_water, wall_margin, max_step
    )

# 在app.py中的实际应用
elevation_hash = hash(elevation_matrix.tobytes())
result = cached_water_simulation(elevation_hash, water_volume, wall_margin, max_step)
```

### 7.3 并行化处理

#### 多进程并行
```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

def parallel_rainfall_simulation(elevation_matrix, rainfall_sequences):
    """并行处理多个降雨场景"""
    
    def simulate_single_sequence(args):
        rainfall_seq, idx = args
        results = []
        for rainfall in rainfall_seq:
            surface, depth = simulate_water_film_with_low_wall(
                elevation_matrix, rainfall / 1000.0
            )
            results.append((rainfall, surface, depth))
        return idx, results
    
    # 准备参数
    tasks = [(seq, i) for i, seq in enumerate(rainfall_sequences)]
    
    # 并行执行
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        results = list(executor.map(simulate_single_sequence, tasks))
    
    # 整理结果
    results.sort(key=lambda x: x[0])  # 按索引排序
    return [r[1] for r in results]
```

---

## 🔧 第四部分：工程参数调优（15分钟）

### 8.1 参数敏感性分析

#### 关键参数影响矩阵
| 参数 | 影响 | 推荐范围 | 调优策略 |
|------|------|----------|----------|
| **挡水墙高度** | 积水范围 | 0.5-2.0mm | 根据路缘石高度设置 |
| **最大步长** | 收敛速度 | 0.01-0.1mm | 平衡精度和速度 |
| **径流系数** | 积水量 | 0.01-1.0 | 根据路面类型设置 |
| **动画帧数** | 可视化效果 | 3-10帧 | 根据计算资源调整 |

### 8.2 自动参数调优

#### 基于性能目标的调优
```python
def auto_tune_parameters(elevation_matrix, target_max_time=5.0, target_accuracy=0.95):
    """自动调优参数以平衡性能和精度"""
    
    # 基准测试：使用保守参数
    baseline_result = simulate_water_film_with_low_wall(
        elevation_matrix, 10.0, wall_margin=0.002, max_h_step=0.0001
    )
    
    # 测试不同参数组合
    best_params = {'wall_margin': 0.002, 'max_h_step': 0.0001}
    best_score = float('inf')
    
    for wall_margin in [0.001, 0.002, 0.005]:
        for max_step in [0.0001, 0.0005, 0.001, 0.002]:
            start_time = time.time()
            test_result = simulate_water_film_with_low_wall(
                elevation_matrix, 10.0, wall_margin=wall_margin, max_h_step=max_step
            )
            elapsed_time = time.time() - start_time
            
            # 计算精度损失
            accuracy_loss = np.mean(np.abs(test_result[1] - baseline_result[1]))
            
            # 综合评分（时间权重 + 精度权重）
            if elapsed_time <= target_max_time:
                score = elapsed_time + 1000 * accuracy_loss
                if score < best_score:
                    best_score = score
                    best_params = {'wall_margin': wall_margin, 'max_h_step': max_step}
    
    return best_params
```

### 8.3 用户自定义配置

#### 配置文件支持
```python
# config.yaml
simulation:
  default_wall_margin: 0.001
  default_max_step: 0.0001
  default_runoff_coefficient: 0.9
  max_animation_frames: 10
  
performance:
  auto_tune: true
  target_max_time: 5.0
  cache_results: true

# 加载配置
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

---

## 📝 第五部分：课后作业与实践

### 9.1 基础作业

#### 作业1：动态降雨模式实现
- [ ] 实现至少3种不同的降雨模式
- [ ] 测试不同模式对积水形成过程的影响
- [ ] 可视化不同降雨模式的结果对比

#### 作业2：数值稳定性测试
- [ ] 测试不同最大步长参数的稳定性
- [ ] 分析收敛条件对结果的影响
- [ ] 记录数值不稳定的情况和解决方案

### 9.2 进阶作业

#### 作业3：性能优化实现
- [ ] 实现内存高效的水膜模拟算法
- [ ] 测试分块处理大型地形的效果
- [ ] 比较向量化和循环实现的性能差异

#### 作业4：自动参数调优系统
- [ ] 实现基于性能目标的自动调优
- [ ] 添加用户配置文件支持
- [ ] 测试不同硬件配置下的最优参数

### 9.3 思考题

1. **算法设计**：如何在保证数值稳定性的同时最大化计算效率？

2. **物理建模**：除了径流系数，还有哪些物理参数可以动态调整？

3. **工程应用**：在实时系统中，如何平衡模拟精度和响应时间？

4. **扩展思考**：这套数值优化技术如何应用到其他物理模拟场景？

---

## 🔍 第六部分：常见问题FAQ

### Q1：模拟结果出现不合理的超深积水怎么办？
**解决方案**：
- 检查地形数据是否有异常值（先进行预处理）
- 降低最大步长参数
- 增加边缘挡水墙高度
- 添加积水深度上限检查

### Q2：算法收敛太慢怎么办？
**解决方案**：
```python
# 1. 使用自适应步长
max_h_step = min(0.01, theoretical_step * 2)

# 2. 添加地形预处理
elevation_smooth = gaussian_filter(elevation_matrix, sigma=1.0)

# 3. 降低精度要求（如果可接受）
tolerance = 1e-5  # 而不是1e-6
```

### Q3：内存不足处理大型地形怎么办？
**解决方案**：
- 实现分块处理算法
- 使用内存映射文件（numpy.memmap）
- 降低地形分辨率（先降采样再插值回原分辨率）
- 考虑使用GPU加速（CuPy库）

---

## 📚 第七部分：延伸学习资源

### 推荐文献
- **"Numerical Recipes: The Art of Scientific Computing"** - Press et al.
- **"Computational Fluid Dynamics: Principles and Applications"** - Blazek
- **"Stability and Convergence of Iterative Methods"** - numerical analysis papers

### 相关技术
- **GPU加速计算**：CuPy, PyTorch, TensorFlow
- **高性能计算**：Dask, Ray, MPI for Python
- **数值分析库**：SciPy.optimize, NumPy.linalg
- **可视化优化**：Plotly Dash, Bokeh

### 下节课预告
**第6课：车辆动力学与滑水风险基础**
- 江守一郎滑水公式推导
- 临界滑水速度计算
- 车速分布统计建模
- 风险初步评估方法

---

> **学习提示**：数值稳定性是科学计算的核心，花时间理解各种稳定性控制技术。建议多做实验，观察不同参数组合的效果。

**祝您学习愉快！** 🚀

---
*第五课内容最后更新：2026年5月19日*