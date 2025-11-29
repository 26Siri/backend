import os
import cv2
from ultralytics import YOLO

# Correct project root
PROJECT_ROOT = r"E:\MINIPTOJECT"

# Corrected weights path
WEIGHTS_PATH = r"E:\MINIPTOJECT\yolov8_block_1-20251118T140423Z-1-001\yolov8_block_1\weights\best.pt"

# Correct test image path (fix your path)
TEST_IMAGE_PATH = r"E:\MINIPTOJECT\drive-download-20251118T143044Z-1-001\20240416_134603_jpg.rf.2cb89106df70105a0aa4fecc13f4a9fd.jpg"

try:
    # Load model
    model = YOLO(WEIGHTS_PATH)
    print("Model loaded successfully from Batch 1 checkpoint.")

    # Predict
    results = model.predict(source=TEST_IMAGE_PATH, conf=0.25)

    # Display results
    im_array = results[0].plot()
    cv2.imshow('YOLOv8 Plastic Detection Test', im_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print raw detections
    print("\n--- Raw Prediction Output ---")
    for box in results[0].boxes:
        label = model.names[int(box.cls[0])]
        conf = box.conf[0].item()
        print(f"Detected: {label} (Confidence: {conf:.2f})")

except FileNotFoundError:
    print(f"\nERROR: Model weights not found at: {WEIGHTS_PATH}")
    print("Please verify the weights folder path.")
except Exception as e:
    print(f"\nAn error occurred during inference: {e}")
