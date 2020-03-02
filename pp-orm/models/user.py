import bcrypt
import jwt

from config import settings
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from orm import Session
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound


# 1 month
_TOKEN_EXPIRATION = 24 * 30


base = declarative_base()
class User(base):
  __tablename__ = 'users'
  id            = Column(BigInteger, primary_key=True)
  email         = Column(String, nullable=False)
  password      = Column(String, nullable=False)
  salt          = Column(String, nullable=False)
  phone         = Column(String)
  name          = Column(String, nullable=False)
  latitude      = Column(Numeric)
  longtitude    = Column(Numeric)
  created_at    = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
  last_login_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

  def __str__(self):
    return (f"ID: {self.id}\n"
            f"Email: {self.email}\n"
            f"Name: {self.name}\n"
            f"latitude: {self.latitude}\n"
            f"longtitude: {self.longtitude}\n")

  @staticmethod
  def login(email, password):
    with Session() as session:
      user = session.query(User).filter(User.email == email).one()
      b_hashed = bytes(user.password, 'utf-8')
      b_password = bytes(password, 'utf-8')
      if bcrypt.checkpw(b_password, b_hashed):
        return make_token(user)
      else:
        raise ValueError('Invalid password')

  @staticmethod
  def create(password, email, phone, name, latitude=0, longtitude=0):
    hashed_password, salt = make_password(password)
    with Session() as session:
      new_user = User(email=email,
                      password=hashed_password,
                      salt=salt,
                      phone=phone,
                      name=name,
                      latitude=latitude,
                      longtitude=longtitude)
      session.add(new_user)
      session.commit()
      token = make_token(new_user)
      return token

def make_token(user):
  data = {
    'user_info': {
      'email': user.email,
      'user_id': user.id
    },
    'exp': datetime.utcnow() + timedelta(hours=_TOKEN_EXPIRATION)
  }
  return jwt.encode(data, settings.JWT_SECRET, algorithm='HS256')

def make_password(password):
  b_salt = bcrypt.gensalt()
  b_password = bytes(password, 'utf-8')
  b_hashed = bcrypt.hashpw(b_password, b_salt)
  return str(b_hashed, 'utf-8'), str(b_salt, 'utf-8')

