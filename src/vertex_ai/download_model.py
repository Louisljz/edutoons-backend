import torch
from diffusers import StableVideoDiffusionPipeline

pipeline = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16,
    variant="fp16",
)
pipeline.save_pretrained("video_model/")