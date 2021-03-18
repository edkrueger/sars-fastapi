"""Pydantic Schemas."""

# pylint doesn't play well with pydandic
# basic pydandic classes a auto-documenting
# pydandic classes don't need methods
# pylint: disable=no-name-in-module, missing-class-docstring, too-few-public-methods

from datetime import date
from pydantic import BaseModel


class Record(BaseModel):
    id: int
    date: date
    country: str
    cases: int
    deaths: int
    recoveries: int

    class Config:
        orm_mode = True
