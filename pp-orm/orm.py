import datetime
import time
import traceback

from config import settings
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}".format(
  user=settings.POSTGRES_USER,
  password=settings.POSTGRES_PASSWORD,
  host=settings.POSTGRES_HOST,
  port=settings.POSTGRES_PORT,
  dbname=settings.POSTGRES_DB
)
engine = create_engine(db_url, pool_size=20, max_overflow=0)
session_maker = sessionmaker(bind=engine)


@contextmanager
def Session(*args, **kwds):
  session = session_maker()
  try:
    yield session
  except Exception as err:
    session.rollback()
    raise err
  finally:
    session.close()

# export all ORM models
from models.favorite import Favorite
from models.follow import Follow
from models.tweet import Tweet
from models.user import User
