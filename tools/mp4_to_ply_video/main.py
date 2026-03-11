
import os
import sys
import typer
import torch
import numpy as np
from typing import Optional

# Ensure we can import from src
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from depth_anything_3.services.input_handlers import VideoHandler, InputHandler
from depth_anything_3.utils.constants import DEFAULT_MODEL, DEFAULT_EXPORT_DIR
from depth_anything_3.specs import Prediction, Gaussians
from depth_anything_3.utils.gsply_helpers import save_gaussian_ply
from depth_anything_3.api import DepthAnything3

app = typer.Typer(help="MP4 to PLY Video Converter")

def save_gs_ply_seq(prediction: Prediction, export_dir: str):
    """Save 4DGS PLY sequence"""
    gs_world = prediction.gaussians
    if gs_world is None:
        print("No Gaussians found in prediction. Make sure infer_gs=True.")
        return

    out_dir = os.path.join(export_dir, "gs_4d_ply_seq")
    os.makedirs(out_dir, exist_ok=True)
    
    num_views = prediction.depth.shape[0]
    # Assuming gaussians are concatenated per view
    # shape: (1, total_gaussians, ...)
    total_gaussians = gs_world.means.shape[1]
    gaussians_per_view = total_gaussians // num_views
    
    pred_depth = torch.from_numpy(prediction.depth).unsqueeze(-1).to(gs_world.means.device)  # N, H, W, 1
    
    print(f"Exporting {num_views} frames to {out_dir}...")
    
    for i in range(num_views):
        save_path = os.path.join(out_dir, f"{i:06d}.ply")
        
        start_idx = i * gaussians_per_view
        end_idx = (i + 1) * gaussians_per_view
        
        # Slice gaussians for this view
        # Keep batch dim 1
        sliced_gs = Gaussians(
            means=gs_world.means[:, start_idx:end_idx],
            scales=gs_world.scales[:, start_idx:end_idx],
            rotations=gs_world.rotations[:, start_idx:end_idx],
            harmonics=gs_world.harmonics[:, start_idx:end_idx],
            opacities=gs_world.opacities[:, start_idx:end_idx],
        )
        
        # Slice depth for this view
        ctx_depth_i = pred_depth[i : i + 1] # (1, H, W, 1)
        
        save_gaussian_ply(
            gaussians=sliced_gs,
            save_path=save_path,
            ctx_depth=ctx_depth_i,
            shift_and_scale=False,
            save_sh_dc_only=True,
            gs_views_interval=1,
            inv_opacity=True,
            prune_by_depth_percent=0.9,
            prune_border_gs=True,
            match_3dgs_mcmc_dev=False,
        )
    
    print(f"Saved {num_views} PLY files.")

@app.command()
def main(
    video_path: str = typer.Argument(..., help="Path to input video file"),
    fps: float = typer.Option(1.0, help="Sampling FPS for frame extraction"),
    model_dir: str = typer.Option(DEFAULT_MODEL, help="Model directory path"),
    export_dir: str = typer.Option(DEFAULT_EXPORT_DIR, help="Export directory"),
    device: str = typer.Option("cuda", help="Device to use"),
    process_res: int = typer.Option(504, help="Processing resolution"),
    process_res_method: str = typer.Option("upper_bound_resize", help="Processing resolution method"),
    auto_cleanup: bool = typer.Option(False, help="Automatically clean export directory"),
    infer_gs: bool = typer.Option(True, help="Enable Gaussian Splatting inference"),
    # Advanced options
    use_ray_pose: bool = typer.Option(False, help="Use ray-based pose estimation"),
    ref_view_strategy: str = typer.Option("saddle_balanced", help="Reference view selection strategy"),
):
    """
    Convert MP4 video to 4D Gaussian Splatting PLY sequence.
    """
    # Handle export directory
    export_dir = InputHandler.handle_export_dir(export_dir, auto_cleanup)
    
    # Process video input (extract frames)
    image_files = VideoHandler.process(video_path, export_dir, fps)
    
    # Load model
    print(f"Loading model from {model_dir}...")
    try:
        model = DepthAnything3.from_pretrained(model_dir).to(device)
    except Exception as e:
        print(f"Error loading model: {e}")
        raise typer.Exit(1)
    
    # Run inference
    print("Running inference...")
    try:
        prediction = model.inference(
            image=image_files,
            process_res=process_res,
            process_res_method=process_res_method,
            infer_gs=infer_gs,
            use_ray_pose=use_ray_pose,
            ref_view_strategy=ref_view_strategy,
        )
    except Exception as e:
        print(f"Error running inference: {e}")
        raise typer.Exit(1)
    
    # Export
    print("Exporting results...")
    save_gs_ply_seq(prediction, export_dir)
    print("Done.")

if __name__ == "__main__":
    app()
