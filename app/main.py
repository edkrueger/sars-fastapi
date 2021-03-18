"""The App."""

# sqlalchemy Sessions don't play well with pylint
# pylint: disable=no-member

# Pylint isn't playing well with black.
# pylint: disable=bad-continuation

import logging
from typing import List

from fastapi import Depends, FastAPI, Response
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from . import models, schemas
from .database import SessionLocal, engine

gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_database():
    """A dependency for FastAPI routes."""
    try:
        database = SessionLocal()
        yield database
    finally:
        database.close()


@app.get("/")
def main():
    """Redirects to the Swagger Docs."""
    return RedirectResponse(url="/docs/")


@app.get("/records/", summary="Get 300 records", response_model=List[schemas.Record])
def show_records(database: Session = Depends(get_database)):
    """Shows all records."""
    records = database.query(models.Record).limit(300).all()
    logger.info("Retrieved Records")
    return records


@app.post("/records/", summary="Post new record", response_model=schemas.Record)
def post_record(rec: schemas.RecordNew, database: Session = Depends(get_database)):
    """Add a new record."""
    record = models.Record(**rec.dict())
    database.add(record)
    database.commit()
    database.refresh(record)
    return record


@app.get("/records/{rec_id}", summary="Get a record", response_model=schemas.Record)
def get_record(rec_id: int, database: Session = Depends(get_database)):
    """Get a record."""
    record = database.query(models.Record).filter(models.Record.id == rec_id).first()
    return record


@app.put("/records/{rec_id}", summary="Modify a record", response_model=schemas.Record)
def put_record(
    rec_id: int, rec: schemas.RecordNew, database: Session = Depends(get_database)
):
    """Modify a record."""

    database.query(models.Record).filter(models.Record.id == rec_id).update(rec.dict())
    database.commit()
    db_record = database.query(models.Record).filter(models.Record.id == rec_id).first()
    return db_record


@app.delete(
    "/records/{rec_id}",
    summary="Delete a record",
    response_class=Response,
    responses={
        200: {"description": "Record successfully deleted"},
        404: {"description": "Record not found"},
    },
)
def delete_record(rec_id: int, database: Session = Depends(get_database)):
    """Delete a record."""

    if database.query(models.Record).filter(models.Record.id == rec_id).count() == 0:
        return Response(status_code=404)

    database.query(models.Record).filter(models.Record.id == rec_id).delete()
    database.commit()
    return Response(status_code=200)
