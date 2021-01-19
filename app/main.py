from fastapi import Depends, FastAPI, HTTPException, Response
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


# get all
@app.get("/records/", summary="Get 300 records", response_model=List[schemas.Record])
def get_all_records(db: Session = Depends(get_db)):
    records = db.query(models.Record).limit(300).all()
    return records

# create new
@app.post("/records/", summary="Post new record", response_model=schemas.Record)
def post_record(rec: schemas.RecordNew, db: Session = Depends(get_db)):
    db_record = models.Record(**rec.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# get single
@app.get("/records/{rec_id}", summary="Get a record", response_model=schemas.Record)
def get_record(rec_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == rec_id).first()
    return record

# modify existing
@app.put("/records/{rec_id}", summary="Modify a record", response_model=schemas.Record)
def put_record(rec_id: int, rec: schemas.RecordNew, db: Session = Depends(get_db)):
    db.query(models.Record).filter(models.Record.id == rec_id).update(rec.dict())
    db.commit()
    db_record = db.query(models.Record).filter(models.Record.id == rec_id).first()
    return db_record

# delete existing
@app.delete("/records/{rec_id}", summary="Delete a record", response_class=Response, responses={200: {"description": "Record successfully deleted"},404: {"description": "Record not found"},},)
def delete_record(rec_id: int, db: Session = Depends(get_db)):
    if db.query(models.Record).filter(models.Record.id == rec_id).count() == 0:
        return Response(status_code=404)
    else:
        db.query(models.Record).filter(models.Record.id == rec_id).delete()
        db.commit()
        return Response(status_code=200)
