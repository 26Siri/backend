import numpy as np
import math
from ultralytics import YOLO
from torch.utils.data import random_split, Subset

FULL_DATA_YAML = '/home/nishank/Downloads/Plastic recyclable detection.v3-roboflow-instant-1--eval-.yolov8/data.yaml'
BATCH_SIZE = 16 
SUBSET_SIZE = 2500 
EPOCHS_PER_SUBSET = 5 


model = YOLO('yolov8n.pt')
print("Model loaded.")


TOTAL_TRAIN_SAMPLES = 19095 


indices = np.arange(TOTAL_TRAIN_SAMPLES)
np.random.shuffle(indices)
num_subsets = math.ceil(TOTAL_TRAIN_SAMPLES / SUBSET_SIZE)

print(f"Dataset has {TOTAL_TRAIN_SAMPLES} samples. Splitting into {num_subsets} subsets of {SUBSET_SIZE} images each.")


for i in range(num_subsets):
    print(f"\n--- Starting Training Block {i+1} of {num_subsets} ---")
    
  
    start_index = i * SUBSET_SIZE
    end_index = min((i + 1) * SUBSET_SIZE, TOTAL_TRAIN_SAMPLES)
    
    
    subset_indices = indices[start_index:end_index]
    
    

    print("YOLOv8 best practice is continuous training.")
    print("Training continuously for better performance, but checking in small steps.")

 
    results = model.train(
        data=FULL_DATA_YAML,
        epochs=EPOCHS_PER_SUBSET,  
        imgsz=480,
        batch=BATCH_SIZE,
        name=f'yolov8_block_{i+1}',
        resume=True if i > 0 else False 
    )
    
final_model = YOLO('yolov8n.pt') 
results = final_model.train(
    data=FULL_DATA_YAML,
    epochs=100, 
    imgsz=480,
    batch=16,
    name='yolov8_final_fast_run'
)