import logging
from logging.config import dictConfig

from faker import Faker
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session


from . import crud, models, schemas, logconf
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

dictConfig(logconf.config)
app = FastAPI()
fake = Faker()
logger = logging.getLogger("store")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    session = SessionLocal()

    number_of_users = session.query(models.User).count()
    if number_of_users != 0:
        logger.info("Database already populated, skipping")
        return

    logger.info("Populating database with fake data")
    for _ in range(100):
        user = schemas.UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )
        user = crud.create_user(session, user)

        for _ in range(10):
            item = schemas.ItemCreate(
                title=fake.name(),
                description=fake.paragraph(),
            )
            crud.create_user_item(session, item, user.id)
    logger.info("Finished populating database")


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
