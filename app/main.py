"""The App."""

# sqlalchemy Sessions don't play well with pylint
# pylint: disable=no-member

import logging
from typing import List

from fastapi import Depends, FastAPI
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


@app.get("/records/", response_model=List[schemas.Record])
def show_records(database: Session = Depends(get_database)):
    """Shows all records."""
    records = database.query(models.Record).all()
    logger.info("Retrieved Records")
    return records
