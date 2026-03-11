# 🚀 Depth Anything 3 命令行界面（Command Line Interface）

## 📋 目录（Table of Contents）

- [📖 概览](#overview)
- [⚡ 快速开始](#quick-start)
- [📚 命令参考](#command-reference)
  - [🤖 auto - 自动模式](#auto---auto-mode)
  - [🖼️ image - 单图处理](#image---single-image-processing)
  - [🗂️ images - 图像目录处理](#images---image-directory-processing)
  - [🎬 video - 视频处理](#video---video-processing)
  - [📐 colmap - COLMAP 数据集处理](#colmap---colmap-dataset-processing)
  - [🔧 backend - 后端服务](#backend---backend-service)
  - [🎨 gradio - Gradio 应用](#gradio---gradio-application)
  - [🖼️ gallery - Gallery 服务](#gallery---gallery-server)
- [⚙️ 参数详解](#parameter-details)
- [💡 使用示例](#usage-examples)

## 📖 概览 <a id="overview"></a>

Depth Anything 3 CLI 提供完整的命令行工具集，支持图像深度估计、视频处理、COLMAP 数据集处理以及 Web 应用能力。

后端服务支持将模型缓存到 GPU，从而避免每次命令执行都重新加载模型。

## ⚡ 快速开始（Quick Start） <a id="quick-start"></a>

CLI 可以完全离线运行，也可以连接后端以复用缓存权重并进行任务调度：

```bash
# 🔧 启动后端服务（可选，使模型常驻 GPU 显存）
da3 backend --model-dir depth-anything/DA3NESTED-GIANT-LARGE

# 🚀 使用 auto 模式处理输入
da3 auto path/to/input --export-dir ./workspace/scene001

# ♻️ 复用后端处理下一次任务
da3 auto path/to/video.mp4 \
    --export-dir ./workspace/scene002 \
    --use-backend \
    --backend-url http://localhost:8008
```

每个导出目录通常包含 `scene.glb`、`scene.jpg`，以及根据所选格式可能额外生成 `depth_vis/`、`gs_video/` 等内容。

## 📚 命令参考（Command Reference） <a id="command-reference"></a>

### 🤖 auto - 自动模式（Auto Mode） <a id="auto---auto-mode"></a>

自动检测输入类型，并分发到对应的处理器。

**Usage:**

```bash
da3 auto INPUT_PATH [OPTIONS]
```

**Input Type Detection:**
- 🖼️ 单张图像文件（.jpg, .png, .jpeg, .webp, .bmp, .tiff, .tif）
- 📁 图像目录
- 🎬 视频文件（.mp4, .avi, .mov, .mkv, .flv, .wmv, .webm, .m4v）
- 📐 COLMAP 目录（包含 `images/` 与 `sparse/` 子目录）

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `INPUT_PATH` | str | Required | 输入路径（图像、目录、视频或 COLMAP） |
| `--model-dir` | str | Default model | 模型目录路径 |
| `--export-dir` | str | `debug` | 导出目录 |
| `--export-format` | str | `glb` | 导出格式（支持 `mini_npz`、`glb`、`feat_vis` 等，可用连字符组合） |
| `--device` | str | `cuda` | 运行设备 |
| `--use-backend` | bool | `False` | 使用后端服务推理 |
| `--backend-url` | str | `http://localhost:8008` | 后端服务 URL |
| `--process-res` | int | `504` | 处理分辨率 |
| `--process-res-method` | str | `upper_bound_resize` | 处理分辨率策略 |
| `--export-feat` | str | `""` | 导出指定层的特征（逗号分隔，如 `"0,1,2"`） |
| `--auto-cleanup` | bool | `False` | 自动清理导出目录（无需确认） |
| `--fps` | float | `1.0` | [Video] 抽帧 FPS |
| `--sparse-subdir` | str | `""` | [COLMAP] sparse 子目录（如 `sparse/0/` 则填 `"0"`） |
| `--align-to-input-ext-scale` | bool | `True` | [COLMAP] 将预测结果对齐到输入外参尺度 |
| `--use-ray-pose` | bool | `False` | 使用 ray-based 位姿估计替代 camera decoder |
| `--ref-view-strategy` | str | `saddle_balanced` | 参考视图选择策略：`first`、`middle`、`saddle_balanced`、`saddle_sim_range`。见 [文档](funcs/ref_view_strategy.md) |
| `--conf-thresh-percentile` | float | `40.0` | [GLB] 自适应置信度阈值下分位数 |
| `--num-max-points` | int | `1000000` | [GLB] 点云最大点数 |
| `--show-cameras` | bool | `True` | [GLB] 在导出场景中显示相机线框 |
| `--feat-vis-fps` | int | `15` | [FEAT_VIS] 输出视频帧率 |

**Examples:**

```bash
# 🖼️ Auto-process an image
da3 auto path/to/image.jpg --export-dir ./output

# 🎬 Auto-process a video
da3 auto path/to/video.mp4 --fps 2.0 --export-dir ./output

# 🔧 Use backend service
da3 auto path/to/input \
    --export-format mini_npz-glb \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output
```

---

### 🖼️ image - 单图处理（Single Image Processing） <a id="image---single-image-processing"></a>

对单张图像进行相机位姿与深度估计。

**Usage:**

```bash
da3 image IMAGE_PATH [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `IMAGE_PATH` | str | Required | 输入图像文件路径 |
| `--model-dir` | str | Default model | 模型目录路径 |
| `--export-dir` | str | `debug` | 导出目录 |
| `--export-format` | str | `glb` | 导出格式 |
| `--device` | str | `cuda` | 运行设备 |
| `--use-backend` | bool | `False` | 使用后端服务推理 |
| `--backend-url` | str | `http://localhost:8008` | 后端服务 URL |
| `--process-res` | int | `504` | 处理分辨率 |
| `--process-res-method` | str | `upper_bound_resize` | 处理分辨率策略 |
| `--export-feat` | str | `""` | 导出特征层索引（逗号分隔） |
| `--auto-cleanup` | bool | `False` | 自动清理导出目录 |
| `--use-ray-pose` | bool | `False` | 使用 ray-based 位姿估计替代 camera decoder |
| `--ref-view-strategy` | str | `saddle_balanced` | 参考视图选择策略。见 [文档](funcs/ref_view_strategy.md) |
| `--conf-thresh-percentile` | float | `40.0` | [GLB] 置信度阈值分位数 |
| `--num-max-points` | int | `1000000` | [GLB] 最大点数 |
| `--show-cameras` | bool | `True` | [GLB] 显示相机 |
| `--feat-vis-fps` | int | `15` | [FEAT_VIS] 视频帧率 |

**Examples:**

```bash
# ✨ 基础用法
da3 image path/to/image.png --export-dir ./output

# ⚡ 使用后端加速
da3 image path/to/image.png \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output

# 🔍 导出特征可视化
da3 image image.jpg \
    --export-format feat_vis \
    --export-feat "9,19,29,39" \
    --export-dir ./results
```

---

### 🗂️ images - 图像目录处理（Image Directory Processing） <a id="images---image-directory-processing"></a>

对一个图像目录进行批量深度估计。

**Usage:**

```bash
da3 images IMAGES_DIR [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `IMAGES_DIR` | str | Required | 图像目录路径 |
| `--image-extensions` | str | `png,jpg,jpeg` | 处理的图像扩展名（逗号分隔） |
| `--model-dir` | str | Default model | 模型目录路径 |
| `--export-dir` | str | `debug` | 导出目录 |
| `--export-format` | str | `glb` | 导出格式 |
| `--device` | str | `cuda` | 运行设备 |
| `--use-backend` | bool | `False` | 使用后端服务推理 |
| `--backend-url` | str | `http://localhost:8008` | 后端服务 URL |
| `--process-res` | int | `504` | 处理分辨率 |
| `--process-res-method` | str | `upper_bound_resize` | 处理分辨率策略 |
| `--export-feat` | str | `""` | 导出特征层索引 |
| `--auto-cleanup` | bool | `False` | 自动清理导出目录 |
| `--use-ray-pose` | bool | `False` | 使用 ray-based 位姿估计替代 camera decoder |
| `--ref-view-strategy` | str | `saddle_balanced` | 参考视图选择策略。见 [文档](funcs/ref_view_strategy.md) |
| `--conf-thresh-percentile` | float | `40.0` | [GLB] 置信度阈值分位数 |
| `--num-max-points` | int | `1000000` | [GLB] 最大点数 |
| `--show-cameras` | bool | `True` | [GLB] 显示相机 |
| `--feat-vis-fps` | int | `15` | [FEAT_VIS] 视频帧率 |

**Examples:**

```bash
# 📁 处理目录（默认 png/jpg/jpeg）
da3 images ./image_folder --export-dir ./output

# 🎯 自定义扩展名
da3 images ./dataset --image-extensions "png,jpg,webp" --export-dir ./output

# 🔧 使用后端服务
da3 images ./dataset \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output
```

---

### 🎬 video - 视频处理（Video Processing） <a id="video---video-processing"></a>

通过抽帧对视频进行深度估计处理。

**Usage:**

```bash
da3 video VIDEO_PATH [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `VIDEO_PATH` | str | Required | 输入视频文件路径 |
| `--fps` | float | `1.0` | 抽帧采样 FPS |
| `--model-dir` | str | Default model | 模型目录路径 |
| `--export-dir` | str | `debug` | 导出目录 |
| `--export-format` | str | `glb` | 导出格式 |
| `--device` | str | `cuda` | 运行设备 |
| `--use-backend` | bool | `False` | 使用后端服务推理 |
| `--backend-url` | str | `http://localhost:8008` | 后端服务 URL |
| `--process-res` | int | `504` | 处理分辨率 |
| `--process-res-method` | str | `upper_bound_resize` | 处理分辨率策略 |
| `--export-feat` | str | `""` | 导出特征层索引 |
| `--auto-cleanup` | bool | `False` | 自动清理导出目录 |
| `--use-ray-pose` | bool | `False` | 使用 ray-based 位姿估计替代 camera decoder |
| `--ref-view-strategy` | str | `saddle_balanced` | 参考视图选择策略。见 [文档](funcs/ref_view_strategy.md) |
| `--conf-thresh-percentile` | float | `40.0` | [GLB] 置信度阈值分位数 |
| `--num-max-points` | int | `1000000` | [GLB] 最大点数 |
| `--show-cameras` | bool | `True` | [GLB] 显示相机 |
| `--feat-vis-fps` | int | `15` | [FEAT_VIS] 视频帧率 |

**Examples:**

```bash
# ✨ 基础视频处理
da3 video path/to/video.mp4 --export-dir ./output

# ⚙️ 控制抽帧与分辨率
da3 video path/to/video.mp4 \
    --fps 2.0 \
    --process-res 1024 \
    --export-dir ./output

# 🔧 使用后端服务
da3 video path/to/video.mp4 \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output
```

---

### 📐 colmap - COLMAP 数据集处理（COLMAP Dataset Processing） <a id="colmap---colmap-dataset-processing"></a>

在 COLMAP 数据上运行位姿条件（pose-conditioned）深度估计。

**Usage:**

```bash
da3 colmap COLMAP_DIR [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `COLMAP_DIR` | str | Required | COLMAP 目录（包含 `images/` 与 `sparse/`） |
| `--sparse-subdir` | str | `""` | sparse 子目录（如 `sparse/0/` 则填 `"0"`） |
| `--align-to-input-ext-scale` | bool | `True` | 将预测结果对齐到输入外参尺度 |
| `--model-dir` | str | Default model | 模型目录路径 |
| `--export-dir` | str | `debug` | 导出目录 |
| `--export-format` | str | `glb` | 导出格式 |
| `--device` | str | `cuda` | 运行设备 |
| `--use-backend` | bool | `False` | 使用后端服务推理 |
| `--backend-url` | str | `http://localhost:8008` | 后端服务 URL |
| `--process-res` | int | `504` | 处理分辨率 |
| `--process-res-method` | str | `upper_bound_resize` | 处理分辨率策略 |
| `--export-feat` | str | `""` | 导出特征层索引 |
| `--auto-cleanup` | bool | `False` | 自动清理导出目录 |
| `--use-ray-pose` | bool | `False` | 使用 ray-based 位姿估计替代 camera decoder |
| `--ref-view-strategy` | str | `saddle_balanced` | 参考视图选择策略。见 [文档](funcs/ref_view_strategy.md) |
| `--conf-thresh-percentile` | float | `40.0` | [GLB] 置信度阈值分位数 |
| `--num-max-points` | int | `1000000` | [GLB] 最大点数 |
| `--show-cameras` | bool | `True` | [GLB] 显示相机 |
| `--feat-vis-fps` | int | `15` | [FEAT_VIS] 视频帧率 |

**Examples:**

```bash
# 📐 处理 COLMAP 数据集
da3 colmap ./colmap_dataset --export-dir ./output

# 🎯 指定 sparse 子目录并对齐尺度
da3 colmap ./colmap_dataset \
    --sparse-subdir 0 \
    --align-to-input-ext-scale \
    --export-dir ./output

# 🔧 使用后端服务
da3 colmap ./colmap_dataset \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output
```

---

### 🔧 backend - 后端服务（Backend Service） <a id="backend---backend-service"></a>

启动带集成 gallery 的模型后端服务。

**Usage:**

```bash
da3 backend [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--model-dir` | str | Default model | 模型目录路径 |
| `--device` | str | `cuda` | 运行设备 |
| `--host` | str | `127.0.0.1` | 绑定的 Host |
| `--port` | int | `8008` | 绑定端口 |
| `--gallery-dir` | str | Default gallery dir | gallery 目录（可选） |

**Features:**
- 🎯 将模型常驻在 GPU 显存中
- 🔌 提供 REST 推理 API
- 📊 集成仪表盘与状态监控
- 🖼️ 可选的 gallery 浏览器（提供 `--gallery-dir` 时）

**Available Endpoints:**
- 🏠 `/` - 首页
- 📊 `/dashboard` - 仪表盘
- ✅ `/status` - API 状态
- 🖼️ `/gallery/` - gallery 浏览（若开启）

**Examples:**

```bash
# 🚀 基础后端服务
da3 backend --model-dir depth-anything/DA3NESTED-GIANT-LARGE

# 🖼️ 带 gallery 的后端服务
da3 backend \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --device cuda \
    --host 0.0.0.0 \
    --port 8008 \
    --gallery-dir ./workspace

# 💻 使用 CPU
da3 backend --model-dir depth-anything/DA3NESTED-GIANT-LARGE --device cpu
```

---

### 🎨 gradio - Gradio 应用（Gradio Application） <a id="gradio---gradio-application"></a>

启动 Depth Anything 3 的 Gradio 交互式 Web 应用。

**Usage:**

```bash
da3 gradio [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--model-dir` | str | Required | 模型目录路径 |
| `--workspace-dir` | str | Required | workspace 目录路径 |
| `--gallery-dir` | str | Required | gallery 目录路径 |
| `--host` | str | `127.0.0.1` | 绑定的 Host |
| `--port` | int | `7860` | 绑定端口 |
| `--share` | bool | `False` | 创建公网分享链接 |
| `--debug` | bool | `False` | 开启 debug 模式 |
| `--cache-examples` | bool | `False` | 启动时预缓存所有示例场景 |
| `--cache-gs-tag` | str | `""` | 匹配用于高分辨率 + 3DGS 缓存的场景名标签 |

**Examples:**

```bash
# 🎨 基础 Gradio 应用
da3 gradio \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --workspace-dir ./workspace \
    --gallery-dir ./gallery

# 🌐 开启分享与 debug
da3 gradio \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --workspace-dir ./workspace \
    --gallery-dir ./gallery \
    --share \
    --debug

# ⚡ 预缓存示例
da3 gradio \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --workspace-dir ./workspace \
    --gallery-dir ./gallery \
    --cache-examples \
    --cache-gs-tag "dl3dv"
```

---

### 🖼️ gallery - Gallery 服务（Gallery Server） <a id="gallery---gallery-server"></a>

启动独立的 Depth Anything 3 Gallery 服务。

**Usage:**

```bash
da3 gallery [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--gallery-dir` | str | Default gallery dir | gallery 根目录 |
| `--host` | str | `127.0.0.1` | 绑定的 Host |
| `--port` | int | `8007` | 绑定端口 |
| `--open-browser` | bool | `False` | 启动后自动打开浏览器 |

**Note:**
gallery 期望每个场景文件夹至少包含 `scene.glb` 与 `scene.jpg`，并可选包含 `depth_vis/` 或 `gs_video/` 等子目录。

**Examples:**

```bash
# 🖼️ 基础 gallery 服务
da3 gallery --gallery-dir ./workspace

# 🌐 自定义 host 与端口
da3 gallery \
    --gallery-dir ./workspace \
    --host 0.0.0.0 \
    --port 8007

# 🚀 自动打开浏览器
da3 gallery --gallery-dir ./workspace --open-browser
```

---

## ⚙️ 参数详解（Parameter Details） <a id="parameter-details"></a>

### 🔧 通用参数（Common Parameters）

- **`--export-dir`**：输出目录，默认 `debug`
- **`--export-format`**：导出格式，支持用连字符组合多个格式：
  - 📦 `mini_npz`：压缩 NumPy 格式
  - 🎨 `glb`：glTF 二进制格式（3D 场景）
  - 🔍 `feat_vis`：特征可视化
  - 示例：`mini_npz-glb` 同时导出两种格式

- **`--process-res`** / **`--process-res-method`**：控制预处理分辨率策略
  - `process-res`：目标分辨率（默认 504）
  - `process-res-method`：resize 方法（默认 `upper_bound_resize`）

- **`--auto-cleanup`**：删除已有导出目录时不再提示确认

- **`--use-backend`** / **`--backend-url`**：复用已运行的后端服务
  - ⚡ 减少模型加载时间
  - 🌐 支持分布式处理

- **`--export-feat`**：导出中间特征的层索引（逗号分隔）
  - 示例：`"9,19,29,39"`

### 🎨 GLB 导出参数（GLB Export Parameters）

- **`--conf-thresh-percentile`**：自适应置信度阈值下分位数（默认 40.0）
  - 用于过滤低置信度点

- **`--num-max-points`**：点云最大点数（默认 1,000,000）
  - 控制输出体积与性能

- **`--show-cameras`**：在导出场景中显示相机线框（默认 True）

### 🔍 特征可视化参数（Feature Visualization Parameters）

- **`--feat-vis-fps`**：特征可视化输出视频帧率（默认 15）

### 🎬 视频相关参数（Video-Specific Parameters）

- **`--fps`**：视频抽帧采样率（默认 1.0 FPS）
  - 值越大抽帧越多

### 📐 COLMAP 相关参数（COLMAP-Specific Parameters）

- **`--sparse-subdir`**：稀疏重建子目录
  - 空字符串表示使用 `sparse/`
  - `"0"` 表示使用 `sparse/0/`

- **`--align-to-input-ext-scale`**：将预测结果对齐到输入外参尺度（默认 True）
  - 使深度估计与 COLMAP 尺度一致

---

## 💡 使用示例（Usage Examples） <a id="usage-examples"></a>

### 1️⃣ 基础流程（Basic Workflow）

```bash
# 🔧 启动后端服务
da3 backend --model-dir depth-anything/DA3NESTED-GIANT-LARGE --host 0.0.0.0 --port 8008

# 🖼️ 处理单张图像
da3 image image.jpg --export-dir ./output1 --use-backend

# 🎬 处理视频
da3 video video.mp4 --fps 2.0 --export-dir ./output2 --use-backend

# 📐 处理 COLMAP 数据集
da3 colmap ./colmap_data --export-dir ./output3 --use-backend
```

### 2️⃣ 使用 Auto 模式（Using Auto Mode）

```bash
# 🤖 自动检测并处理
da3 auto ./unknown_input --export-dir ./output

# ⚡ 使用后端加速
da3 auto ./unknown_input \
    --use-backend \
    --backend-url http://localhost:8008 \
    --export-dir ./output
```

### 3️⃣ 多格式导出（Multi-Format Export）

```bash
# 📦 同时导出 NPZ 与 GLB
da3 auto assets/examples/SOH \
    --export-format mini_npz-glb \
    --export-dir ./workspace/soh

# 🔍 导出特征可视化
da3 image image.jpg \
    --export-format feat_vis \
    --export-feat "9,19,29,39" \
    --export-dir ./results
```

### 4️⃣ 高级配置（Advanced Configuration）

```bash
# ⚙️ 自定义分辨率与点云密度
da3 image image.jpg \
    --process-res 1024 \
    --num-max-points 2000000 \
    --conf-thresh-percentile 30.0 \
    --export-dir ./output

# 📐 COLMAP 高级选项
da3 colmap ./colmap_data \
    --sparse-subdir 0 \
    --align-to-input-ext-scale \
    --process-res 756 \
    --export-dir ./output
```

### 5️⃣ 批处理流程（Batch Processing Workflow）

```bash
# 🔧 启动后端
da3 backend \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --device cuda \
    --host 0.0.0.0 \
    --port 8008 \
    --gallery-dir ./workspace

# 🔄 批量处理多个场景
for scene in scene1 scene2 scene3; do
    da3 auto ./data/$scene \
        --export-dir ./workspace/$scene \
        --use-backend \
        --auto-cleanup
done

# 🖼️ 启动 gallery 查看结果
da3 gallery --gallery-dir ./workspace --open-browser
```

### 6️⃣ Web 应用（Web Applications）

```bash
# 🎨 启动 Gradio 应用
da3 gradio \
    --model-dir depth-anything/DA3NESTED-GIANT-LARGE \
    --workspace-dir workspace/gradio \
    --gallery-dir ./gallery \
    --host 0.0.0.0 \
    --port 7860 \
    --share
```

### 7️⃣ Transformer 特征可视化（Transformer Feature Visualization）

```bash
# 🔍 导出 Transformer 特征
# 📦 与数值输出组合
da3 auto video.mp4 \
    --export-format glb-feat_vis \
    --export-feat "11,21,31" \
    --export-dir ./debug \
    --use-backend
```

---

## 📝 备注（Notes）

1. **🔧 后端服务**：处理多个任务时推荐使用，以提升效率
2. **💾 GPU 显存**：处理高分辨率输入时注意显存占用
3. **📁 导出目录**：使用 `--auto-cleanup` 可避免删除提示
4. **🔀 格式组合**：可用连字符组合多个导出格式（例如 `mini_npz-glb-feat_vis`）
5. **📐 COLMAP 数据**：确保 COLMAP 目录结构正确（包含 `images/` 与 `sparse/`）

---

## ❓ 获取帮助（Getting Help）

查看任意命令的详细帮助：

```bash
# 📖 查看主帮助
da3 --help

# 🔍 查看具体命令帮助
da3 auto --help
da3 image --help
da3 backend --help
```
