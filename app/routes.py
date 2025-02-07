import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import redis
import os
from .models import UploadedFile, ScrapedMetadata
from .database import get_db
from .worker import scrape_url_task

router = APIRouter()
redis_conn = redis.Redis.from_url(os.getenv("REDIS_URL"))

@router.post("/upload")
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    if "url" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'url' column")
    
    uploaded_file = UploadedFile(filename=file.filename)
    db.add(uploaded_file)
    db.commit()
    
    for url in df["url"]:
        task_id = scrape_url_task.delay(uploaded_file.id, url)
        redis_conn.set(task_id, "pending")

    return {"message": "File uploaded successfully", "file_id": uploaded_file.id}
