from openai import OpenAI
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from moviepy.editor import (ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips)
import json
import requests
import os


class EduToons:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def generate_storyboard(self, content: str, video_type: str, duration: str):
        completion = self.openai.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": f"""
                You are a cartoonist who is creating a storyboard for an {video_type} video. Use the provided content to generate DALL-E prompts for the storyboard, associated with a relevant script for each scene to be narrated in the video. The video should be {duration} in length. Be sure that each scene last for less than 4 seconds, when converted to speech.""" + 
                '''
                Respond in the form of JSON object with the following structure:
                {"storyboard": [{"prompt": "", "script": ""}, {"prompt": "", "script": ""}, ...]}
                ''',
                },
                {"role": "user", "content": f'video content: {content}'},
            ],
        )
        response = completion.choices[0].message.content
        return json.loads(response)['storyboard']

    def text_to_image(self, prompt: str, project_id: str):
        stable_api = f'{os.getenv("STABLE_API_URL")}/draw/'
        data = {"prompt": prompt, "projectId": project_id}
        response = requests.post(stable_api, json=data)
        return response.json()["imageUrl"]

    def image_to_video(self, image_url: str, project_id: str):
        stable_api = f'{os.getenv("STABLE_API_URL")}/animate/'
        data = {"url": image_url, "projectId": project_id}
        response = requests.post(stable_api, json=data)
        return response.json()["videoUrl"]

    def text_to_speech(self, script: str, audio_path: str):
        response = self.elevenlabs.text_to_speech.convert(
            voice_id="5HuFhTDIKwL0cGenPHbW",
            output_format="mp3_22050_32",
            text=script,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        with open(audio_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

    def create_video_clip(self, video_path, audio_path):
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        video = VideoFileClip(video_path)

        if video.duration > duration:
            video = video.subclip(0, duration)
        elif video.duration < duration:
            repeats = int(duration // video.duration) + 1
            video = concatenate_videoclips([video] * repeats).subclip(0, duration)

        video = video.set_audio(audio)
        return video

    def create_photo_clip(self, photo_path, audio_path):
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        photo = ImageClip(photo_path).set_duration(duration)
        photo = photo.set_audio(audio)
        return photo

    def regenerate_scene(self, new_text: str):
        # Logic to regenerate scene with new text
        pass

    def stitch_video(self, clips: list, video_path: str):
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(video_path, codec="libvpx", fps=24)
