# Backend for Daily Plastic Usage Tracker

This backend exposes simple endpoints to accept image uploads, run a YOLOv8 detection (if `ultralytics` and weights are available), and store per-user per-day aggregated counts.

Files:
- `app.py` - FastAPI server (endpoints: `/api/upload`, `/api/summary`, `/api/health`).
- `requirements.txt` - Python dependencies.

Quick start (Windows PowerShell):

```powershell
cd e:\MINIPTOJECT\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# make sure the YOLO weights (e.g. yolov8n.pt) are available at the project root or backend folder
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:
- `POST /api/upload` (multipart form): fields: `email` (string), `file` (image), optional `the_date` (dd-mm-YYYY). Returns detections and updated summary for that user+date.
- `GET /api/summary?email=you@example.com` returns aggregated counts for today (or pass `the_date`).
- `GET /api/health` quick health check.

Integration notes:
- The provided frontend (`index.html`) is currently fully client-side and stores usage in `localStorage`.
- To integrate without modifying `index.html`, you can either:
  - Serve the frontend through this backend and inject a small integration script, or
  - Use a browser bookmarklet / console snippet that intercepts the form submit and `fetch`es `/api/upload` with the selected image and `email` value.
This backend can now serve the frontend directly and inject a small integration script so you do NOT have to edit `index.html`.

Open `http://localhost:8000/` after starting the server to load the dashboard served by the backend. A floating `Upload & Detect` button will appear in the bottom-right — click it to capture/upload an image from the camera or file picker. The backend will run detection and the UI will be updated automatically.

If you prefer the bookmarklet/console approach instead, tell me and I can provide that too.
