import numpy as np
import math
from ultralytics import YOLO
import os 


FULL_DATA_YAML = '/home/nishank/Downloads/Plastic recyclable detection.v3-roboflow-instant-1--eval-.yolov8/data.yaml'
BATCH_SIZE = 16 
SUBSET_SIZE = 2500 
EPOCHS_PER_SUBSET = 5 
TOTAL_TRAIN_SAMPLES = 19095 
RUNS_BASE_DIR = '/home/nishank/Downloads/Plastic recyclable detection.v3-roboflow-instant-1--eval-.yolov8/runs/detect' 

model = YOLO('yolov8n.pt')
print("Model loaded.")

indices = np.arange(TOTAL_TRAIN_SAMPLES)
np.random.shuffle(indices)
num_subsets = math.ceil(TOTAL_TRAIN_SAMPLES / SUBSET_SIZE)

print(f"Dataset has {TOTAL_TRAIN_SAMPLES} samples. Splitting into {num_subsets} subsets.")

for i in range(num_subsets):
    current_run_name = f'yolov8_block_{i+1}'
    
    if i > 0:
        
        previous_run_name = f'yolov8_block_{i}'
        previous_weights_path = os.path.join(RUNS_BASE_DIR, previous_run_name, 'weights', 'best.pt')
        
        try:
           
            model = YOLO(previous_weights_path)
            print(f"Loaded checkpoint from: {previous_weights_path}")
        except FileNotFoundError:
            print(f"ERROR: Weights for block {i} not found. Skipping block {i+1}.")
            continue

    print(f"\n--- Starting Training Block {i+1} of {num_subsets} ---")
    
   
    results = model.train(
        data=FULL_DATA_YAML,
        epochs=EPOCHS_PER_SUBSET,
        imgsz=480,
        batch=BATCH_SIZE,
        name=current_run_name,
    )