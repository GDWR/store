import logging
import operator
import random
from logging.config import dictConfig

from faker import Faker
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import column, select, func, literal
from sqlalchemy.orm import Session

from . import models, schemas, logconf
from .database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

dictConfig(logconf.config)
app = FastAPI()
fake = Faker()
logger = logging.getLogger("store")


@app.on_event("startup")
def startup_event():
    session = SessionLocal()

    file_count = session.query(models.File).count()
    if file_count != 0:
        logger.info("Database already populated, skipping")
        return

    logger.info("Populating database with fake data")
    for _ in range(100):
        file = models.File(
            path=fake.file_path()
        )
        session.add(file)
        session.commit()
        session.refresh(file)

        for _ in range(random.randint(0, 3)):
            error = models.Error(
                file=file,
                message=fake.text(),
            )
            session.add(error)
            session.commit()

    logger.info("Finished populating database")


@app.get("/files/", response_model=schemas.Paginated[schemas.FileWithErrors])
def get_files(size: int = 0, max: int = 25, session: Session = Depends(get_db)):
    count = select(func.count()) \
        .select_from(models.File) \
        .cte('count')

    stmt = select(models.File, column('count')) \
        .distinct(models.File.id) \
        .join(models.Error, isouter=True) \
        .join(count, literal(1) == 1) \
        .offset(size * max) \
        .limit(max)

    results = session \
        .execute(stmt) \
        .all()

    # count comes with parenthesis?
    count = results[0][1].replace('(', '').replace(')', '')

    return {
        "size": size,  # offset
        "max": max,  # amount returned
        "count": count,
        "results": map(operator.itemgetter(0), results),
    }


@app.get("/files/{file_id}", response_model=schemas.File)
def get_file_by_id(file_id: int, session: Session = Depends(get_db)):
    file = session \
        .query(models.File) \
        .filter(models.File.id == file_id) \
        .first()

    if file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return file


@app.get("/errors/", response_model=list[schemas.Error])
def get_errors(skip: int = 0, limit: int = 100, session: Session = Depends(get_db)):
    return session \
        .query(models.Error) \
        .offset(skip) \
        .limit(limit) \
        .all()


@app.get("/errors/{error_id}", response_model=schemas.Error)
def get_file_by_id(error_id: int, session: Session = Depends(get_db)):
    error = session \
        .query(models.Error) \
        .filter(models.Error.id == error_id) \
        .first()

    if error is None:
        raise HTTPException(status_code=404, detail="Error not found")

    return error
