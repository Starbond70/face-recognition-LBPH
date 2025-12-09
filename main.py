from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
import uvicorn
import os
import time
import asyncio
from typing import List, Set

from src.data_handler import DataManager
from src.face_rec import FaceRecognitionSystem

app = FastAPI(title="Face Attendance System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (Useful if running frontend separately, though we serve static here)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_manager = DataManager()
try:
    face_rec = FaceRecognitionSystem()
except Exception as e:
    print(f"Error initializing Face Recognition System: {e}")
    face_rec = None

# In-memory state
attendance_session: Set[str] = set() # Set of Student IDs

@app.get("/")
async def read_root():
    with open("static/index.html", "r") as f:
        content = f.read()
    return Response(content=content, media_type="text/html")

# --- API Endpoints ---

@app.get("/api/dashboard")
async def get_dashboard_stats():
    """Returns dashboard statistics and student list."""
    today_df = data_manager.get_attendance_today()
    students_df = data_manager.get_attendance_today() 
    # Using read_csv directly or data_manager helper for registered students
    
    registered_count = 0
    registered_students = []
    if os.path.exists(data_manager.student_file):
        import pandas as pd
        try:
            sdf = pd.read_csv(data_manager.student_file)
            registered_count = len(sdf)
            registered_students = sdf.to_dict(orient="records")
        except Exception:
            pass

    today_count = len(today_df) if not today_df.empty else 0
    
    return {
        "today_count": today_count,
        "total_students": registered_count,
        "students": registered_students
    }

@app.post("/api/register/check")
async def check_student(data: dict):
    """Check if student ID exists before starting capture."""
    student_id = data.get("student_id")
    name = data.get("name")
    if not student_id or not name:
        return JSONResponse(status_code=400, content={"message": "ID and Name required"})
    
    success, msg = data_manager.add_student(student_id, name)
    # The current add_student appends immediately. 
    # Logic in Streamlit was: add -> then capture.
    # If capture fails or is aborted, we might have a student with no images. 
    # That matches existing logic.
    
    if success:
        return {"success": True, "message": msg}
    else:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

@app.post("/api/train")
async def train_model():
    if not face_rec:
        return JSONResponse(status_code=500, content={"message": "System not initialized"})
    
    success, msg = face_rec.train_model()
    if success:
        return {"success": True, "message": msg}
    else:
        return JSONResponse(status_code=500, content={"success": False, "message": msg})

@app.get("/api/attendance/current")
async def get_current_attendance():
    """Get list of currently recognized students in this session."""
    students = []
    for sid in attendance_session:
        name = data_manager.get_student_name(sid)
        students.append({"id": sid, "name": name})
    return {"students": students}

@app.post("/api/attendance/save")
async def save_attendance():
    if not attendance_session:
        return {"success": False, "message": "No students to save."}
    
    count = 0
    for sid in attendance_session:
        name = data_manager.get_student_name(sid)
        success, _ = data_manager.mark_attendance(sid, name)
        if success:
            count += 1
            
    attendance_session.clear()
    return {"success": True, "message": f"Saved {count} records."}

@app.post("/api/attendance/clear")
async def clear_attendance_session():
    attendance_session.clear()
    return {"success": True, "message": "Cleared session."}

@app.post("/api/danger/clear")
async def clear_all_data(data: dict):
    password = data.get("password")
    if password != "244001":
         return JSONResponse(status_code=403, content={"success": False, "message": "Incorrect Password"})
    
    success, msg = data_manager.clear_all_students()
    return {"success": success, "message": msg}

# --- Video Streams ---

def gen_frames_registration(student_id, name):
    """Generator for registration video feed."""
    if not face_rec:
        return
        
    limit = 30
    # Create generator
    gen = face_rec.capture_frames(student_id, name, limit=limit)
    
    for frame, count, total in gen:
        if frame is None:
            break
            
        # Draw progress on frame
        # Convert RGB (from generator) to BGR for OpenCV drawing
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        cv2.putText(frame_bgr, f"Progress: {count}/{total}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Encode
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
    # Send a "Completed" image or just stop
    # To notify frontend of completion, frontend can poll or just see stream end.

@app.get("/video_feed/register/{student_id}/{name}")
async def video_feed_register(student_id: str, name: str):
    return StreamingResponse(gen_frames_registration(student_id, name), 
                             media_type='multipart/x-mixed-replace; boundary=frame')

def gen_frames_attendance():
    """Generator for attendance video feed."""
    if not face_rec:
        return

    # Use existing generator
    gen = face_rec.generate_frames()
    
    for frame, students in gen:
        if frame is None:
            break
            
        # Update session state global
        for s in students:
            attendance_session.add(str(s['id']))
        
        # Frame is RGB, convert to BGR for encoding if needed (imencode expects BGR usually, but let's check input)
        # face_rec.generate_frames returns RGB.
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed/attendance")
async def video_feed_attendance():
    return StreamingResponse(gen_frames_attendance(), 
                             media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
