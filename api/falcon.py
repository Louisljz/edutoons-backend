from ai71 import AI71
from dotenv import load_dotenv
import os

load_dotenv()

client = AI71(os.getenv("FALCON_API_KEY"))
response = client.chat.completions.create(
    model="tiiuae/falcon-180B-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)

print(response.choices[0].message.content)
