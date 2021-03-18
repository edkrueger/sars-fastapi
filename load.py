"""Load the data into the database."""

# sqlalchemy Sessions don't play well with pylint
# pylint: disable=no-member

import csv
import datetime

from app import models
from app.database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

# import fresh data only if the table is empty
if db.query(models.Record).count() == 0:

    with open("sars_2003_complete_dataset_clean.csv", "r") as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = models.Record(
                date=datetime.datetime.strptime(row["date"], "%Y-%m-%d"),
                country=row["country"],
                cases=row["cases"],
                deaths=row["deaths"],
                recoveries=row["recoveries"],
            )
            db.add(db_record)
        db.commit()

db.close()
