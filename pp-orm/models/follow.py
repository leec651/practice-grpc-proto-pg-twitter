from .user import User
from datetime import datetime
from datetime import timezone
from orm import Session
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()
class Follow(base):
  __tablename__ = 'follows'
  id = Column(BigInteger, primary_key=True)
  followee_id = Column(BigInteger, ForeignKey(User.id))
  follower_id = Column(BigInteger, ForeignKey(User.id))
  created_at = Column(DateTime, default=datetime.now(timezone.utc))
  deleted_at = Column(DateTime)

  def __str__(self):
    return (f"Followee ID: {followee_id}"
            f"Follower ID: {follower_id}"
            f"Created at: {created_at}"
            f"Deleted at: {deleted_at}")

  @staticmethod
  def follow(follower_id, followee_id):
    with Session() as session:
      follow = session.query(Follow). \
        filter(Follow.follower_id == follower_id). \
        filter(Follow.followee_id == followee_id).one_or_none()
      if follow:
        if follow.deleted_at:
          follow.deleted_at = None
          session.commit()
      else:
        follow = Follow(followee_id=followee_id, follower_id=follower_id)
        session.add(follow)
        session.commit()

  @staticmethod
  def unfollow(follower_id, followee_id):
    with Session() as session:
      follow = session.query(Follow).\
        filter(Follow.follower_id == follower_id).\
        filter(Follow.followee_id == followee_id).one_or_none()
      if follow:
        follow.deleted_at = datetime.now(timezone.utc)
        session.commit()