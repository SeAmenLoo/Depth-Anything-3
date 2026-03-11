# 📚 DepthAnything3 API 文档（API Documentation）

## 📑 目录（Table of Contents）

1. [📖 概览](#overview)
2. [💡 使用示例](#usage-examples)
3. [🔧 核心 API](#core-api)
   - [DepthAnything3 类](#depthanything3-class)
   - [inference() 方法](#inference-method)
4. [⚙️ 参数说明](#parameters)
   - [输入参数](#input-parameters)
   - [位姿对齐参数](#pose-alignment-parameters)
   - [特征导出参数](#feature-export-parameters)
   - [渲染参数](#rendering-parameters)
   - [处理参数](#processing-parameters)
   - [导出参数](#export-parameters)
5. [📤 导出格式](#export-formats)
6. [↩️ 返回值](#return-value)

## 📖 概览 <a id="overview"></a>

本文档提供 DepthAnything3 的完整 API 参考，包括使用示例、参数规格、导出格式与高级特性。内容覆盖基础的位姿与深度估计工作流，以及支持位姿条件（pose-conditioned）的高级处理流程，并提供多种导出能力。

## 💡 使用示例 <a id="usage-examples"></a>

下面是一些快速示例，帮助你快速上手：

### 🚀 基础深度估计（Basic Depth Estimation）
```python
from depth_anything_3.api import DepthAnything3

# 初始化并运行推理
model = DepthAnything3.from_pretrained("depth-anything/DA3NESTED-GIANT-LARGE").to("cuda")
prediction = model.inference(["image1.jpg", "image2.jpg"])
```

### 📷 位姿条件深度估计（Pose-Conditioned Depth Estimation）
```python
import numpy as np

# 传入相机参数以获得更好的跨视图一致性
prediction = model.inference(
    image=["image1.jpg", "image2.jpg"],
    extrinsics=extrinsics_array,  # (N, 4, 4)
    intrinsics=intrinsics_array   # (N, 3, 3)
)
```

### 📤 导出结果（Export Results）
```python
# 导出深度数据与 3D 可视化
prediction = model.inference(
    image=image_paths,
    export_dir="./output",
    export_format="mini_npz-glb"
)
```

### 🔍 特征提取（Feature Extraction）
```python
# 导出指定层的中间特征
prediction = model.inference(
    image=image_paths,
    export_dir="./output",
    export_format="feat_vis",
    export_feat_layers=[0, 1, 2]  # 导出第 0、1、2 层特征
)
```

### ✨ 高斯点扩展导出（Advanced Export with Gaussian Splatting）
```python
# 导出多个格式（包含 Gaussian Splatting）
# 注意：infer_gs=True 需要 da3-giant 或 da3nested-giant-large 模型
model = DepthAnything3(model_name="da3-giant").to("cuda")

prediction = model.inference(
    image=image_paths,
    extrinsics=extrinsics_array,
    intrinsics=intrinsics_array,
    export_dir="./output",
    export_format="npz-glb-gs_ply-gs_video",
    align_to_input_ext_scale=True,
    infer_gs=True,  # gs_ply 与 gs_video 导出必需
)
```

### 🎨 特征可视化高级导出（Advanced Export with Feature Visualization）
```python
# 导出时包含中间特征可视化
prediction = model.inference(
    image=image_paths,
    export_dir="./output",
    export_format="mini_npz-glb-depth_vis-feat_vis",
    export_feat_layers=[0, 5, 10, 15, 20],
    feat_vis_fps=30,
)
```

### 📐 使用基于射线的位姿估计（Using Ray-Based Pose Estimation）
```python
# 使用 ray-based 位姿估计替代 camera decoder
prediction = model.inference(
    image=image_paths,
    export_dir="./output",
    export_format="glb",
    use_ray_pose=True,  # 启用 ray-based 位姿估计
)
```

### 🎯 参考视图选择（Reference View Selection）
```python
# 多视图输入时自动选择最佳参考视图
prediction = model.inference(
    image=image_paths,
    ref_view_strategy="saddle_balanced",  # Default: balanced selection
)

# 视频序列场景可用中间帧作为参考
prediction = model.inference(
    image=video_frames,
    ref_view_strategy="middle",  # Good for temporally ordered inputs
)
```

## 🔧 核心 API <a id="core-api"></a>

### 🔨 DepthAnything3 类（DepthAnything3 Class） <a id="depthanything3-class"></a>

这是主 API 类，提供深度估计能力，并可选支持位姿条件（pose conditioning）。

#### 🎯 初始化（Initialization）

```python
from depth_anything_3 import DepthAnything3

# 使用模型预设名称初始化
model = DepthAnything3(model_name="da3-large")
model = model.to("cuda")  # 移动到 GPU
```

**Parameters:**
- `model_name` (str, default: "da3-large")：要使用的模型预设名称。
  - **Available models:**
    - 🦾 `"da3-giant"` - 1.15B 参数，any-view 模型，支持 GS
    - ⭐ `"da3-large"` - 0.35B 参数，any-view 模型（多数场景推荐）
    - 📦 `"da3-base"` - 0.12B 参数，any-view 模型
    - 🪶 `"da3-small"` - 0.08B 参数，any-view 模型
    - 👁️ `"da3mono-large"` - 0.35B 参数，仅单目深度
    - 📏 `"da3metric-large"` - 0.35B 参数，度量深度并带天空分割
    - 🎯 `"da3nested-giant-large"` - 1.40B 参数，包含全部特性的大型 nested 模型

### 🚀 inference() 方法（inference() Method） <a id="inference-method"></a>

主要的推理方法：处理输入图像并返回深度预测结果。

```python
prediction = model.inference(
    image=image_list,
    extrinsics=extrinsics_array,      # Optional
    intrinsics=intrinsics_array,      # Optional
    align_to_input_ext_scale=True,   # Whether to align predicted poses to input scale
    infer_gs=True,                   # Enable Gaussian branch for gs exports
    use_ray_pose=False,              # Use ray-based pose estimation instead of camera decoder
    ref_view_strategy="saddle_balanced",  # Reference view selection strategy
    render_exts=render_extrinsics,    # Optional renders for gs_video
    render_ixts=render_intrinsics,    # Optional renders for gs_video
    render_hw=(height, width),        # Optional renders for gs_video
    process_res=504,
    process_res_method="upper_bound_resize",
    export_dir="output_directory",    # Optional
    export_format="mini_npz",
    export_feat_layers=[],            # List of layer indices to export features from
    conf_thresh_percentile=40.0,      # Confidence threshold percentile for depth map in GLB export
    num_max_points=1_000_000,         # Maximum number of points to export in GLB export
    show_cameras=True,                # Whether to show cameras in GLB export
    feat_vis_fps=15,                  # Frames per second for feature visualization in feat_vis export
    export_kwargs={}                  # Optional, additional arguments to export functions. export_format:key:val, see 'Parameters/Export Parameters' for details
)
```

## ⚙️ 参数说明 <a id="parameters"></a>

### 📸 输入参数 <a id="input-parameters"></a>

#### `image` (required)
- **Type**: `List[Union[np.ndarray, Image.Image, str]]`
- **Description**: 输入图像列表。元素可以是 numpy 数组、PIL Image 或文件路径。
- **Example**:
  ```python
  # From file paths
  image = ["image1.jpg", "image2.jpg", "image3.jpg"]

  # From numpy arrays
  image = [np.array(img1), np.array(img2)]

  # From PIL Images
  image = [Image.open("image1.jpg"), Image.open("image2.jpg")]
  ```

#### `extrinsics` (optional)
- **Type**: `Optional[np.ndarray]`
- **Shape**: `(N, 4, 4)`，其中 N 为输入图像数量
- **Description**: 相机外参矩阵（world-to-camera 变换）。提供该参数会启用位姿条件深度估计模式。
- **Note**: 若不提供，模型运行在标准深度估计模式下。

#### `intrinsics` (optional)
- **Type**: `Optional[np.ndarray]`
- **Shape**: `(N, 3, 3)`，其中 N 为输入图像数量
- **Description**: 相机内参矩阵，包含焦距与主点信息。提供该参数会启用位姿条件深度估计模式。

### 🎯 位姿对齐参数 <a id="pose-alignment-parameters"></a>

#### `align_to_input_ext_scale` (default: True)
- **Type**: `bool`
- **Description**: 当为 True 时，预测的外参会被输入外参替换，深度图会被重缩放以匹配其度量尺度；当为 False 时，函数会返回内部通过 Umeyama 对齐得到的对齐位姿。

#### `infer_gs` (default: False)
- **Type**: `bool`
- **Description**: 启用 Gaussian Splatting 分支以支持高斯相关导出。在使用 `gs_ply` 或 `gs_video` 导出格式时必须为 True。

#### `use_ray_pose` (default: False)
- **Type**: `bool`
- **Description**: 使用基于射线（ray-based）的位姿估计替代 camera decoder。为 True 时模型使用射线预测头来估计相机位姿；为 False 时使用 camera decoder 方法。

#### `ref_view_strategy` (default: "saddle_balanced")
- **Type**: `str`
- **Description**: 多视图输入时参考视图的选择策略。可选：`"first"`, `"middle"`, `"saddle_balanced"`, `"saddle_sim_range"`。仅当视图数量 ≥ 3 时生效。策略对比请见 [详细文档](funcs/ref_view_strategy.md)。
- **Available strategies**:
  - `"saddle_balanced"`：在多指标上选取特征更均衡的视图（推荐默认）
  - `"saddle_sim_range"`：选取相似度范围最大的视图
  - `"first"`：始终使用第一张（不推荐；当视图 < 3 时等价于不重排）
  - `"middle"`：使用中间视图（推荐用于视频序列）

### 🔍 特征导出参数 <a id="feature-export-parameters"></a>

#### `export_feat_layers` (default: [])
- **Type**: `List[int]`
- **Description**: 需要导出的中间特征层索引列表。特征会存入 Prediction 对象的 `aux` 字典中，键名类似 `feat_layer_0`, `feat_layer_1` 等。

### 🎥 渲染参数 <a id="rendering-parameters"></a>

这些参数仅在导出高斯渲染视频（`export_format` 包含 `"gs_video"`）时使用，用于描述一条包含 ``M`` 个视角的辅助相机轨迹。

#### `render_exts` (optional)
- **Type**: `Optional[np.ndarray]`
- **Shape**: `(M, 4, 4)`
- **Description**: 合成轨迹的相机外参。如果省略，导出器会回退使用预测位姿。

#### `render_ixts` (optional)
- **Type**: `Optional[np.ndarray]`
- **Shape**: `(M, 3, 3)`
- **Description**: 每一帧渲染对应的相机内参。设为 `None` 将复用输入内参。

#### `render_hw` (optional)
- **Type**: `Optional[Tuple[int, int]]`
- **Description**: 渲染输出分辨率 `(height, width)`。若不提供，默认使用输入分辨率。

### ⚡ 处理参数 <a id="processing-parameters"></a>

#### `process_res` (default: 504)
- **Type**: `int`
- **Description**: 处理的基准分辨率。模型会在推理前将图像 resize 到该分辨率策略所得到的大小。

#### `process_res_method` (default: "upper_bound_resize")
- **Type**: `str`
- **Description**: 将图像调整到目标分辨率的策略。
- **Options**:
  - `"upper_bound_resize"`：使指定维度（例如 504）成为较长边
  - `"lower_bound_resize"`：使指定维度（例如 504）成为较短边
- **Example**:
  - 输入：1200×1600 → 输出：378×504（`process_res=504`, `process_res_method="upper_bound_resize"`）
  - 输入：504×672 → 输出：504×672（无需变更）

### 📦 导出参数 <a id="export-parameters"></a>

#### `export_dir` (optional)
- **Type**: `Optional[str]`
- **Description**: 导出文件保存目录。若不提供，则不写出文件。

#### `export_format` (default: "mini_npz")
- **Type**: `str`
- **Description**: 导出格式。支持用 `-` 连接多个格式。
- **Example**: `"mini_npz-glb"` 同时导出 mini_npz 与 glb。

#### 🌐 GLB Export Parameters

这些参数会直接传入 `inference()`，且仅在 `export_format` 包含 `"glb"` 时生效。

##### `conf_thresh_percentile` (default: 40.0)
- **Type**: `float`
- **Description**: 自适应置信度阈值的下分位数。低于该分位数的点会从点云中过滤掉。

##### `num_max_points` (default: 1,000,000)
- **Type**: `int`
- **Description**: 导出点云的最大点数。超过上限时将进行下采样。

##### `show_cameras` (default: True)
- **Type**: `bool`
- **Description**: 是否在导出的 GLB 中包含相机线框以便可视化。

#### 🎨 Feature Visualization Parameters

这些参数会直接传入 `inference()`，且仅在 `export_format` 包含 `"feat_vis"` 时生效。

##### `feat_vis_fps` (default: 15)
- **Type**: `int`
- **Description**: 将多图特征可视化成视频时的输出帧率。

#### ✨🎥 3DGS and 3DGS Video Parameters

这些参数会直接传入 `inference()`，且仅在 `export_format` 包含 `"gs_ply"` 或 `"gs_video"` 时生效。

##### `export_kwargs` (default: `{}`)
- Type: `dict[str, dict[str, Any]]`
- Description: 针对每个导出格式的额外参数字典，主要用于 `"gs_ply"` 与 `"gs_video"`。
  - Access pattern: `export_kwargs[export_format][key] = value`
  - Example:
    ```python
    {
        "gs_ply": {
            "gs_views_interval": 1,
        },
        "gs_video": {
            "trj_mode": "interpolate_smooth",
            "chunk_size": 1,
            "vis_depth": None,
        },
    }
    ```

## 📤 导出格式 <a id="export-formats"></a>

API 支持多种导出格式以适配不同使用场景：

### 📊 `mini_npz`
- **Description**: 最小化的 NPZ 格式，仅包含关键数据
- **Contents**: `depth`, `conf`, `exts`, `ixts`
- **Use case**: 轻量存储深度数据与相机参数

### 📦 `npz`
- **Description**: 完整 NPZ 格式，包含更全面的数据
- **Contents**: `depth`, `conf`, `exts`, `ixts`, `image`, etc.
- **Use case**: 用于高级处理的完整数据导出

### 🌐 `glb`
- **Description**: 带点云与相机位姿的 3D 可视化格式
- **Contents**:
  - 带颜色的点云（颜色来自原始图像）
  - 用于可视化的相机线框
  - 基于置信度的过滤与下采样
- **Use case**: 3D 可视化、检查与分析
- **Features**:
  - 自动处理天空深度
  - 置信度阈值过滤
  - 背景过滤（黑/白）
  - 场景尺度归一化
- **Parameters**（通过 `inference()` 直接传入）:
  - `conf_thresh_percentile` (float, default: 40.0)
  - `num_max_points` (int, default: 1,000,000)
  - `show_cameras` (bool, default: True)

### ✨ `gs_ply`
- **Description**: Gaussian Splatting 点云格式
- **Contents**: PLY 形式的 3DGS 数据。兼容常见 3DGS 查看器，如 [SuperSplat](https://superspl.at/editor)（推荐）、[SPARK](https://sparkjs.dev/viewer/)。
- **Use case**: Gaussian Splatting 重建
- **Requirements**: 调用 `inference()` 时必须设置 `infer_gs=True`。仅 `da3-giant` 与 `da3nested-giant-large` 模型支持。
- **Additional configs**（通过 `export_kwargs` 提供，见 [Export Parameters](#export-parameters)）:
  - `gs_views_interval`: 每 N 个视图导出一次 3DGS，默认 `1`。

### 🎥 `gs_video`
- **Description**: 将 3DGS 光栅化渲染为视频
- **Contents**: 使用给定视角或预定义相机轨迹渲染得到的 3DGS 视频
- **Use case**: Gaussian Splatting 的视频渲染
- **Requirements**: 调用 `inference()` 时必须设置 `infer_gs=True`。仅 `da3-giant` 与 `da3nested-giant-large` 模型支持。
- **Note**: 可选使用 `render_exts`、`render_ixts`、`render_hw` 在 `inference()` 中指定新视角渲染。
- **Additional configs**（通过 `export_kwargs` 提供，见 [Export Parameters](#export-parameters)）:
  - `extrinsics`: 新视角 world-to-camera 位姿（可省略，省略则回退使用输入视角预测位姿；也可用 `render_exts`）
  - `intrinsics`: 新视角相机内参（可省略，省略则回退使用预测内参；也可用 `render_ixts`）
  - `out_image_hw`: 输出分辨率 `H x W`（可省略，省略则回退输入分辨率；也可用 `render_hw`）
  - `chunk_size`: 每批次光栅化的视图数，默认 `8`
  - `trj_mode`: 预定义相机轨迹
  - `color_mode`: 同 [gsplat](https://docs.gsplat.studio/main/apis/rasterization.html#gsplat.rasterization) 中的 `render_mode`
  - `vis_depth`: 深度与 RGB 的组合方式，默认 `hcat`（水平拼接）
  - `enable_tqdm`: 是否显示 tqdm 进度条
  - `output_name`: 渲染视频的文件名
  - `video_quality`: 保存视频质量，默认 `high`
    - `high`: 高质量（默认）
    - `medium`: 中等质量（平衡体积与质量）
    - `low`: 低质量（更小体积）

### 🔍 `feat_vis`
- **Description**: 特征可视化格式
- **Contents**: 将指定层的中间特征进行 PCA 可视化
- **Use case**: 模型可解释性与特征分析
- **Note**: 需要指定 `export_feat_layers`
- **Parameters**（通过 `inference()` 直接传入）:
  - `feat_vis_fps` (int, default: 15)

### 🎨 `depth_vis`
- **Description**: 深度可视化格式
- **Contents**: 与原图并排的伪彩色深度图
- **Use case**: 直观检查深度估计质量

### 🔗 Multiple Format Export
你可以使用 `-` 同时导出多个格式：

```python
# Export both mini_npz and glb formats
export_format = "mini_npz-glb"

# Export multiple formats
export_format = "npz-glb-gs_ply"
```

## ↩️ 返回值 <a id="return-value"></a>

`inference()` 会返回一个 `Prediction` 对象，包含如下属性：

### 📊 核心输出（Core Outputs）

- **depth**: `np.ndarray` - 估计的深度图，形状为 `(N, H, W)`，其中 N 为图像数量，H/W 为高/宽。
- **conf**: `np.ndarray` - 置信度图，形状为 `(N, H, W)`，用于表示预测可靠性（可选，取决于模型）。

### 📷 相机参数（Camera Parameters）

- **extrinsics**: `np.ndarray` - 相机外参矩阵，形状为 `(N, 3, 4)`，表示 world-to-camera 变换。仅当估计或提供了相机位姿时存在。
- **intrinsics**: `np.ndarray` - 相机内参矩阵，形状为 `(N, 3, 3)`，包含焦距与主点信息。仅当估计或提供了相机位姿时存在。

### 🎁 额外输出（Additional Outputs）

- **processed_images**: `np.ndarray` - 预处理后的输入图像，形状为 `(N, H, W, 3)`，RGB 格式（0-255 uint8）。
- **aux**: `dict` - 辅助输出，包括：
  - `feat_layer_X`: 第 X 层的中间特征（当指定 `export_feat_layers` 时）
  - `gaussians`: 3D Gaussian Splats 数据（当 `infer_gs=True` 时）

### 💻 使用示例（Usage Example）

```python
prediction = model.inference(image=["img1.jpg", "img2.jpg"])

# 访问深度图
depth_maps = prediction.depth  # shape: (2, H, W)

# 访问置信度
if hasattr(prediction, 'conf'):
    confidence = prediction.conf

# 访问相机参数（若存在）
if hasattr(prediction, 'extrinsics'):
    camera_poses = prediction.extrinsics  # shape: (2, 4, 4)

if hasattr(prediction, 'intrinsics'):
    camera_intrinsics = prediction.intrinsics  # shape: (2, 3, 3)

# 访问中间特征（当设置 export_feat_layers 时）
if hasattr(prediction, 'aux') and 'feat_layer_0' in prediction.aux:
    features = prediction.aux['feat_layer_0']
```
