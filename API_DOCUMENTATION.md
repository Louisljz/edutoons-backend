# EduToons API Documentation

**EduToons** - "Cartoons that Teach!"

EduToons is a fun and engaging educational platform for kids, blending the magic of cartoons with interactive learning. Through animated video lessons, playful quizzes, and insightful reports, EduToons makes learning an adventure, helping children explore and understand concepts in an entertaining and memorable way.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Cloud Run API Service](#cloud-run-api-service)
- [Vertex AI Service](#vertex-ai-service)
- [AI Model APIs](#ai-model-apis)
- [Core Classes and Utilities](#core-classes-and-utilities)
- [Data Models](#data-models)
- [Background Workers](#background-workers)
- [Setup and Configuration](#setup-and-configuration)

## Architecture Overview

The EduToons platform consists of three main components:

1. **Cloud Run Service** (`src/cloud_run/`): Main FastAPI application handling user requests
2. **Vertex AI Service** (`src/vertex_ai/`): Specialized service for video generation using Stable Video Diffusion
3. **AI Model APIs** (`api/`): Standalone scripts for various AI model integrations

## Cloud Run API Service

### Main Application (`src/cloud_run/app.py`)

The main FastAPI application provides endpoints for content generation and video processing.

#### Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

#### Public Endpoints

##### 1. Create Outline Endpoint

**POST** `/create_outline/`

Generates storyboard and images from user-guided content.

**Request Body:**
```json
{
    "content": "string",      // Educational content to convert
    "type": "string",         // Type of video (e.g., "educational", "tutorial")
    "duration": "string",     // Desired video duration
    "projectId": "string"     // Unique project identifier
}
```

**Response:**
```json
[
    {
        "script": "string",     // Narration script for the scene
        "imageUrl": "string"    // Generated image URL for the scene
    }
]
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/create_outline/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Learn about photosynthesis in plants",
    "type": "educational",
    "duration": "2 minutes",
    "projectId": "proj-123"
  }'
```

##### 2. Animate Video Endpoint

**POST** `/animate_video/`

Generates animations from storyboard and images using background processing.

**Request Body:**
```json
{
    "data": [
        {
            "imageUrl": "string",   // URL of the image to animate
            "script": "string"      // Narration script for the scene
        }
    ],
    "projectId": "string",      // Unique project identifier
    "email": "string"           // User email for completion notification
}
```

**Response:**
```json
{
    "message": "Video processing started."
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/animate_video/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
        {
            "imageUrl": "https://storage.googleapis.com/bucket/image.webp",
            "script": "Plants use sunlight to make food through photosynthesis."
        }
    ],
    "projectId": "proj-123",
    "email": "user@example.com"
  }'
```

## Vertex AI Service

### Video Generation API (`src/vertex_ai/app.py`)

Specialized FastAPI service for animating still images using Stable Video Diffusion.

#### Public Endpoints

##### 1. Health Check

**GET** `/health`

Simple health check endpoint.

**Response:**
```json
{
    "health": "ok"
}
```

##### 2. Predict Video Animation

**POST** `/predict`

Animates a still image to create video content.

**Request Body:**
```json
{
    "instances": [
        {
            "image_url": "string",      // URL of the image to animate
            "file_id": "string",        // Unique file identifier
            "project_id": "string"      // Project identifier
        }
    ]
}
```

**Response:**
```json
{
    "video_url": "string"       // URL of the generated video
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
        {
            "image_url": "https://example.com/image.jpg",
            "file_id": "file-123",
            "project_id": "proj-123"
        }
    ]
  }'
```

## AI Model APIs

### 1. Falcon Language Model (`api/falcon.py`)

Integrates with AI71's Falcon-180B-chat model for text generation.

```python
from ai71 import AI71
import os

client = AI71(os.getenv("FALCON_API_KEY"))
response = client.chat.completions.create(
    model="tiiuae/falcon-180B-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
```

### 2. Stable Image Generation (`api/stable-image.py`)

Generates images using Stability AI's image generation API.

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/core",
    headers={"authorization": f"Bearer {API_KEY}", "accept": "image/*"},
    data={
        "prompt": "a person cycling on the park",
        "aspect_ratio": "16:9",
        "style_preset": "photographic",
        "output_format": "png",
    },
)
```

### 3. Stable Video Generation (`api/stable-video.py`)

Converts images to videos using Stability AI's video generation API.

```python
import requests

# Generate video from image
response = requests.post(
    "https://api.stability.ai/v2beta/image-to-video",
    headers={"authorization": f"Bearer {API_KEY}"},
    files={"image": open("./cycling.png", "rb")},
    data={"seed": 0, "cfg_scale": 1.8, "motion_bucket_id": 127},
)
```

## Core Classes and Utilities

### EduToons Class (`src/cloud_run/utils/genai_utils.py`)

Main utility class that orchestrates various AI services for content generation.

#### Constructor

```python
class EduToons:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
```

#### Methods

##### `generate_storyboard(content: str, video_type: str, duration: str) -> list`

Generates a storyboard with scenes containing prompts and scripts.

**Parameters:**
- `content`: Educational content to convert into a storyboard
- `video_type`: Type of video (e.g., "educational", "tutorial")
- `duration`: Desired video duration

**Returns:** List of dictionaries with `prompt` and `script` keys

**Example:**
```python
edutoons = EduToons()
storyboard = edutoons.generate_storyboard(
    content="Learn about solar system",
    video_type="educational",
    duration="3 minutes"
)
```

##### `text_to_image(prompt: str, project_id: str) -> str`

Converts text prompt to image using external API.

**Parameters:**
- `prompt`: Description of the image to generate
- `project_id`: Project identifier for organization

**Returns:** URL of the generated image

##### `image_to_video(image_url: str, project_id: str) -> str`

Converts a static image to animated video.

**Parameters:**
- `image_url`: URL of the source image
- `project_id`: Project identifier

**Returns:** URL of the generated video

##### `text_to_speech(script: str, audio_path: str) -> None`

Converts text script to speech audio using ElevenLabs.

**Parameters:**
- `script`: Text to convert to speech
- `audio_path`: Local path to save the audio file

**Example:**
```python
edutoons.text_to_speech(
    script="Welcome to our lesson on photosynthesis",
    audio_path="./audio/scene1.mp3"
)
```

##### `create_video_clip(video_path: str, audio_path: str) -> VideoFileClip`

Combines video and audio into a synchronized clip.

**Parameters:**
- `video_path`: Path to video file
- `audio_path`: Path to audio file

**Returns:** MoviePy VideoFileClip object

##### `stitch_video(clips: list, video_path: str) -> None`

Combines multiple video clips into a final video.

**Parameters:**
- `clips`: List of VideoFileClip objects
- `video_path`: Output path for the final video

### GCSUtil Class (`src/cloud_run/utils/data_utils.py`)

Utility class for Google Cloud Storage operations.

#### Constructor

```python
class GCSUtil:
    def __init__(self, bucket_name: str):
        self.client = storage.Client.from_service_account_json(
            "config/edutoons-service-account.json"
        )
        self.bucket = self.client.bucket(bucket_name)
```

#### Methods

##### `upload_image(image: PIL.Image, project_id: str) -> str`

Uploads an image to Google Cloud Storage.

**Parameters:**
- `image`: PIL Image object
- `project_id`: Project identifier for organization

**Returns:** Blob name of the uploaded image

##### `upload_final_video(video: file-like, project_id: str) -> str`

Uploads a final video to Google Cloud Storage.

**Parameters:**
- `video`: File-like object containing video data
- `project_id`: Project identifier

**Returns:** Blob name of the uploaded video

##### `generate_signed_url(blob_name: str, expiration: int = 10) -> str`

Generates a signed URL for accessing a file.

**Parameters:**
- `blob_name`: Name of the blob in the bucket
- `expiration`: URL expiration time in hours (default: 10)

**Returns:** Signed URL string

**Example:**
```python
gcs_util = GCSUtil("edutoons-storage")
url = gcs_util.generate_signed_url("project-123/final_video.mp4")
```

##### `download_file(signed_url: str) -> bytes`

Downloads a file from a signed URL.

**Parameters:**
- `signed_url`: The signed URL to download from

**Returns:** File content as bytes

### Email Utilities (`src/cloud_run/utils/email_utils.py`)

#### `send_email_to_user(video_url: str, project_id: str, recipient_email: str) -> None`

Sends completion notification email to user with video link.

**Parameters:**
- `video_url`: URL of the completed video
- `project_id`: Project identifier
- `recipient_email`: User's email address

**Example:**
```python
send_email_to_user(
    video_url="https://storage.googleapis.com/bucket/video.mp4",
    project_id="proj-123",
    recipient_email="user@example.com"
)
```

## Data Models

### Pydantic Models (`src/cloud_run/config/models.py`)

#### UserInput

```python
class UserInput(BaseModel):
    content: str        # Educational content to process
    type: str          # Type of video to create
    duration: str      # Desired duration
    projectId: str     # Unique project identifier
```

#### VideoData

```python
class VideoData(BaseModel):
    imageUrl: str      # URL of the scene image
    script: str        # Narration script for the scene
```

#### VideoInput

```python
class VideoInput(BaseModel):
    data: List[VideoData]   # List of video scenes
    projectId: str          # Project identifier
    email: str             # User email for notifications
```

## Background Workers

### Celery Worker (`src/cloud_run/workers.py`)

#### `animate_video_task(video: list, project_id: str, email: str)`

Background task that processes video animation asynchronously.

**Parameters:**
- `video`: List of video scene data
- `project_id`: Project identifier
- `email`: User email for completion notification

**Process:**
1. Creates temporary directories for video and audio files
2. Downloads and processes each scene image
3. Generates audio narration for each scene
4. Creates video clips with synchronized audio
5. Combines all clips into final video
6. Uploads final video to cloud storage
7. Sends completion email to user
8. Cleans up temporary files

**Example Usage:**
```python
from workers import animate_video_task

task = animate_video_task.delay(
    video_data,
    "proj-123",
    "user@example.com"
)
print(f"Task submitted with ID: {task.id}")
```

## Setup and Configuration

### Environment Variables

The following environment variables are required:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
FALCON_API_KEY=your_falcon_api_key
STABILITY_API_KEY=your_stability_api_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Email Configuration
SENDER_EMAIL=noreply@edutoons.com

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://edutoons.com

# Redis Configuration
REDIS_BROKER_URL=redis://localhost:6379/0
REDIS_BACKEND_URL=redis://localhost:6379/0

# External API URLs
STABLE_API_URL=https://your-stable-api-url.com
```

### Dependencies

#### Cloud Run Service
```txt
fastapi[standard]
celery
flower
redis
google-cloud-storage
sendgrid
openai
moviepy
elevenlabs
```

#### Vertex AI Service
```txt
python-dotenv
diffusers
accelerate
opencv-python
fastapi
google-cloud-storage
```

### Docker Deployment

Both services include Dockerfile configurations for containerized deployment:

#### Cloud Run
- Multi-stage build with Python 3.11
- Production-ready with gunicorn
- Health checks included

#### Vertex AI
- GPU-optimized container
- Model caching for faster inference
- Automatic model downloading

### Service Account Configuration

Both services require Google Cloud service account credentials:
- `src/cloud_run/config/edutoons-service-account.json`
- `src/vertex_ai/edutoons-service-account.json`

### Testing

#### Vertex AI Endpoint Testing

Use `src/vertex_ai/test_endpoint.py` to test deployed Vertex AI endpoints:

```python
from google.cloud import aiplatform

# Configure project settings
project_id = "your-project-id"
endpoint_id = "your-endpoint-id"
location = "us-central1"

# Make prediction
endpoint = aiplatform.Endpoint(f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}")
prediction = endpoint.predict(instances=data['instances'])
```

## Error Handling

All APIs include comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Missing or invalid API keys
- **500 Internal Server Error**: Processing failures
- **503 Service Unavailable**: External API failures

Errors are logged with detailed information for debugging and monitoring.

## Rate Limiting

External API calls are managed to respect rate limits:
- OpenAI: Per-minute token limits
- ElevenLabs: Character limits per month
- Stability AI: Generation limits per day

## Security Considerations

- All API keys are stored as environment variables
- CORS is configured for specific origins
- Signed URLs have expiration times
- File uploads are validated and sanitized
- Service accounts use minimal required permissions

## Performance Optimization

- Background processing for video generation
- Temporary file cleanup
- Optimized video encoding settings
- Image resizing to standard dimensions
- GPU acceleration for video processing