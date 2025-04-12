from fastapi import FastAPI, Request, Response

import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video

from cloud_run.data_utils import GCSUtil
import os

generator = torch.manual_seed(42)

pipe = StableVideoDiffusionPipeline.from_pretrained("video_model/", device_map="balanced")

app = FastAPI(title='Stable Video Diffusion API', description='API for generating animated videos from still images', version='0.1')
gcs_utils = GCSUtil(bucket_name="edutoons-431101-storage")

@app.get('/health', status_code=200, description='Health check endpoint')
async def health():
    return {"health": "ok"}

@app.post('/predict', description='Animate a still image')
async def predict(request: Request, response: Response):
    print(f"Number of available GPUs: {torch.cuda.device_count()}")
    print("Multi GPU Mapping: ", pipe.hf_device_map)
    try:
        # assume that each project is its own main folder
        # file_id pairs up in images/ and video/clips/
        body = await request.json()
        data = body["instances"][0]
        print('Request Body', data)

        image = load_image(data['image_url'])
        image = image.resize((1024, 576))  # resize to 16:9 aspect ratio
        print('image ready!')

        frames = pipe(image, decode_chunk_size=8, generator=generator).frames[0]

        print('video process complete!')

        video_path = f"{data['file_id']}.mp4"
        export_to_video(frames, video_path, fps=7)
        print('video exported!')

        with open(video_path, 'rb') as video:
            video_blob = gcs_utils.upload_file_obj(file_obj=video,
                                    project_id=data['project_id'],
                                    category='videos/clips')
        os.remove(video_path)

        print('video uploaded to GCS!')

        video_url = gcs_utils.generate_signed_url(blob_name=video_blob)
        return {"video_url": video_url}

    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
