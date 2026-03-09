# MP4 转 4DGS PLY 序列操作文档

## 1. 功能说明

本项目当前能力：

- 从 MP4 抽帧并执行 DA3 推理
- 从 MP4 抽帧并执行 DA3 推理
- 生成 4DGS 形式的逐帧高斯 PLY 序列（`gs_4d_ply_seq/*.ply`）
- 不输出 MP4 渲染视频

对应命令：

- `da3 mp4-to-ply-video`
- `da3 check-env`


## 2. 环境配置

### 2.1 Python 依赖

推荐在项目根目录执行：

```bash
pip install -e .
```

若只为本功能补齐关键依赖，可执行：

```bash
pip install typer moviepy opencv-python plyfile imageio fastapi uvicorn requests
```

验证：

```bash
da3 check-env
```


## 3. 一键执行 MP4 -> 4DGS PLY 序列

```bash
da3 mp4-to-ply-video INPUT.mp4 \
  --model-dir depth-anything/DA3NESTED-GIANT-LARGE-1.1 \
  --export-dir workspace/mp4_demo \
  --fps 2 \
  --process-res 504 \
  --process-res-method upper_bound_resize
```

常用参数：

- `--fps`：抽帧频率
- `--process-res` / `--process-res-method`：推理分辨率策略
- `--use-backend`：是否使用后端服务


## 4. 输出目录说明

以 `--export-dir workspace/mp4_demo` 为例：

- `workspace/mp4_demo/input_images/`：抽帧结果
- `workspace/mp4_demo/gs_4d_ply_seq/*.ply`：4DGS 高斯序列（逐帧 PLY）


## 5. 当前支持格式说明

当前 `export_format` 支持：

- `gs_4d_ply_seq`：4DGS 逐帧 PLY 序列
- `gs_ply`：单个静态 3DGS PLY
- `gs_video`：3DGS 渲染 MP4（你当前场景不需要）
- `glb`、`mini_npz`、`npz`、`depth_vis`、`feat_vis`、`colmap`

