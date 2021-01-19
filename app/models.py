from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.types import Date
from .database import Base


class Record(Base):
    __tablename__ = "Records"

    id = Column(Integer, Sequence('records_seq', start=1001, increment=1), primary_key=True, index=True)
    date = Column(Date)
    country = Column(String(255), index=True)
    cases = Column(Integer)
    deaths = Column(Integer)
    recoveries = Column(Integer)
