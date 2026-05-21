# 🌧️ 高速公路路面积水智能识别系统 - 10节课课程大纲

> **课程目标**：通过10节课的系统学习，掌握从零开始构建智能道路水坑检测系统的完整技术栈，包括数据处理、物理模拟、风险评估和智能决策等核心技术。

---

## 📚 课程总体安排

| 课次 | 主题 | 核心技术点 | 实践项目 |
|------|------|------------|----------|
| 第1课 | 项目概览与环境搭建 | Streamlit, Plotly, 项目架构 | 运行示例系统 |
| 第2课 | 点云数据处理基础 | HDF5, NumPy, 数据预处理 | 数据格式转换工具 |
| 第3课 | 3D地形重构技术 | 插值算法, 异常值处理, 可视化 | 3D路表重建器 |
| 第4课 | 流体力学基础 | 填洼算法, 物理约束建模 | 水膜推演引擎V1 |
| 第5课 | 高级水膜模拟 | 迭代优化, 数值稳定性 | 水膜推演引擎V2 |
| 第6课 | 车辆动力学基础 | 江守一郎公式, 临界速度计算 | 滑水风险计算器 |
| 第7课 | 概率统计应用 | 正态分布, 生存函数, 风险分级 | 全域风险评估系统 |
| 第8课 | 计算机视觉基础 | 连通域算法, 形态学处理 | 病害区域识别器 |
| 第9课 | 智能决策系统 | 成本效益分析, 工艺匹配 | 处治方案生成器 |
| 第10课 | 系统集成与优化 | 性能调优, 用户体验, 部署 | 完整系统交付 |

---

## 📖 详细课程内容介绍

### 第1课：项目概览与开发环境搭建
**学习目标**：理解项目整体架构，搭建开发环境，运行示例系统

**理论内容**：
- 项目背景与业务价值
- 四大核心功能模块介绍
- 技术栈概览（Python生态）
- Streamlit Web框架基础

**实践内容**：
```python
# 环境搭建
pip install streamlit plotly scipy numpy h5py pandas

# 运行系统
streamlit run app.py

# 探索界面组件
st.title(), st.sidebar, st.plotly_chart()
```

**课后作业**：
- 成功运行项目并加载内置示例数据
- 修改界面标题和颜色主题

---

### 第2课：点云数据处理与HDF5格式
**学习目标**：掌握点云数据的存储、读取和预处理技术

**理论内容**：
- 点云数据特点与应用场景
- HDF5文件格式优势（压缩、分层、高效）
- MATLAB到Python的数据迁移
- 数据质量评估指标

**实践内容**：
```python
# HDF5文件操作
import h5py
with h5py.File('data.h5', 'w') as f:
    group = f.create_group('road_segments')
    group.create_dataset('segment_001', data=matrix)

# 数据转换脚本开发
def convert_mat_to_h5(src_folder, output_file):
    # 实现.mat到.h5的批量转换
    pass
```

**课后作业**：
- 使用`assets/data_convert_to_h5.py`转换自己的数据
- 添加数据质量检查功能

---

### 第3课：3D地形重构与可视化
**学习目标**：实现高精度3D路表重构和交互式可视化

**理论内容**：
- 插值算法原理（线性、三次样条）
- 异常值检测（3σ原则）
- 多路段拼接技术
- Plotly 3D可视化配置

**实践内容**：
```python
# 超分辨率插值
from scipy.ndimage import zoom
fine_matrix = zoom(coarse_matrix, scale_factor, order=3)

# 3D可视化
fig = go.Figure()
fig.add_trace(go.Surface(z=matrix, colorscale='Portland'))

# 异常值修复
median_filtered = median_filter(data, size=5)
outlier_mask = np.abs(data - median_filtered) > threshold
```

**课后作业**：
- 实现不同插值算法的对比
- 添加地形剖面图功能

---

### 第4课：流体力学基础 - 水膜推演算法
**学习目标**：理解并实现基础的填洼算法

**理论内容**：
- 表面水流基本原理
- 局部最小值检测（8邻域）
- 水体填充策略
- 边缘约束处理

**实践内容**：
```python
# 局部最小值检测
is_min_center = (center <= neighbors).all(axis=-1)

# 基础水膜填充
def basic_water_filling(elevation_matrix, water_volume):
    # 实现简单的填洼逻辑
    pass

# 连通域标记
from scipy.ndimage import label
labeled_array, num_features = label(minima_mask)
```

**课后作业**：
- 实现静态水膜填充（单次迭代）
- 可视化不同填充阶段的结果

---

### 第5课：高级水膜模拟与数值优化
**学习目标**：掌握完整的动态水膜推演引擎

**理论内容**：
- 迭代收敛条件设计
- 数值稳定性控制（最大步长）
- 径流系数物理意义
- 动态降雨过程模拟

**实践内容**：
```python
# 完整的水膜推演引擎
def simulate_water_film_with_low_wall(
    data0, shuimo_h, wall_margin, max_h_step
):
    # 实现完整的迭代算法
    # 包含溢出处理、连通域更新等
    pass

# 动态模拟控制
for step in range(anim_frames):
    current_rain = total_rain * (step / anim_frames)
    # 执行单步推演
```

**课后作业**：
- 优化算法性能（减少迭代次数）
- 添加不同的降雨模式（阵雨、持续雨）

---

### 第6课：车辆动力学与滑水风险基础
**学习目标**：理解车辆滑水的物理机制和临界条件

**理论内容**：
- 江守一郎滑水公式推导
- 轮胎-路面-水膜相互作用
- 临界滑水速度计算
- 车速分布统计特性

**实践内容**：
```python
# 临界速度计算
vc_matrix = 145.0 * (water_depth_mm ** -0.4)

# 车速分布建模
from scipy.stats import norm
mu_v, sigma_v = 75.3, 5.7  # 实测参数

# 风险初步评估
risk_indicator = vehicle_speed > critical_speed
```

**课后作业**：
- 实现不同车型的滑水风险计算
- 添加路面摩擦系数的影响

---

### 第7课：概率统计在风险评估中的应用
**学习目标**：掌握基于概率的风险量化评估方法

**理论内容**：
- 正态分布的概率密度函数
- 生存函数(Survival Function)应用
- 对数尺度风险分级
- 面域风险聚合统计

**实践内容**：
```python
# 滑水概率计算
prob_matrix = norm.sf(vc_matrix, loc=mu_v, scale=sigma_v)

# 风险等级划分
risk_level_matrix = np.full_like(prob_matrix, 'E')
risk_level_matrix[prob_matrix >= 1e-1] = 'A'  # 高风险
risk_level_matrix[(prob_matrix >= 1e-3) & (prob_matrix < 1e-1)] = 'B'

# 动态决策逻辑
high_risk_ratio = high_risk_pixels / total_pixels
if high_risk_ratio > 0.05:
    status = "危险"
```

**课后作业**：
- 实现自定义风险阈值配置
- 添加时间维度的风险演化分析

---

### 第8课：计算机视觉在工程检测中的应用
**学习目标**：掌握连通域算法在病害识别中的应用

**理论内容**：
- 二值图像连通域分析
- 形态学处理基础
- 区域特征提取（面积、深度、形状）
- 噪声过滤策略

**实践内容**：
```python
# 连通域标记
from scipy.ndimage import label, find_objects
high_risk_mask = risk_score_matrix >= 4
labeled_array, num_features = label(high_risk_mask, structure=np.ones((3,3)))

# 区域特征提取
objects = find_objects(labeled_array)
for i, obj in enumerate(objects):
    region_mask = (labeled_array == (i + 1))
    area = np.sum(region_mask) * pixel_area
    depths = depth_matrix[region_mask]
    
# 噪声过滤
if phys_area < 0.2:  # 小于0.2㎡忽略
    continue
```

**课后作业**：
- 实现不同结构元素的连通性比较
- 添加区域形状特征分析

---

### 第9课：智能决策与成本效益分析
**学习目标**：构建完整的工程处治决策系统

**理论内容**：
- 工艺-深度匹配规则
- 成本核算模型
- 传统vs智能方案对比
- 经济效益量化

**实践内容**：
```python
# 处治工艺匹配
if max_depth < 3.0:
    tech = "浅层靶向微创刻槽"
    unit_price = 18.0  # 元/m²
elif max_depth < 8.0:
    tech = "中深层自动刻槽"  
    unit_price = 18.0
else:
    tech = "深水区复合处治"
    unit_price = 18.0 + 120.0 * 0.3

# 成本计算
smart_cost = treat_area * unit_price
trad_cost = full_lane_area * 90.0  # 传统铣刨单价
saving_ratio = (trad_cost - smart_cost) / trad_cost * 100
```

**课后作业**：
- 实现多工艺组合优化
- 添加不同地区的人工成本差异

---

### 第10课：系统集成、优化与部署
**学习目标**：完成完整的系统交付和性能优化

**理论内容**：
- Streamlit状态管理最佳实践
- 性能瓶颈分析与优化
- 用户体验设计原则
- 系统部署与维护

**实践内容**：
```python
# 性能优化
# 1. 缓存重复计算结果
@st.cache_data
def expensive_computation(data):
    return result

# 2. 内存管理
del unused_variables
gc.collect()

# 3. 并行计算（可选）
from concurrent.futures import ThreadPoolExecutor

# 系统部署
# Docker容器化
# 云服务器部署
# API接口开发
```

**最终项目**：
- 集成所有模块的完整系统
- 添加用户友好的报告生成功能
- 实现一键导出审计报告

---

## 🎯 课程学习成果

完成本课程后，您将能够：

### 技术能力
- ✅ 熟练使用Python科学计算栈（NumPy, SciPy, Pandas）
- ✅ 掌握Streamlit Web应用开发
- ✅ 理解流体力学基础算法实现
- ✅ 应用概率统计进行风险评估
- ✅ 运用计算机视觉解决工程问题

### 工程思维
- ✅ 将理论算法转化为实际工程解决方案
- ✅ 进行成本效益分析和方案比选
- ✅ 设计用户友好的交互界面
- ✅ 考虑系统性能和可维护性

### 职业发展
- ✅ 具备智能交通系统开发能力
- ✅ 能够承担基础设施智能化项目
- ✅ 掌握产学研结合的项目方法论

---

## 📚 推荐学习资源

### 必备工具文档
- [Streamlit官方文档](https://docs.streamlit.io/)
- [Plotly Python文档](https://plotly.com/python/)
- [SciPy用户指南](https://docs.scipy.org/doc/scipy/reference/)
- [HDF5 for Python](https://docs.h5py.org/)

### 理论参考书籍
- 《Python数据科学手册》- Jake VanderPlas
- 《计算流体力学基础》- John D. Anderson
- 《计算机视觉：算法与应用》- Richard Szeliski
- 《概率论与数理统计》- 盛骤

### 在线学习平台
- Coursera: Python for Data Science
- edX: Computational Fluid Dynamics
- Udacity: Computer Vision Nanodegree

---

> **学习建议**：每节课都要动手实践，不要只看不练。遇到问题时，先尝试自己解决，再查阅文档或寻求帮助。记住，真正的技能来自于反复的实践和调试！

**祝您学习顺利！** 🚀

*课程大纲最后更新：2026年5月19日*