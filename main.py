from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

MODEL_URL = "https://drive.google.com/uc?export=download&id=1cjt9RlYiqGqY8mmko3HQ2Gbd4yTT3YZz"
MODEL_PATH = "best.pt"

def download_model():
    if os.path.exists(MODEL_PATH):
        print("best.pt already exists. Skipping download.")
        return
    print("Downloading best.pt from Google Drive...")
    response = requests.get(MODEL_URL, stream=True)
    if response.status_code != 200:
        raise Exception("Failed to download model file from Google Drive.")
    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download complete! best.pt saved.")

download_model()
model = YOLO(MODEL_PATH)

@app.post("/predict")
async def predict(file: UploadFile):
    data = await file.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    results = model(img)[0]
    return results.tojson()
