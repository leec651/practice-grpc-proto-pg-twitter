from .user import User
from datetime import datetime
from datetime import timezone
from orm import Session
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()
class Tweet(base):
  __tablename__ = 'tweets'
  id            = Column(BigInteger, primary_key=True)
  user_id       = Column(BigInteger, ForeignKey(User.id))
  content       = Column(String, nullable=False)
  latitude      = Column(Numeric, default=0)
  longtitude    = Column(Numeric, default=0)
  num_favorites = Column(Integer, default=0, nullable=False)
  created_at    = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
  deleted_at    = Column(DateTime)

  def __str__(self):
    return (f"ID: {self.id}\n"
            f"USER ID: {self.user_id}\n"
            f"Content: {self.content}\n"
            f"latitude: {self.latitude}\n"
            f"longtitude: {self.longtitude}\n"
            f"num_favorites: {self.num_favorites}\n"
            f"created_at: {self.created_at}\n")

  @staticmethod
  def post(user_id, content, latitude, longtitude):
    """Post a tweet"""
    if len(content) > 300:
      raise ValueError(f"Content length is greater than 300. Got {len(content)}")

    with Session() as session:
      # we need to set created_at here instead of using the default because
      # expunge was called before created_at was set during commit
      new_tweet = Tweet(user_id=user_id,
                        content=content,
                        latitude=latitude,
                        longtitude=longtitude,
                        created_at=datetime.now(timezone.utc))
      session.add(new_tweet)
      # we need to duplicate another one and detach it from the session
      # in order to use it outside of session
      # https://docs.sqlalchemy.org/en/latest/orm/session_state_management.html#merge-tips
      merged_tweet = session.merge(new_tweet)
      session.expunge(merged_tweet)
      session.commit()
      return merged_tweet

  @staticmethod
  def delete(user_id, tweet_id):
    """Delete a tweet"""
    with Session() as session:
      now = datetime.now(timezone.utc)
      tweet = session.query(Tweet). \
        filter(Tweet.id == tweet_id). \
        filter(Tweet.user_id == user_id).one()
      tweet.deleted_at = now
      session.commit()

  @staticmethod
  def get_tweets(user_id, created_at, offset=0, limit=100):
    with Session() as session:
      query = session.query(Tweet).\
                filter(Tweet.deleted_at == None).\
                filter(Tweet.user_id == user_id).\
                filter(Tweet.created_at > created_at)
      for tweet in query.limit(limit).offset(offset).yield_per(10):
        yield tweet
