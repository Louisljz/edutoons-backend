import uuid
from io import BytesIO
import datetime
from PIL import Image
import requests
from io import BytesIO
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError


IMAGE_SIZE = (1280, 720)


class GCSUtil:
    def __init__(self, bucket_name):
        self.client = storage.Client.from_service_account_json(
            "config/edutoons-service-account.json"
        )
        self.bucket = self.client.bucket(bucket_name)

    def generate_uuid(self):
        """Generate a random UUID for folder naming."""
        return str(uuid.uuid4())

    def upload_image(self, image, project_id):
        """Uploads a image object to the bucket within a unique request folder."""

        file_name = self.generate_uuid()

        file_name += ".webp"
        new_file = BytesIO()
        image.save(new_file, format="webp")
        new_file.seek(0)

        destination_blob_name = f"{project_id}/images/{file_name}"
        blob = self.bucket.blob(destination_blob_name)

        try:
            blob.upload_from_file(new_file)

        except GoogleCloudError as e:
            print(
                f"Failed to upload image to {destination_blob_name}: {e}"
            )

        return destination_blob_name

    def upload_final_video(self, video, project_id):
        """Uploads a video object to the bucket within a unique request folder."""

        destination_blob_name = f"{project_id}/final_video.mp4"
        blob = self.bucket.blob(destination_blob_name)

        try:
            blob.upload_from_file(video)

        except GoogleCloudError as e:
            print(
                f"Failed to upload video to {destination_blob_name}: {e}"
            )

        return destination_blob_name

    def upload_video_clip(self, video, project_id):

        file_name = self.generate_uuid()
        destination_blob_name = f"{project_id}/videos/{file_name}.mp4"
        blob = self.bucket.blob(destination_blob_name)

        try:
            blob.upload_from_file(video)

        except GoogleCloudError as e:
            print(f"Failed to upload video to {destination_blob_name}: {e}")

        return destination_blob_name

    def download_file(self, signed_url):
        """Downloads a file from the specified signed URL and returns it as a bytes object."""
        try:
            response = requests.get(signed_url)
            response.raise_for_status()

            return response.content

        except requests.exceptions.RequestException as e:
            print(f"Failed to download file from {signed_url}: {e}")
            return None

    def generate_signed_url(self, blob_name, expiration=10):
        """Generates a signed URL for the specified file."""
        blob = self.bucket.blob(blob_name)

        try:
            expiration = datetime.timedelta(hours=expiration)
            url = blob.generate_signed_url(expiration=expiration, method="GET")
            return url
        except GoogleCloudError as e:
            print(f"Failed to generate signed URL for {blob_name}: {e}")
            return None
