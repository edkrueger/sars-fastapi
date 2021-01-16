from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from typing import List

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fastapi.logger import logger
import logging
gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)

from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    logger.info("Startup event !")

    scheduler = AsyncIOScheduler(timezone=pytz.utc)
    scheduler.start()
    scheduler.add_job(count_records_task, "cron", minute='*')  # runs every minute

def count_records_task():
    db = SessionLocal()
    n = db.query(models.Record).count()
    logger.info(f"Cron counter {n}")


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.get("/records/", response_model=List[schemas.Record])
def show_records(db: Session = Depends(get_db)):
    logger.info("Rest call")
    records = db.query(models.Record).limit(300).all()
    return records
