@echo off
echo Building Docker image...
docker build -t gcr.io/edutoons-431101/stable-diffusion-image .

echo Pushing Docker image to Artifact Registry...
docker push gcr.io/edutoons-431101/stable-diffusion-image

echo Uploading model to Vertex AI...
gcloud ai models upload --container-ports=8000 --container-predict-route="/predict" --container-health-route="/health" --region=us-central1 --display-name=stable-diffusion-model --container-image-uri=gcr.io/edutoons-431101/stable-diffusion-image

echo Creating Vertex AI endpoint...
gcloud ai endpoints create --project=edutoons-431101 --region=us-central1 --display-name=stable-diffusion

echo All tasks completed.
pause
