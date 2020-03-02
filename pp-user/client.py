import sys
sys.path.append("/ws-py/pp-orm")
sys.path.append("/ws-py/pp-protos")
sys.path.append("/ws-py/pp-config")
sys.path.append("/ws-py/pp-middleware")

import asyncio
import data
import grpc
import traceback
import user_pb2_grpc as user_grpc

from concurrent.futures import ThreadPoolExecutor
from random import randint
from tweet_pb2_grpc import TweetStub
from user_pb2_grpc import UserStub
from user_types_pb2 import SignUpRequest

# create channels
user_channel = grpc.insecure_channel('localhost:50051')
tweet_channel = grpc.insecure_channel('localhost:50052')
# create services
user_stub = UserStub(user_channel)
tweet_stub = TweetStub(tweet_channel)


async def setup():
  loop = asyncio.get_event_loop()
  futures = []
  for name in data.names:
    req = SignUpRequest(name=name, password=f'{name}{name}', email=f'{name}@gmail.com')
    futures.append(loop.run_in_executor(None, user_stub.SignUp, req))
  await asyncio.gather(*futures)

def initial_setup():
  loop = asyncio.get_event_loop()
  print('Start initial setup...')
  loop.run_until_complete(setup())
  print('Done initial setup')

class TaskMaker(object):
  def make(self):
    todo = self.tweet    # 90%
    if randint(1, 10) > 9:
      todo = self.signup # 10%
    return todo

  def tweet(self):
    try:
      # try to login
      _succeed = False if randint(1, 10) > 9 else True
      login_req = data.get_login_request(_succeed)
      res = user_stub.Login(login_req)

      # try to tweet
      _succeed = False if randint(1, 10) > 9 else True
      tweet_req = data.get_tweet(_succeed)
      tweet_stub.Tweet(tweet_req, metadata=[('session_token', res.token)])

    except Exception as err:
      print('details    =', err.details())
      print('code.name  =', err.code().name)
      print('code.value =', err.code().value)

  def signup(self):
    try:
      _succeed = False if randint(1, 10) > 9 else True
      req = data.get_signup_request(_succeed)
      res = user_stub.SignUp(req)
    except Exception as err:
      print('details    =', err.details())
      print('code.name  =', err.code().name)
      print('code.value =', err.code().value)


def run(first=False):
  if first: initial_setup()

  task_maker = TaskMaker()
  task = task_maker.make()
  task()

run()