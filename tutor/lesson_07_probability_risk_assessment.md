# 🌧️ 第7课：概率统计在风险评估中的应用

> **课时**：2.5小时  
> **学习目标**：掌握基于概率的风险量化评估方法，理解对数尺度风险分级和动态决策逻辑  
> **先修要求**：完成第1-6课，理解车辆动力学和江守一郎公式

---

## 📚 课程内容概览

### 本课学习路线
1. **概率统计基础回顾**（30分钟）- 正态分布、生存函数和对数尺度
2. **多级风险等级划分**（60分钟）- 对数尺度风险分级实现  
3. **面域风险聚合统计**（45分钟）- 区域风险汇总和统计分析
4. **动态决策逻辑实现**（15分钟）- 基于风险比例的智能决策

---

## 📈 第一部分：概率统计基础回顾（30分钟）

### 7.1 正态分布与交通安全

#### 车速分布的正态性假设
在高速公路交通流中，车速通常呈现正态分布特征：
- **均值(μ)**：代表平均行驶速度
- **标准差(σ)**：代表速度离散程度
- **68-95-99.7规则**：约68%的车辆速度在μ±σ范围内

#### 项目中的参数选择
```python
# modules/risk_assessment.py 中的车速参数
mu_v = 75.3  # 平均车速 km/h (限速80km/h路段)
sigma_v = 5.7  # 车速标准差 km/h
```

这些参数基于实际交通观测数据，具有良好的代表性。

### 7.2 生存函数(Survival Function)的应用

#### 数学定义
生存函数SF(x)表示随机变量X大于x的概率：
```
SF(x) = P(X > x) = 1 - CDF(x)
```

#### 在滑水风险中的应用
- **X**：实际车速V
- **x**：临界滑水速度vc
- **SF(vc)**：车速超过临界速度的概率，即滑水风险概率

#### SciPy实现
```python
from scipy.stats import norm

# 计算滑水概率
prob_matrix = norm.sf(vc_matrix, loc=mu_v, scale=sigma_v)
```

### 7.3 对数尺度的重要性

#### 风险概率的数量级差异
滑水概率通常跨越多个数量级：
- **低风险区域**：P ≈ 10⁻⁷ (0.00001%)
- **中风险区域**：P ≈ 10⁻³ (0.1%)  
- **高风险区域**：P ≈ 10⁻¹ (10%)

#### 对数尺度的优势
- **线性化处理**：将指数关系转换为线性关系
- **直观分级**：每个数量级对应一个风险等级
- **数值稳定性**：避免极小概率的浮点精度问题

---

## 🎯 第二部分：多级风险等级划分（60分钟）

### 8.1 五级风险等级体系

#### 风险等级定义
项目采用A-E五级风险等级体系：

| 等级 | 概率范围 | 风险描述 | 工程意义 |
|------|----------|----------|----------|
| **A** | P ≥ 10⁻¹ | 高风险 | 立即限速管控 |
| **B** | 10⁻³ ≤ P < 10⁻¹ | 中高风险 | 预警提示 |
| **C** | 10⁻⁵ ≤ P < 10⁻³ | 中风险 | 日常监控 |
| **D** | 10⁻⁷ ≤ P < 10⁻⁵ | 中低风险 | 常规巡检 |
| **E** | P < 10⁻⁷ | 低风险 | 安全状态 |

#### 项目中的实现代码
```python
# modules/risk_assessment.py 中的风险等级划分
risk_level_matrix = np.full_like(prob_matrix, 'E', dtype=object)
risk_score_matrix = np.zeros_like(prob_matrix, dtype=int)

# A(高风险): P >= 1e-1 (10%)
mask_A = prob_matrix >= 1e-1
# B(中高风险): 10^-3 <= P < 10^-1
mask_B = (prob_matrix >= 1e-3) & (prob_matrix < 1e-1)
# C(中风险): 10^-5 <= P < 10^-3
mask_C = (prob_matrix >= 1e-5) & (prob_matrix < 1e-3)
# D(中低风险): 10^-7 <= P < 10^-5
mask_D = (prob_matrix >= 1e-7) & (prob_matrix < 1e-5)
# E(低风险): P < 10^-7 默认已是 E 级

risk_level_matrix[mask_A] = 'A'
risk_score_matrix[mask_A] = 4
risk_level_matrix[mask_B] = 'B'
risk_score_matrix[mask_B] = 3
risk_level_matrix[mask_C] = 'C'
risk_score_matrix[mask_C] = 2
risk_level_matrix[mask_D] = 'D'
risk_score_matrix[mask_D] = 1
```

### 8.2 风险评分矩阵设计

#### 评分体系的意义
- **数值化表示**：便于后续的计算机视觉处理
- **等级映射**：A=4, B=3, C=2, D=1, E=0
- **可视化友好**：可直接用于热力图颜色映射

#### 评分矩阵的应用
```python
# 用于Plotly热力图的颜色映射
fig = px.imshow(
    transposed_matrix,
    color_continuous_scale=[
        (0.0, "green"),   # E级: 绿色
        (0.25, "lime"),   # D级: 浅绿  
        (0.5, "yellow"),  # C级: 黄色
        (0.75, "orange"), # B级: 橙色
        (1.0, "red")      # A级: 红色
    ],
    zmin=0, zmax=4,
)
```

### 8.3 自定义风险阈值配置

#### 参数化风险分级
```python
def configurable_risk_classification(prob_matrix, thresholds=None):
    """
    可配置的风险等级划分
    
    Parameters:
    -----------
    prob_matrix : array
        滑水概率矩阵
    thresholds : dict, optional
        自定义阈值字典，格式：
        {
            'A': 1e-1,    # P >= 1e-1 → A级
            'B': 1e-3,    # P >= 1e-3 → B级  
            'C': 1e-5,    # P >= 1e-5 → C级
            'D': 1e-7     # P >= 1e-7 → D级
        }
    """
    if thresholds is None:
        thresholds = {'A': 1e-1, 'B': 1e-3, 'C': 1e-5, 'D': 1e-7}
    
    risk_level_matrix = np.full_like(prob_matrix, 'E', dtype=object)
    risk_score_matrix = np.zeros_like(prob_matrix, dtype=int)
    
    # 按风险等级从高到低依次判断
    if thresholds['A'] is not None:
        mask_A = prob_matrix >= thresholds['A']
        risk_level_matrix[mask_A] = 'A'
        risk_score_matrix[mask_A] = 4
    
    if thresholds['B'] is not None:
        mask_B = (prob_matrix >= thresholds['B']) & (prob_matrix < thresholds['A'])
        risk_level_matrix[mask_B] = 'B'
        risk_score_matrix[mask_B] = 3
    
    if thresholds['C'] is None:
        thresholds['C'] = 1e-5
    mask_C = (prob_matrix >= thresholds['C']) & (prob_matrix < thresholds['B'])
    risk_level_matrix[mask_C] = 'C'
    risk_score_matrix[mask_C] = 2
    
    if thresholds['D'] is None:
        thresholds['D'] = 1e-7
    mask_D = (prob_matrix >= thresholds['D']) & (prob_matrix < thresholds['C'])
    risk_level_matrix[mask_D] = 'D'
    risk_score_matrix[mask_D] = 1
    
    return risk_level_matrix, risk_score_matrix
```

### 8.4 风险等级验证实验

#### 创建测试函数
```python
# risk_validation.py
import numpy as np

def test_risk_classification():
    """测试风险等级划分的正确性"""
    
    # 创建测试概率矩阵
    test_probs = np.array([
        [1e-8, 1e-6, 1e-4, 1e-2, 1e-0],
        [5e-8, 5e-6, 5e-4, 5e-2, 5e-1],
        [1e-7, 1e-5, 1e-3, 1e-1, 1e+0]
    ])
    
    levels, scores = configurable_risk_classification(test_probs)
    
    print("测试概率矩阵:")
    print(test_probs)
    print("\n风险等级矩阵:")
    print(levels)
    print("\n风险评分矩阵:")
    print(scores)
    
    # 验证预期结果
    expected_levels = np.array([
        ['E', 'D', 'C', 'B', 'A'],
        ['E', 'D', 'C', 'B', 'A'], 
        ['D', 'C', 'B', 'A', 'A']
    ])
    
    assert np.array_equal(levels, expected_levels), "风险等级划分错误！"
    print("✅ 风险等级划分验证通过！")

# 运行测试
test_risk_classification()
```

---

## 📊 第三部分：面域风险聚合统计（45分钟）

### 9.1 面域风险统计指标

#### 关键统计指标
- **高危区域占比**：A级和B级区域占总面积的比例
- **风险分布直方图**：各级风险区域的面积分布
- **最大风险等级**：整个路段的最高风险等级
- **平均风险评分**：风险评分的加权平均值

#### 项目中的统计实现
```python
# modules/risk_assessment.py 中的动态决策函数
def dynamic_decision(risk_level_matrix, area_ratio=1.0):
    total_pixels = risk_level_matrix.size * area_ratio
    high_risk_pixels = np.sum((risk_level_matrix == 'A') | (risk_level_matrix == 'B'))
    high_risk_ratio = high_risk_pixels / total_pixels
```

### 9.2 面积比例计算

#### 像素到物理面积的转换
```python
def calculate_physical_area(risk_matrix, pixel_area_m2, area_ratio=1.0):
    """
    计算各风险等级的实际物理面积
    
    Parameters:
    -----------
    risk_matrix : array
        风险等级矩阵
    pixel_area_m2 : float
        单个像素对应的物理面积(m²)
    area_ratio : float
        面积缩放系数（考虑超分辨率等因素）
    """
    total_area = risk_matrix.size * pixel_area_m2 * area_ratio
    
    area_stats = {}
    for level in ['A', 'B', 'C', 'D', 'E']:
        pixel_count = np.sum(risk_matrix == level)
        physical_area = pixel_count * pixel_area_m2 * area_ratio
        area_stats[level] = {
            'pixels': pixel_count,
            'area_m2': physical_area,
            'ratio': physical_area / total_area
        }
    
    return area_stats, total_area
```

### 9.3 风险分布可视化

#### 风险等级分布饼图
```python
import plotly.graph_objects as go

def plot_risk_distribution_pie(area_stats):
    """绘制风险等级分布饼图"""
    labels = []
    values = []
    colors = ['#FF0000', '#FF8C00', '#FFFF00', '#90EE90', '#00FF00']
    
    for i, level in enumerate(['A', 'B', 'C', 'D', 'E']):
        ratio = area_stats[level]['ratio']
        if ratio > 0:
            labels.append(f'{level}级风险 ({ratio:.1%})')
            values.append(ratio)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=colors)])
    fig.update_layout(title='风险等级面积分布')
    return fig
```

#### 风险评分热力图
```python
def risk_heatmap(risk_score_matrix):
    """绘制风险评分热力图"""
    # 反转 Y 轴使其与路面图像的朝向一致
    transposed_matrix = risk_score_matrix.T
    fig = px.imshow(
        transposed_matrix,
        color_continuous_scale=[
            (0.0, "green"),  # E级: 绿
            (0.25, "lime"),  # D级: 浅绿
            (0.5, "yellow"), # C级: 黄
            (0.75, "orange"),# B级: 橙
            (1.0, "red")     # A级: 红
        ],
        zmin=0, zmax=4,
        labels={'color': '风险等级 (0=E, 4=A)'},
    )

    fig.update_layout(
        xaxis_title='纵向行驶距离 (采样点)',
        yaxis_title='横向物理宽度 (采样点)',
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['E (低)', 'D (中低)', 'C (中)', 'B (中高)', 'A (高)']
        )
    )
    return fig
```

### 9.4 统计结果的工程意义

#### 风险比例的工程阈值
- **>5%高危区域**：危险状态，需要立即采取措施
- **1%-5%高危区域**：关注状态，需要预警和监控  
- **<1%高危区域**：安全状态，常规维护即可

#### 动态决策的业务逻辑
```python
# modules/risk_assessment.py 中的完整决策逻辑
if high_risk_ratio > 0.05:  # 超过 5% 的面积处于高危
    status = "危险 (全域或大面积滑水隐患)"
    traffic = "立即实施限速管控 (建议降至 60 km/h 以下)，或开启车道级封闭指引。"
    maint = "路面可能存在贯通性车辙或严重排水不畅，需重点排查病害区域，考虑铣刨重铺。"
elif high_risk_ratio > 0.01:  # 1% ~ 5% 的高危面积
    status = "关注 (局部存在高危积水坑槽)"
    traffic = "建议开启雨天安全预警情报板，提示“前方局部积水，注意方向盘跑偏”。"
    maint = "关注积水最深的局部坑槽或微车辙，雨后建议安排日常局部修补。"
else:
    status = "安全 (路面排水状况良好)"
    traffic = "路段整体处于低风险等级，维持正常限速 (80 km/h)。"
    maint = "暂无特殊养护需求，按常规周期巡检即可。"
```

---

## 🤖 第四部分：动态决策逻辑实现（15分钟）

### 10.1 决策函数的完整实现

#### 输入输出设计
```python
def dynamic_decision(risk_level_matrix, area_ratio=1.0):
    """
    根据面域风险分布生成动态决策
    
    Parameters:
    -----------
    risk_level_matrix : array
        风险等级矩阵 (包含'A', 'B', 'C', 'D', 'E')
    area_ratio : float
        面积缩放系数
        
    Returns:
    --------
    dict : 包含决策结果的字典
        - overall_status: 整体评估状态
        - high_risk_area_ratio: 高危区域占比
        - traffic_control: 交通管控建议  
        - maintenance_action: 养护指导建议
    """
    # ... 实现逻辑 ...
    return decision_dict
```

### 10.2 决策结果的应用

#### 在Streamlit应用中的集成
```python
# app.py 中的风险评估调用
if run_risk_btn:
    water_depth = st.session_state.final_depth_crop
    with st.spinner("⏳ 正在结合水膜厚度与车速分布计算全域滑水概率..."):
        prob_matrix, risk_level_matrix, risk_score_matrix = evaluate_hydroplaning_risk(water_depth * 1000.0)
        area_ratio = st.session_state.matrix_full.shape[1] / st.session_state.matrix_crop.shape[1]
        decision = dynamic_decision(risk_level_matrix, area_ratio)

        st.session_state.risk_results = {
            "decision": decision,
            "risk_score_matrix": risk_score_matrix
        }
```

#### 决策结果的展示
```python
# app.py 中的决策结果显示
decision = st.session_state.risk_results["decision"]

col1, col2 = st.columns(2)
with col1:
    if "危险" in decision['overall_status']:
        st.error(f"**整体评估状态:** {decision['overall_status']}")
    elif "关注" in decision['overall_status']:
        st.warning(f"**整体评估状态:** {decision['overall_status']}")
    else:
        st.success(f"**整体评估状态:** {decision['overall_status']}")
    st.metric(label="高风险区 (A/B级) 占比", value=decision['high_risk_area_ratio'])

with col2:
    st.info(f"**🚦 动态交通管控建议:** \n\n{decision['traffic_control']}")
    st.warning(f"**🛠️ 宏观养护指导:** \n\n{decision['maintenance_action']}")
```

---

## 📝 第五部分：课后作业与实践

### 11.1 基础作业

#### 作业1：风险等级划分实现
- [ ] 实现五级风险等级划分函数
- [ ] 测试不同概率值的风险等级分配
- [ ] 验证边界条件的正确性

#### 作业2：面域统计计算
- [ ] 实现各风险等级的面积统计
- [ ] 计算高危区域占比
- [ ] 可视化风险分布结果

### 11.2 进阶作业

#### 作业3：自定义风险阈值
- [ ] 实现可配置的风险阈值系统
- [ ] 测试不同阈值组合的效果
- [ ] 添加用户界面进行阈值调节

#### 作业4：动态决策优化
- [ ] 扩展决策逻辑，支持更多场景
- [ ] 添加时间维度的风险演化分析
- [ ] 实现多路段综合风险评估

### 11.3 思考题

1. **阈值选择**：如何科学地确定风险等级的阈值？这些阈值是否应该根据不同地区、不同季节进行调整？

2. **统计方法**：除了面积比例，还有哪些统计指标可以更好地反映风险状况？

3. **决策逻辑**：当前的决策逻辑是否足够全面？还需要考虑哪些因素？

4. **扩展应用**：这套风险评估方法如何应用到其他交通安全场景（如冰雪路面、雾天能见度）？

---

## 🔍 第六部分：常见问题FAQ

### Q1：风险等级划分结果不连续怎么办？
**原因分析**：
- 概率计算存在数值误差
- 阈值边界处理不当

**解决方案**：
```python
# 添加数值容差处理
epsilon = 1e-12
mask_A = prob_matrix >= (1e-1 - epsilon)
mask_B = (prob_matrix >= (1e-3 - epsilon)) & (prob_matrix < (1e-1 + epsilon))
# ... 其他等级类似处理
```

### Q2：高危区域占比计算不准确怎么办？
**可能原因**：
- 面积缩放系数设置错误
- 像素面积计算有误

**解决方案**：
```python
# 验证面积计算
def verify_area_calculation(risk_matrix, dx_mm, area_ratio):
    pixel_area = (dx_mm / 1000.0) ** 2  # 转换为平方米
    total_pixels = risk_matrix.size
    total_area = total_pixels * pixel_area * area_ratio
    
    # 手动计算验证
    manual_area = 0
    for level in ['A', 'B', 'C', 'D', 'E']:
        pixels = np.sum(risk_matrix == level)
        manual_area += pixels * pixel_area * area_ratio
    
    assert abs(total_area - manual_area) < 1e-6, "面积计算错误！"
    return total_area
```

### Q3：如何处理极端概率值？
**解决方案**：
```python
# 处理极小概率值
prob_matrix = np.clip(prob_matrix, 1e-15, 1-1e-15)

# 或者使用对数概率进行计算
log_prob = np.log(prob_matrix + 1e-15)
# 在显示时再转换回线性尺度
```

---

## 📚 第七部分：延伸学习资源

### 推荐文献
- **"Risk Assessment and Management in Transportation Engineering"** - Transportation Research Board
- **"Statistical Methods for Risk Analysis"** - NASA Risk Management Handbook
- **"Probability and Statistics for Engineers"** - Walpole et al.

### 相关标准
- **ISO 31000** - 风险管理标准
- **《公路工程风险评估规范》** - 中国交通运输部
- **FHWA Risk-Based Decision Making Guidelines** - 美国联邦公路管理局

### 下节课预告
**第8课：计算机视觉在工程检测中的应用**
- 连通域算法识别高危区域
- 形态学处理技术
- 区域特征提取（面积、深度、形状）
- 噪声过滤策略

---

> **学习提示**：概率统计是连接理论模型和工程决策的桥梁，深入理解对数尺度风险分级对构建可靠的智能决策系统至关重要。

**祝您学习愉快！** 🚀

---
*第七课内容最后更新：2026年5月19日*