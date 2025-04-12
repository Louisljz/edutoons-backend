import requests
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm

load_dotenv()
API_KEY = os.getenv("STABILITY_API_KEY")

response = requests.post(
    f"https://api.stability.ai/v2beta/image-to-video",
    headers={"authorization": f"Bearer {API_KEY}"},
    files={"image": open("./cycling.png", "rb")},
    data={"seed": 0, "cfg_scale": 1.8, "motion_bucket_id": 127},
)

if response.status_code == 200:
    generation_id = response.json().get("id")
else:
    raise Exception(str(response.json()))

print("Generation ID:", generation_id)

# 32ef75db382d5d32fe941386d72ed0ab866c075dd5bb2121bebe3ac81272f7c2
while True:
    response = requests.request(
        "GET",
        f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}",
        headers={
            "accept": "video/*",
            "authorization": f"Bearer {API_KEY}",
        },
    )
    if response.status_code == 202:
        print("Generation in-progress, try again in 10 seconds.")
        for _ in tqdm(range(10), desc="Loading", unit="s"):
            time.sleep(1)
    elif response.status_code == 200:
        print("Generation complete!")
        with open("video.mp4", "wb") as file:
            file.write(response.content)
        break
    else:
        raise Exception(str(response.json()))
