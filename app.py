from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import sqlite3
import uuid
from datetime import date

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    YOLO_AVAILABLE = False
    print(f"Warning: ultralytics not available: {e}")

# Paths
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
DB_PATH = Path(__file__).resolve().parent / "usage.db"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(title="Plastic Usage Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model
MODEL = None

# Serve frontend from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
app.mount('/static', StaticFiles(directory=str(ROOT_DIR)), name='root_static')


@app.get('/', response_class=HTMLResponse)
def serve_index():
    idx = ROOT_DIR / 'index.html'
    if not idx.exists():
        return HTMLResponse('<h1>Index not found</h1>', status_code=404)
    return HTMLResponse(idx.read_text(encoding='utf-8'))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    tb = traceback.format_exc()
    # Log to server console for debugging
    print('=== Unhandled Exception ===')
    print(tb)
    # Return JSON so frontend can parse and show error details
    return JSONResponse(status_code=500, content={
        'status': 'error',
        'error': str(exc),
        'trace': tb
    })


def init_db():
    """Initialize SQLite database for tracking daily plastic usage."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usage (
            id TEXT PRIMARY KEY,
            email TEXT,
            entry_date TEXT,
            label TEXT,
            count INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def upsert_counts(email: str, entry_date: str, counts: dict):
    """Add or update detection counts for a user on a given date."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for label, cnt in counts.items():
        cur.execute(
            "SELECT id, count FROM usage WHERE email=? AND entry_date=? AND label=?",
            (email, entry_date, label)
        )
        row = cur.fetchone()
        if row:
            uid, existing = row
            new_count = existing + cnt
            cur.execute("UPDATE usage SET count=? WHERE id=?", (new_count, uid))
        else:
            uid = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO usage (id,email,entry_date,label,count) VALUES (?,?,?,?,?)",
                (uid, email, entry_date, label, cnt)
            )
    conn.commit()
    conn.close()


def get_summary(email: str, entry_date: str):
    """Get all detections for a user on a given date."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT label, count FROM usage WHERE email=? AND entry_date=?",
        (email, entry_date)
    )
    rows = cur.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def map_label_to_category(label: str) -> str:
    """Map YOLO detected labels to plastic categories."""
    l = label.lower()
    
    if any(k in l for k in ("bottle", "flask", "jar")):
        return "Bottle"
    if any(k in l for k in ("bag", "sack", "pouch")):
        return "Bag"
    if any(k in l for k in ("cup", "mug", "glass")):
        return "Cup"
    if "straw" in l:
        return "Straw"
    if any(k in l for k in ("packet", "wrapper", "container")):
        return "Container"
    if "plastic" in l or "poly" in l:
        return "Plastic"
    
    return "Other"


@app.on_event("startup")
def startup_event():
    """Load YOLO model on startup."""
    init_db()
    global MODEL
    
    if not YOLO_AVAILABLE:
        print("ultralytics package not installed. Install with: pip install ultralytics")
        MODEL = None
        return
    
    # Try to find weights file
    candidates = [
        Path(__file__).resolve().parent.parent / 'yolov8n.pt',
        Path(__file__).resolve().parent / 'yolov8n.pt',
    ]
    
    weights = None
    for candidate in candidates:
        if candidate.exists():
            weights = str(candidate)
            break
    
    if weights is None:
        weights = 'yolov8n.pt'
    
    try:
        MODEL = YOLO(weights)
        print(f"✅ YOLO model loaded: {weights}")
    except Exception as e:
        print(f"❌ Failed to load YOLO model: {e}")
        MODEL = None


@app.post("/api/upload")
async def upload_image(
    email: str = Form(...),
    file: UploadFile = File(...),
    the_date: str = Form(None)
):
    """
    Upload an image and run YOLO detection.
    
    - email: user email
    - file: image file
    - the_date: optional date (format: DD-MM-YYYY)
    
    Returns: {status, detections, summary}
    """
    if not email:
        raise HTTPException(status_code=400, detail="email is required")
    
    entry_date = the_date or date.today().strftime("%d-%m-%Y")
    
    # Save uploaded image
    user_dir = UPLOAD_DIR / email
    dest_dir = user_dir / entry_date
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = dest_dir / filename
    
    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    
    print(f"📷 Image saved: {dest_path}")
    
    # Run detection
    detections = {}
    
    if MODEL is None:
        return JSONResponse({
            "status": "ok",
            "note": "YOLO model not available on server",
            "detections": {},
            "summary": get_summary(email, entry_date)
        })
    
    try:
        results = MODEL.predict(source=str(dest_path), imgsz=640, conf=0.25, verbose=False)
        
        if not results:
            return JSONResponse({
                "status": "ok",
                "detections": {},
                "summary": get_summary(email, entry_date)
            })
        
        res = results[0]
        names = getattr(MODEL, 'names', None) or {}
        
        # Extract detections from boxes
        for box in getattr(res, 'boxes', []):
            try:
                cls = int(box.cls.cpu().numpy()[0]) if hasattr(box.cls, 'cpu') else int(box.cls)
            except Exception:
                try:
                    cls = int(box.cls)
                except Exception:
                    continue
            
            label = names.get(cls, str(cls))
            category = map_label_to_category(label)
            detections[category] = detections.get(category, 0) + 1
            print(f"🔍 Detected: {label} -> {category}")
    
    except Exception as e:
        print(f"❌ Detection error: {e}")
        return JSONResponse({"status": "error", "error": str(e)})
    
    # Persist to database
    if detections:
        upsert_counts(email, entry_date, detections)
    
    summary = get_summary(email, entry_date)
    
    return JSONResponse({
        "status": "ok",
        "detections": detections,
        "summary": summary
    })


@app.get("/api/summary")
def api_summary(email: str, the_date: str = None):
    """Get today's (or specified date) detection summary for a user."""
    if not email:
        raise HTTPException(status_code=400, detail="email is required")
    
    entry_date = the_date or date.today().strftime("%d-%m-%Y")
    summary = get_summary(email, entry_date)
    
    return JSONResponse({
        "status": "ok",
        "date": entry_date,
        "summary": summary
    })


@app.get("/api/health")
def health():
    """Health check and model status."""
    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "ultralytics_available": YOLO_AVAILABLE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
