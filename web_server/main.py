from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil
import os
import sys
from pathlib import Path
from typing import List, Dict
import json
from pydantic import BaseModel
import uuid
from datetime import datetime
import io
import contextlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio_engine.audio_mixer import StemMixer

from . import models, database, auth_router, auth

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("temp_uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="temp_uploads"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

class MixRequest(BaseModel):
    stems: Dict[str, str]
    gains: Dict[str, float]
    pans: Dict[str, float]
    auto_gain: bool = False
    use_cnn: bool = False

class MixLog(BaseModel):
    id: int
    timestamp: datetime
    logs: str
    output_url: str
    settings_summary: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "url": f"/static/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mix")
async def mix_audio(request: MixRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    try:
        mixer = StemMixer(sample_rate=44100)
        
        stems_paths = {}
        for name, filename in request.stems.items():
            path = UPLOAD_DIR / filename
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"Stem {name} not found")
            stems_paths[name] = str(path)
            
        log_capture = io.StringIO()
        with contextlib.redirect_stdout(log_capture):
            mixed_audio, used_gains = mixer.mix_stems(
                stems=stems_paths,
                gains=request.gains,
                pans=request.pans,
                normalize_output=True,
                auto_gain=request.auto_gain,
                use_cnn=request.use_cnn
            )
        
        logs = log_capture.getvalue()
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"mix_{current_user.username}_{timestamp_str}_{unique_id}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        mixer.save_audio(mixed_audio, str(output_path))
        
        summary = f"{len(request.stems)} stems. Auto-Gain: {'On' if request.auto_gain else 'Off'}. CNN: {'On' if request.use_cnn else 'Off'}."
        
        history_entry = models.MixHistory(
            user_id=current_user.id,
            output_filename=output_filename,
            logs=logs,
            settings_summary=summary
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        
        return {"url": f"/output/{output_filename}", "logs": logs, "gains": used_gains, "history_id": history_entry.id}
        
    except Exception as e:
        print(f"Mixing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[MixLog])
async def get_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    history_items = db.query(models.MixHistory).filter(models.MixHistory.user_id == current_user.id).order_by(models.MixHistory.timestamp.desc()).all()
    
    result = []
    for item in history_items:
        result.append(MixLog(
            id=item.id,
            timestamp=item.timestamp,
            logs=item.logs,
            output_url=f"/output/{item.output_filename}",
            settings_summary=item.settings_summary or "Custom Mix"
        ))
    return result

@app.delete("/history/{item_id}")
async def delete_history_item(item_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    history_item = db.query(models.MixHistory).filter(models.MixHistory.id == item_id, models.MixHistory.user_id == current_user.id).first()
    if not history_item:
        raise HTTPException(status_code=404, detail="History item not found")
    
    try:
        file_path = OUTPUT_DIR / history_item.output_filename
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.delete(history_item)
    db.commit()
    return {"status": "deleted"}

@app.get("/")
def read_root():
    return {"status": "Auralis API is running"}
