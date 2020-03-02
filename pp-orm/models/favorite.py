from datetime import datetime
from datetime import timezone
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()
class Favorite(base):
  __tablename__ = 'favorites'
  id = Column(BigInteger, primary_key=True)
  tweet_id = Column(BigInteger, ForeignKey("tweets.id"))
  user_id = Column(BigInteger, ForeignKey("users.id"))
  created_at = Column(DateTime, default=datetime.now(timezone.utc))
