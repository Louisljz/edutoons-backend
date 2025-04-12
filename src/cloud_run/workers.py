from tqdm import tqdm
from dotenv import load_dotenv
from urllib.parse import urlparse
import shutil
import os

from utils.email_utils import send_email_to_user
from utils.data_utils import GCSUtil
from utils.genai_utils import EduToons

from celery import Celery

load_dotenv()


celery_app = Celery(
    __name__,
    broker=os.getenv("REDIS_BROKER_URL"),
    backend=os.getenv("REDIS_BACKEND_URL"),
)

edutoons = EduToons()
db_utils = GCSUtil("edutoons-storage")


@celery_app.task
def animate_video_task(video, projectId, email):
    print('sync changes..')
    print(f"Starting animate_video_task for projectId: {projectId}")
    project_path = os.path.join("temp", projectId)
    video_folder = os.path.join(project_path, "videos")
    audio_folder = os.path.join(project_path, "audio")

    os.makedirs(video_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)

    clips = []

    for scene in tqdm(video, desc="animating each scene", total=len(video)):
        file_path = urlparse(scene['imageUrl']).path
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        video_url = edutoons.image_to_video(scene["imageUrl"], projectId)
        print(f"animated scene: {video_url}")

        video_file = os.path.join(video_folder, file_name + ".webm")
        video = db_utils.download_file(video_url)
        with open(video_file, "wb") as f:
            f.write(video)

        audio_file = os.path.join(audio_folder, file_name + ".mp3")
        edutoons.text_to_speech(scene['script'], audio_file)

        video_clip = edutoons.create_video_clip(video_file, audio_file)
        clips.append(video_clip)

    final_video_path = os.path.join(project_path, f"{projectId}_final_video.webm")
    edutoons.stitch_video(clips, final_video_path)

    with open(final_video_path, "rb") as video_file:
        video_blob = db_utils.upload_final_video(video_file, projectId)

    video_url = db_utils.generate_signed_url(video_blob)
    print(f"final video url: {video_url}")

    shutil.rmtree(project_path)

    send_email_to_user(video_url, projectId, email)
