import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()
API_KEY = os.getenv("STABILITY_API_KEY")

start = time.time()
response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/core",
    headers={"authorization": f"Bearer {API_KEY}", "accept": "image/*"},
    files={"none": ""},
    data={
        "prompt": "a person cycling on the park",
        "aspect_ratio": "16:9",
        "style_preset": "photographic",
        "output_format": "png",
    },
)
end = time.time()
print(f"Time taken: {round(end - start, 1)} s")
print("Image generation complete!")

if response.status_code == 200:
    with open("./stable-image.png", "wb") as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))
