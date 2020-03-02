import grpc
import sys

from random import randint
sys.path.append("/ws-py/pp-orm")
sys.path.append("/ws-py/pp-protos")
sys.path.append("/ws-py/pp-config")

from datetime import datetime
from google.protobuf import json_format
from google.protobuf.timestamp_pb2 import Timestamp
from tweet_pb2_grpc import TweetStub
from tweet_types_pb2 import DeleteTweetRequest
from tweet_types_pb2 import GetTweetRequest
from tweet_types_pb2 import GetTweetsRequest
from tweet_types_pb2 import TweetReply
from tweet_types_pb2 import TweetRequest





class Token(object):
  emma   = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJlbW1hQGdtYWlsLmNvbS'\
           'IsInVzZXJfaWQiOjF9LCJleHAiOjE1NTQzNTYxNDB9.Lprcm2gWhSHM0ox5zfaRxTDAGE_zTQRGRTCB7cXY45I'
  chen   = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJjaGVuQGdtYWlsLmNvbS'\
           'IsInVzZXJfaWQiOjJ9LCJleHAiOjE1NTQzOTkwNzN9.j8gzJMXarxav8LahKU_PJDg7NkyGeHX_8-f2e5bgBGs'
  winter = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJ3aW50ZXJAZ21haWwuY2'\
           '9tIiwidXNlcl9pZCI6M30sImV4cCI6MTU1NDQyMzkwM30.-ThI7M9UB0u3WqGvk8EA3_d5zENAt3rIoRjDxXDe2HA'
  bad    = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJ3aW50ZXJAZ21haWwuY2'\
           '9tIiwidXNlcl9pZCI6M30sImV4cCI6MTU1NDQyMzkwM30.-ThI7M9UB0u3WqGvk8EA3_d5zENAt3rIoRjDxXDe2HA'
  test   = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJoYXJwZXJAZ21haWwuY29tIiwidXNlcl9pZCI6MTg5OH0sImV4cCI6MTU1NTAwNjA2NX0.y_F75pTXzAACSV9JYWgDJzg8hfvMDLFCEcWEBrSo25o'


def generate_text():
  with open("./short_text", "r") as file:
    for line in file:
      line = line.strip()
      num = randint(150, 250)
      index = 0
      while index < len(line):
        content = line[index:index+num]
        latitude, longtitude = round(randint(-10000, 10000)/100, 3), round(randint(-10000, 10000)/100, 3)
        yield TweetRequest(content=content, latitude=latitude, longtitude=longtitude)
        index += num

class HandleError(object):
  def __call__(self, callback):
    def _handle_error(instance, **args):
      try:
        res = callback(instance, **args)
        if res:
          return json_format.MessageToDict(res)
      except grpc.RpcError as err:
        print('details    =', err.details())
        print('code.name  =', err.code().name)
        print('code.value =', err.code().value)
    return _handle_error


class Client(object):
  def __init__(self, session_token):
    self.channel = grpc.insecure_channel('localhost:50052')
    self.service = TweetStub(self.channel)
    self._auth = [('session_token', session_token)]

  @HandleError()
  def tweet(self, content):
    tweet_request = TweetRequest(content=content, latitude=40.685536, longtitude=-73.951705)
    return self.service.Tweet(tweet_request, metadata=self._auth)

  @HandleError()
  def delete(self, tweet_id):
    req = DeleteTweetRequest(tweet_id=tweet_id)
    return self.service.DeleteTweet(req, metadata=self._auth)

  @HandleError()
  def get_tweet(self, tweet_id):
    req = GetTweetRequest(tweet_id=tweet_id)
    return self.service.GetTweet(req)

  @HandleError()
  def get_tweets(self, user_id, offset, limit, created_at):
    time = Timestamp()
    time.FromDatetime(created_at)
    request = GetTweetsRequest(user_id=user_id, offset=offset, limit=limit, created_at=time)
    return self.service.GetTweets(request)

  @HandleError()
  def spam(self, content_iterator):
    for record in self.service.Spam(content_iterator, metadata=self._auth):
      record = json_format.MessageToDict(record)
      print(record)


if __name__ == '__main__':

  client = Client(Token.test)
  r = client.tweet(content="test")
  print(r)
  # r = client.delete(tweet_id=1)


  # print('get')
  # r = client.get_tweet(tweet_id=5)
  # print(r)

  # client.spam(content_iterator=generate_text())

  # time = datetime.fromisoformat("2019-03-03 19:01:22.223144")
  # for item in client.get_tweets(user_id=3, offset=10000, limit=100, created_at=time):
  #   print("---------------")
  #   item = json_format.MessageToDict(item)
  #   print(item['tweet']['content'])
