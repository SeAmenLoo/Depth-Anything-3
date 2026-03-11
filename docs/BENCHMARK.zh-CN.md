# 📏 视觉几何基准评测（Visual Geometry Benchmark）

本文档提供在 Depth Anything 3 上运行基准评测（benchmark evaluation）的完整说明。

## ✨ 亮点（Highlights）

- 🗂️ **多样且具有挑战的数据集**：包含 5 个数据集（ETH3D、7Scenes、ScanNet++、HiRoom、DTU），覆盖从物体到室内外场景。部分数据集进行了重新标定以提升精度（细节见 [ScanNet++](#scannet)）。所有预处理后的数据集已上传至 [depth-anything/DA3-BENCH](https://huggingface.co/datasets/depth-anything/DA3-BENCH)。
- 🔧 **鲁棒的评测流水线**：标准化流程包含基于 RANSAC 的位姿对齐以获得更一致的坐标系，以及 TSDF 融合用于直接反映深度的 3D 一致性。
- 📊 **标准化指标**：性能使用经典指标衡量：位姿精度使用 AUC；重建质量使用 F1-score 与 Chamfer Distance。

---

## 📑 目录（Table of Contents）

- [🚀 快速开始](#quick-start)
- [📥 数据集下载](#dataset-download)
- [⚙️ 评测流程](#evaluation-pipeline)
- [🔧 配置](#configuration)
- [📊 指标](#metrics)
- [🗂️ 数据集详情](#dataset-details)
- [💻 命令参考](#command-reference)
- [🔍 故障排查](#troubleshooting)

---

## 🚀 快速开始（Quick Start） <a id="quick-start"></a>

### 1. 下载基准数据（Download Benchmark Data）

> 💡 **Note:** 先安装 HuggingFace CLI：`pip install -U huggingface_hub[cli]`
>
> 🌐 **Mirror:** 如果下载较慢，可尝试：`export HF_ENDPOINT=https://hf-mirror.com`

```bash
cd da3_release

# 创建目录并从 HuggingFace 下载
mkdir -p workspace/benchmark_dataset
hf download depth-anything/DA3-BENCH \
    --local-dir workspace/benchmark_dataset \
    --repo-type dataset

# 解压全部数据集
cd workspace/benchmark_dataset
for f in *.zip; do unzip -q "$f"; done
```

### 2. 运行评测（Run Evaluation）

```bash
# 设置模型（默认：depth-anything/DA3-GIANT）
MODEL=depth-anything/DA3-GIANT

# 完整评测（全部数据集、全部模式）
python -m depth_anything_3.bench.evaluator model.path=$MODEL

# 查看结果
python -m depth_anything_3.bench.evaluator eval.print_only=true
```

---

## 📥 数据集下载（Dataset Download） <a id="dataset-download"></a>

所有基准数据集均托管在 HuggingFace：**[depth-anything/DA3-BENCH](https://huggingface.co/datasets/depth-anything/DA3-BENCH)**

| Dataset | File | Size | Description |
|---------|------|------|-------------|
| ETH3D | `eth3d.zip` | ~14.1 GB | 高分辨率多视图立体（室内/室外） |
| ScanNet++ | `scannetpp.zip` | ~10.1 GB | 高质量室内 RGB-D 场景 |
| DTU-49 | `dtu.zip` | ~8.3 GB | 多视图立体基准（22 个场景 × 49 视图） |
| 7Scenes | `7scenes.zip` | ~3.3 GB | 室内 RGB-D 重定位数据集 |
| DTU-64 | `dtu64.zip` | ~1.7 GB | 用于位姿评测的 DTU 子集（13 个场景 × 64 视图） |
| HiRoom | `hiroom.zip` | ~0.7 GB | 高分辨率室内房间 |

### 下载选项（Download Options）

**Option 1: Download All (Recommended)**
```bash
hf download depth-anything/DA3-BENCH \
    --local-dir workspace/benchmark_dataset \
    --repo-type dataset
```

**Option 2: Download Specific Dataset**
```bash
# 仅下载 HiRoom
hf download depth-anything/DA3-BENCH hiroom.zip \
    --local-dir workspace/benchmark_dataset \
    --repo-type dataset
```

**Option 3: Manual Download**

访问 [https://huggingface.co/datasets/depth-anything/DA3-BENCH](https://huggingface.co/datasets/depth-anything/DA3-BENCH) 并手动下载 zip 文件。

### 解压数据集（Extract Datasets）

```bash
cd workspace/benchmark_dataset

# 解压全部
for f in *.zip; do unzip -q "$f"; done

# 或解压指定数据集
unzip hiroom.zip
```

### 预期目录结构（Expected Directory Structure）

解压后目录结构应类似：
```
workspace/benchmark_dataset/
├── eth3d/
│   ├── courtyard/
│   ├── electro/
│   └── ...
├── 7scenes/
│   └── 7Scenes/
│       ├── chess/
│       └── ...
├── scannetpp/
│   ├── 09c1414f1b/
│   └── ...
├── hiroom/
│   ├── data/
│   ├── fused_pcd/
│   └── selected_scene_list_val.txt
├── dtu/
│   ├── Rectified/
│   ├── Cameras/
│   ├── Points/
│   ├── SampleSet/
│   └── depth_raw/
└── dtu64/
    ├── Cameras/
    ├── scan105/
    └── ...
```

---

## ⚙️ 评测流程（Evaluation Pipeline） <a id="evaluation-pipeline"></a>

### 评测模式（Evaluation Modes）

| Mode | Description | Metrics |
|------|-------------|---------|
| `pose` | 相机位姿估计 | AUC@3°, AUC@30° |
| `recon_unposed` | 使用 **预测** 位姿进行 3D 重建 | F-score, Overall |
| `recon_posed` | 使用 **GT** 位姿进行 3D 重建 | F-score, Overall |

### 基础用法（Basic Usage）

```bash
cd da3_release
MODEL=depth-anything/DA3-GIANT

# 完整评测（推理 + 评测 + 打印结果）
python -m depth_anything_3.bench.evaluator model.path=$MODEL

# 跳过推理，仅评测已有预测结果
python -m depth_anything_3.bench.evaluator eval.eval_only=true

# 仅打印已保存的指标
python -m depth_anything_3.bench.evaluator eval.print_only=true
```

### 选择性评测（Selective Evaluation）

```bash
# 评测指定数据集
python -m depth_anything_3.bench.evaluator model.path=$MODEL eval.datasets=[hiroom]

# 评测指定模式
python -m depth_anything_3.bench.evaluator model.path=$MODEL eval.modes=[pose,recon_unposed]

# 组合选择数据集与模式
python -m depth_anything_3.bench.evaluator model.path=$MODEL \
    eval.datasets=[hiroom] \
    eval.modes=[pose]
```

### 🖥️ Multi-GPU Inference

评测器会自动将推理分发到可用 GPU 上：

```bash
# 使用 4 张 GPU
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m depth_anything_3.bench.evaluator model.path=$MODEL

# 使用全部可用 GPU（默认）
python -m depth_anything_3.bench.evaluator model.path=$MODEL

# 单 GPU
CUDA_VISIBLE_DEVICES=0 python -m depth_anything_3.bench.evaluator model.path=$MODEL
```

---

## 🔧 配置（Configuration） <a id="configuration"></a>

### 配置文件（Config File）

默认配置：`src/depth_anything_3/bench/configs/eval_bench.yaml`

```yaml
# 模型路径
model:
  path: depth-anything/DA3-GIANT

# Workspace 目录
workspace:
  work_dir: ./workspace/evaluation

# 评测设置
eval:
  datasets: [eth3d, 7scenes, scannetpp, hiroom, dtu, dtu64]
  modes: [pose, recon_unposed, recon_posed]
  max_frames: 100      # Max frames per scene (-1 = no limit)
  scenes: null         # Specific scenes (null = all)

# 推理设置
inference:
  num_fusion_workers: 4
  debug: false
```

### 输出结构（Output Structure）

```
workspace/evaluation/
├── model_results/              # Inference outputs
│   ├── eth3d/
│   │   └── {scene}/
│   │       ├── unposed/       # Predictions for recon_unposed
│   │       └── posed/         # Predictions for recon_posed
│   ├── 7scenes/
│   ├── scannetpp/
│   ├── hiroom/
│   ├── dtu/
│   └── dtu64/
└── metric_results/             # Evaluation metrics (JSON)
    ├── eth3d_pose.json
    ├── eth3d_recon_unposed.json
    ├── eth3d_recon_posed.json
    └── ...
```

---

## 📊 指标（Metrics） <a id="metrics"></a>

### 🎯 Pose Estimation

| Metric | Description |
|--------|-------------|
| **Auc3** | 角误差阈值 3° 下的 AUC |
| **Auc30** | 角误差阈值 30° 下的 AUC |

### 🏗️ 3D Reconstruction

| Metric | Description | Note |
|--------|-------------|------|
| **F-score** | Precision 与 Recall 的调和平均 | 越高越好 |
| **Overall** | (Accuracy + Completeness) / 2 | 越低越好（以米/mm 计的误差） |

> **Note:** DTU 的 Overall 以毫米为单位；其他数据集以米为单位。

### DA3-GIANT 的预期结果（Expected Results for DA3-GIANT）

如果环境配置正确，评测 **DA3-GIANT** 时应得到类似如下结果：

```
========================================================
📊 SUMMARY
========================================================

🎯 POSE ESTIMATION
---------------------------------------------------------------------------------------
Metric         Avg         HiRoom      ETH3D       DTU-64      7Scenes     ScanNet++
---------------------------------------------------------------------------------------
Auc3           0.6705      0.8030      0.4872      0.9408      0.2744      0.8470
Auc30          0.9436      0.9592      0.9153      0.9939      0.8668      0.9827

🏗️  RECON_UNPOSED (Pred Pose)
---------------------------------------------------------------------------------------
Metric         Avg*        HiRoom      ETH3D       DTU         7Scenes     ScanNet++
---------------------------------------------------------------------------------------
F-score        0.7345      0.8629      0.7876      N/A         0.5043      0.7831
Overall        0.1682      0.0457      0.4366      1.7927      0.1230      0.0676

🏗️  RECON_POSED (GT Pose)
---------------------------------------------------------------------------------------
Metric         Avg*        HiRoom      ETH3D       DTU         7Scenes     ScanNet++
---------------------------------------------------------------------------------------
F-score        0.7978      0.9546      0.8685      N/A         0.5635      0.8045
Overall        0.1408      0.0213      0.3679      1.7488      0.1092      0.0649

* Avg F-score / Overall = average over HiRoom, ETH3D, 7Scenes, ScanNet++ (4 datasets)
```

---

## 🗂️ 数据集详情（Dataset Details） <a id="dataset-details"></a>

### ETH3D

带激光扫描真值的高分辨率多视图立体基准。

- **Scenes:** 11（courtyard、electro、kicker、pipes、relief、delivery_area、facade、office、playground、relief_2、terrains）
- **Resolution:** 可变（高分辨率 DSLR 图像）
- **GT:** 激光扫描网格 + 深度图

> **⚠️ Image Filtering:** 为保证评测稳定性，一些具有异常相机旋转的图像会被过滤。详情见 `constants.py` 中的 `ETH3D_FILTER_KEYS`。

### 7Scenes

用于相机重定位的室内 RGB-D 数据集。

- **Scenes:** 7（chess、fire、heads、office、pumpkin、redkitchen、stairs）
- **Resolution:** 640×480
- **GT:** 来自 KinectFusion 的位姿；由 TSDF 融合得到的网格

### ScanNet++

带密集标注的高质量室内 RGB-D 数据集。

- **Scenes:** 20 个验证场景
- **Resolution:** 768×1024（去畸变后）
- **GT:** 由 FARO 扫描仪获取的高质量网格

> **⚠️ Camera Pose Re-calibration:** ScanNet++ 的默认位姿常因 iPhone 采集时的运动模糊与纹理不足而不够准确。我们使用如下改进重新运行了 COLMAP：
> - **Frame filtering:** 抽帧时移除模糊图像
> - **Fisheye calibration:** 联合标定鱼眼相机以获得更大 FOV 与更高精度
> - **Exhaustive matching:** 使用 COLMAP 的 exhaustive matcher 与 mapper 获取更可靠的位姿（每个场景可能需要数天，但对质量必要）
> - 所有处理后的场景可在 [haotongl/scannetpp_zipnerf](https://huggingface.co/datasets/haotongl/scannetpp_zipnerf) 获取

### HiRoom

包含高分辨率 RGB-D 数据的室内房间场景。

- **Scenes:** 24 个验证场景
- **GT:** 融合后的点云

### DTU-49 (Reconstruction Only)

遵循 MVSNet 评测协议的多视图立体基准。

- **Scenes:** 22 个评测场景
- **Views:** 每个场景 49 张图像
- **GT:** 带观测 mask 的激光扫描点云
- **Metrics:** 仅 Overall（以 mm 计的 accuracy + completeness）

### DTU-64 (Pose Only)

用于位姿估计评测的 DTU 子集。

- **Scenes:** 13 个场景
- **Views:** 每个场景 64 张图像
- **Metrics:** AUC@3°、AUC@30°

> **Why two DTU settings?**
> - **DTU-64**（pose）：更多视图，位姿估计更具挑战
> - **DTU-49**（recon）：标准 MVSNet 协议，便于与其他 MVS 方法公平对比

---

## 💻 命令参考（Command Reference） <a id="command-reference"></a>

```
python -m depth_anything_3.bench.evaluator [OPTIONS] [KEY=VALUE ...]

Configuration:
  --config PATH                      Config YAML file (default: bench/configs/eval_bench.yaml)

Config Overrides (using dotlist notation):
  model.path=VALUE                   Model path or HuggingFace ID
  workspace.work_dir=VALUE           Working directory for outputs
  eval.datasets=[dataset1,dataset2]  Datasets to evaluate (eth3d,7scenes,scannetpp,hiroom,dtu,dtu64)
  eval.modes=[mode1,mode2]           Evaluation modes (pose,recon_unposed,recon_posed)
  eval.scenes=[scene1,scene2]        Specific scenes to evaluate (null=all)
  eval.max_frames=VALUE              Max frames per scene (-1=no limit, default: 100)
  eval.ref_view_strategy=VALUE       Reference view strategy (default: first)
  eval.eval_only=VALUE               Only run evaluation (skip inference) (true/false)
  eval.print_only=VALUE              Only print saved metrics (true/false)
  inference.num_fusion_workers=VALUE Number of parallel workers (default: 4)
  inference.debug=VALUE              Enable debug mode (true/false)

Special Flags:
  --help, -h                         Show this help message

Multi-GPU:
  Use CUDA_VISIBLE_DEVICES to specify GPUs (auto-detected and distributed)
```

### 示例（Examples）

```bash
MODEL=depth-anything/DA3-GIANT

# 完整评测
python -m depth_anything_3.bench.evaluator model.path=$MODEL

# 仅在 HiRoom 上快速测试
python -m depth_anything_3.bench.evaluator \
    model.path=$MODEL \
    eval.datasets=[hiroom] \
    eval.modes=[pose]

# 仅位姿评测（全部 5 个 pose 数据集）
python -m depth_anything_3.bench.evaluator \
    model.path=$MODEL \
    eval.datasets=[eth3d,7scenes,scannetpp,hiroom,dtu64] \
    eval.modes=[pose]

# 仅重建评测（全部 5 个 recon 数据集）
python -m depth_anything_3.bench.evaluator \
    model.path=$MODEL \
    eval.datasets=[eth3d,7scenes,scannetpp,hiroom,dtu] \
    eval.modes=[recon_unposed,recon_posed]

# Debug 指定场景
python -m depth_anything_3.bench.evaluator \
    model.path=$MODEL \
    eval.datasets=[eth3d] \
    eval.scenes=[courtyard] \
    inference.debug=true

# 不重新推理，直接重新评测
python -m depth_anything_3.bench.evaluator eval.eval_only=true

# 仅查看结果
python -m depth_anything_3.bench.evaluator eval.print_only=true
```

---

## 🔍 故障排查（Troubleshooting） <a id="troubleshooting"></a>

### 数据路径问题（Data Path Issues）

请确保 `src/depth_anything_3/utils/constants.py` 中的数据集路径正确：

```python
# Default paths (relative to project root)
ETH3D_EVAL_DATA_ROOT = "workspace/benchmark_dataset/eth3d"
SEVENSCENES_EVAL_DATA_ROOT = "workspace/benchmark_dataset/7scenes"
SCANNETPP_EVAL_DATA_ROOT = "workspace/benchmark_dataset/scannetpp"
HIROOM_EVAL_DATA_ROOT = "workspace/benchmark_dataset/hiroom/data"
DTU_EVAL_DATA_ROOT = "workspace/benchmark_dataset/dtu"
DTU64_EVAL_DATA_ROOT = "workspace/benchmark_dataset/dtu64"
```

---

## 📝 引用（Citation）

如果你觉得该基准评测有帮助，请引用：

```
@article{depthanything3,
  title={Depth Anything 3: Recovering the visual space from any views},
  author={Haotong Lin and Sili Chen and Jun Hao Liew and Donny Y. Chen and Zhenyu Li and Guang Shi and Jiashi Feng and Bingyi Kang},
  journal={arXiv preprint arXiv:2511.10647},
  year={2025}
}
```

同时请引用你所使用的各数据集的原始论文。

---

## 📄 许可证（License）

基准数据集仅供科研用途。使用者必须遵守每个数据集的原始许可证：

- **ETH3D:** [https://www.eth3d.net/](https://www.eth3d.net/)
- **7Scenes:** [Microsoft Research](https://www.microsoft.com/en-us/research/project/rgb-d-dataset-7-scenes/)
- **ScanNet++:** [http://www.scan-net.org/](http://www.scan-net.org/)
- **DTU:** [https://roboimagedata.compute.dtu.dk/](https://roboimagedata.compute.dtu.dk/)
- **HiRoom:** [SVLightVerse](https://jerrypiglet.github.io/SVLightVerse/)

