import grpc

from auth import Authenticator
from auth import get_user_info_from_context
from config import settings
from google.protobuf.timestamp_pb2 import Timestamp
from middleware import HandleGenericError
from middleware import handle_resp
from orm import Tweet
from orm import session_maker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from structlog import get_logger
from tweet_pb2_grpc import TweetServicer
from tweet_types_pb2 import EmptyReply
from tweet_types_pb2 import GetTweetRequest
from tweet_types_pb2 import Tweet as ProtoTweet
from tweet_types_pb2 import TweetReply

logger = get_logger()

def to_proto_tweet(db_tweet):
  """Convert db tweet to proto tweet"""
  created_at = Timestamp()
  created_at.FromJsonString(db_tweet.created_at.isoformat())
  return ProtoTweet(id=db_tweet.id, user_id=db_tweet.user_id, content=db_tweet.content,
                    latitude=db_tweet.latitude, longtitude=db_tweet.longtitude,
                    num_favorites=db_tweet.num_favorites, created_at=created_at)


class TweetService(TweetServicer):
  """Tweet service gRPC implementation"""

  @Authenticator(response_class=TweetReply, jwt_key=settings.JWT_SECRET)
  def Tweet(self, request, context):
    """Post a tweet message"""
    result = TweetReply()
    log = get_logger()
    try:
      user_id = get_user_info_from_context(settings.JWT_SECRET, context)['user_id']
      log = log.bind(user_id=user_id, content_length=len(request.content))
      new_tweet = Tweet.post(user_id=user_id, content=request.content,
                             latitude=request.latitude, longtitude=request.longtitude)
      result = TweetReply(tweet=to_proto_tweet(new_tweet))
    except ValueError as err:
      context.set_details(str(err))
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
    except Exception as err:
      context.set_code(grpc.StatusCode.INTERNAL)
      context.set_details(str(err))
    finally:
      handle_resp('tweet', context, log)
      return result






  # the following methods use HandleGenericError



  @Authenticator(response_class=EmptyReply, jwt_key=settings.JWT_SECRET)
  @HandleGenericError(response_class=EmptyReply)
  def DeleteTweet(self, request, context):
    """Delete a tweet"""
    try:
      tweet_id = request.tweet_id
      user_info = get_user_info_from_context(settings.JWT_SECRET, context)
      Tweet.delete(user_info['user_id'], tweet_id)
      return EmptyReply()
    except NoResultFound as err:
      context.set_details("No permission to delete")
      context.set_code(grpc.StatusCode.PERMISSION_DENIED)


  @HandleGenericError(response_class=TweetReply)
  def GetTweet(self, request, context):
    """Get a single tweet by tweet ID"""
    try:
      tweet_id = request.tweet_id
      session = session_maker()
      tweet = session.query(Tweet). \
        filter(Tweet.id == tweet_id). \
        filter(Tweet.deleted_at == None).one()
      return TweetReply(tweet=to_proto_tweet(tweet))
    except NoResultFound as err:
      context.set_details(f"No tweet with ID {tweet_id}")
      context.set_code(grpc.StatusCode.NOT_FOUND)

  @HandleGenericError(response_class=TweetReply, is_stream=True)
  def GetTweets(self, request, context):
    """Stream a list of tweets"""
    user_id = request.user_id
    offset = request.offset
    limit = request.limit
    created_at = request.created_at.ToDatetime()
    if limit > 100:
      context.set_details(f"Limit must be <100; got {limit}")
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
    elif offset < 0:
      context.set_details(f"Offset must be >0; got {offset}")
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
    else:
      for db_tweet in Tweet.get_tweets(user_id, created_at, offset, limit):
        yield TweetReply(tweet=to_proto_tweet(db_tweet))


  @Authenticator(response_class=TweetReply, jwt_key=settings.JWT_SECRET, is_stream=True)
  @HandleGenericError(response_class=TweetReply, is_stream=True)
  def Spam(self, request_iterator, context):
    """Post a list of tweets and stream back the db tweets"""
    user_id = get_user_info_from_context(settings.JWT_SECRET, context)['user_id']
    for tweet in request_iterator:
      db_tweet = Tweet.post(user_id=user_id, content=tweet.content,
                            latitude=tweet.latitude, longtitude=tweet.longtitude)
      yield TweetReply(tweet=to_proto_tweet(db_tweet))
