from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.models import UserInput, VideoInput

from utils.data_utils import GCSUtil
from utils.genai_utils import EduToons
from workers import animate_video_task

from tqdm import tqdm
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

edutoons = EduToons()
db_utils = GCSUtil("edutoons-storage")


@app.post(
    "/create_outline/",
    description="Generate storyboard and images from user-guided content",
)
async def create_outline(input: UserInput):
    storyboard = edutoons.generate_storyboard(input.content,
                                              input.type,
                                              input.duration)
    print('storyboard:', storyboard)

    for scene in tqdm(storyboard, desc="Generating images"):
        image_url = edutoons.text_to_image(scene["prompt"], input.projectId)
        scene["imageUrl"] = image_url
        del scene["prompt"]

    return storyboard


@app.post(
    "/animate_video/", description="Generate animations from storyboard and images"
)
async def animate_video_endpoint(video: VideoInput):
    video_data = [data.model_dump() for data in video.data]
    task = animate_video_task.delay(video_data, video.projectId, video.email)
    print(f"Task submitted with ID: {task.id}")
    return {"message": "Video processing started."}
