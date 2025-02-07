from celery import Celery
import requests
from bs4 import BeautifulSoup
import os
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ScrapedMetadata

celery = Celery("tasks", broker=os.getenv("REDIS_URL"))

@celery.task
def scrape_url_task(file_id, url):
    db = SessionLocal()
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text if soup.find("title") else None
        description = soup.find("meta", attrs={"name": "description"})
        keywords = soup.find("meta", attrs={"name": "keywords"})

        metadata = ScrapedMetadata(
            file_id=file_id,
            url=url,
            title=title,
            description=description["content"] if description else None,
            keywords=keywords["content"] if keywords else None,
            status="completed",
        )
        db.add(metadata)
        db.commit()
    except Exception:
        metadata = ScrapedMetadata(file_id=file_id, url=url, status="failed")
        db.add(metadata)
        db.commit()
    finally:
        db.close()
