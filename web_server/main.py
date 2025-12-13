from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import sys
from pathlib import Path
from typing import List, Dict
import json
from pydantic import BaseModel

# Add parent directory to path to import audio_mixer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio_mixer import StemMixer

# Import Auth modules
from . import models, database, auth_router, auth

app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Include Auth Router
app.include_router(auth_router.router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("temp_uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files to serve stems and output
app.mount("/static", StaticFiles(directory="temp_uploads"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

import io
import contextlib

class MixRequest(BaseModel):
    stems: Dict[str, str]  # name -> filename (in temp_uploads)
    gains: Dict[str, float]
    pans: Dict[str, float]
    auto_gain: bool = False
    use_cnn: bool = False

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
async def mix_audio(request: MixRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        mixer = StemMixer(sample_rate=44100)
        
        # Prepare stems dict with full paths
        stems_paths = {}
        for name, filename in request.stems.items():
            path = UPLOAD_DIR / filename
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"Stem {name} not found")
            stems_paths[name] = str(path)
            
        # Capture stdout to get logs
        log_capture = io.StringIO()
        with contextlib.redirect_stdout(log_capture):
            # Perform mixing
            mixed_audio, used_gains = mixer.mix_stems(
                stems=stems_paths,
                gains=request.gains,
                pans=request.pans,
                normalize_output=True,
                auto_gain=request.auto_gain,
                use_cnn=request.use_cnn
            )
        
        logs = log_capture.getvalue()
        
        output_filename = "web_mix_output.wav"
        output_path = OUTPUT_DIR / output_filename
        mixer.save_audio(mixed_audio, str(output_path))
        
        return {"url": f"/output/{output_filename}", "logs": logs, "gains": used_gains}
        
    except Exception as e:
        print(f"Mixing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "Audio Mixer API is running"}
