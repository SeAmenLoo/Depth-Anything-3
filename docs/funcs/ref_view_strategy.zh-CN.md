# 📐 参考视图选择策略（Reference View Selection Strategy）

## 📖 概览（Overview）

参考视图选择（Reference view selection）是多视图深度估计中的一个组件。在处理多个输入视图时，模型需要确定哪一张视图作为深度预测的主要参考帧，从而定义世界坐标系。

不同的参考视图会导致不同的重建结果。这是多视图几何中的一个已知因素，并在 [PI3](https://arxiv.org/abs/2507.13347) 中进行了分析。参考视图的选择会影响场景内各视图深度预测的质量与一致性。


## 🚀 我们的简单方案：自动参考视图选择（Our Simple Solution: Automatic Reference View Selection）

DA3 提供了一种简单的方法来应对这个问题：基于 **class tokens** 的 **自动参考视图选择**。模型不依赖启发式规则或人工指定，而是分析所有输入视图的 class token 特征，智能选择最合适的参考帧。

---

## 🎨 可用策略（Available Strategies）

### 1. ⚖️ `saddle_balanced`（推荐，默认）

**理念：**  
选择一个在多种特征指标之间达到平衡的视图。该策略会寻找一个“折中”的视图：它既不会与其他视图过于相似，也不会过于不同，从而成为稳定的参考点。

**工作方式：**
1. 提取并归一化所有视图的 class tokens
2. 为每个视图计算三个互补指标：
   - **相似度得分**：与其他视图的平均余弦相似度
   - **特征范数**：原始特征的 L2 范数  
   - **特征方差**：特征维度上的方差
3. 将每个指标归一化到 [0, 1] 范围
4. 在三项指标上选择最接近 0.5（中位附近）的视图

### 2. 🎢 `saddle_sim_range`（相似度范围）

**理念：**  
选择与其他视图相似度范围最大的视图。该策略会识别“鞍点”视图：它与部分视图高度相似、与另一些视图差异较大，因此往往包含更丰富的信息，可作为锚点。

**工作方式：**
1. 计算所有视图两两之间的余弦相似度
2. 对每个视图，计算其与其他视图相似度的范围（最大值 - 最小值）
3. 选择相似度范围最大的视图

---

### 3. 1️⃣ `first`（不推荐）

**理念：**  
始终使用输入序列中的第一张视图作为参考。

**工作方式：**
直接返回索引 0。

**适用场景：**
- ⛔ 一般情况下不推荐
- 🔧 仅当你已手动对视图排序并确认第一张视图最优时使用
- 🐛 用于调试或基线对比

---

### 4. ⏸️ `middle`（中间帧）

**理念：**  
选择输入序列中间位置的视图作为参考。

**工作方式：**
返回索引 `S // 2` 的视图，其中 S 为视图数量。

**适用场景：**
- ⏱️ 仅在输入图像按时间顺序排列时推荐
- 🎬 视频序列（例如 **DA3-LONG** 设置）
- 📹 顺序采集场景，中间帧通常视角更稳定

**特定用例：DA3-LONG** 🎬  
在基于视频的深度估计场景（如 DA3-LONG）中，输入为连续帧时，`middle` 往往是 **最优选择**，因为它与所有其他帧的重叠程度最大。


## 💻 用法（Usage）

### 🐍 Python API（Python API）

```python
from depth_anything_3 import DepthAnything3

model = DepthAnything3.from_pretrained("depth-anything/DA3NESTED-GIANT-LARGE")

# Use default (saddle_balanced)
prediction = model.inference(
    images,
    ref_view_strategy="saddle_balanced"
)

# For video sequences, consider using middle
prediction = model.inference(
    video_frames,
    ref_view_strategy="middle"  # Good for temporal sequences
)

# For complex scenes with wide baselines
prediction = model.inference(
    images,
    ref_view_strategy="saddle_sim_range"
)
```

### 🖥️ 命令行（Command Line Interface）

```bash
# Default (saddle_balanced)
da3 auto input/ --export-dir output/

# Explicitly specify strategy
da3 auto input/ --ref-view-strategy saddle_balanced

# For video processing
da3 video input.mp4 --ref-view-strategy middle

# For wide-baseline multi-view
da3 images captures/ --ref-view-strategy saddle_sim_range
```

---

### 🎯 何时应用选择（When Selection Is Applied）

参考视图选择在以下条件满足时才会启用：
- 3️⃣ 视图数量 S ≥ 3

---

## 💡 推荐（Recommendations）

### 📋 快速指南（Quick Guide）

| 场景 | 推荐策略 | 理由 |
|----------|---------------------|-----------|
| **默认 / 不确定** | `saddle_balanced` | 稳健、均衡，适用于多种场景 |
| **视频帧** | `middle` | 时间一致性更好，中间帧视角更稳定 |
| **大基线多视图** | `saddle_sim_range` | 最大化信息覆盖 |
| **已排序输入** | `first` | 仅在你已手动优化顺序时使用 |
| **单张图像** | `first` | 自动使用（S ≤ 2 时不重排） |

### ✨ 最佳实践（Best Practices）

1. 🎯 **从默认开始**：`saddle_balanced` 在多数情况下表现良好
2. 🎬 **考虑输入类型**：视频用 `middle`，照片用 `saddle_balanced`
3. 🔬 **必要时做对比实验**：当结果不理想时尝试不同策略
4. 📊 **关注表现**：检查 `glb` 质量与跨视图一致性

---

## 🔧 技术细节（Technical Details）

### 🎚️ 触发阈值（Selection Threshold）

参考视图选择仅在以下条件触发：
```python
num_views >= 3  # At least 3 views required
```

当视图数量为 1-2 时，不进行重排（等价于使用 `first`）。

### ⚙️ 实现（Implementation）

选择发生在视觉 Transformer 的 `alt_start - 1` 层，即第一次全局注意力层之前。这保证所选参考视图会影响整个深度预测流水线。

---

## ❓ 常见问题（FAQ）

**Q: 🤔 为什么提供这个功能？**  
A: 模型可以处理任意视图顺序，但该功能会对参考视图选择进行自动优化，从而在多视图场景下帮助提升深度预测质量。

**Q: ⏱️ 会增加计算开销吗？**  
A: 额外开销可以忽略不计。

**Q: 🎮 我可以手动指定使用哪一张视图作为参考吗？**  
A: 不能直接通过该参数指定。你可以预先对输入图像进行排序，把你偏好的参考视图放在第一张，然后使用 `ref_view_strategy="first"`。

**Q: ⚙️ 如果不指定该参数会怎样？**  
A: 默认自动使用 `saddle_balanced` 策略。

**Q: 📊 论文基准里使用了这个功能吗？**  
A: 没有。论文中所有多视图实验默认使用 `first`。当前默认已更新为 `saddle_balanced` 以增强鲁棒性。

