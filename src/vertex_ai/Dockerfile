FROM huggingface/transformers-pytorch-gpu:4.41.2

WORKDIR /app

COPY video_model/ /app/video_model/

COPY vertex_ai/requirements.txt /app/

RUN pip install -r requirements.txt

COPY vertex_ai/ /app/

EXPOSE 8000

CMD ["fastapi", "run", "app.py"]