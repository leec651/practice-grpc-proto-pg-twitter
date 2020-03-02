import grpc
import jwt
import sys
sys.path.append("/ws-py/pp-orm")
sys.path.append("/ws-py/pp-config")

from config import settings
from datetime import datetime
from datetime import timezone
from google.protobuf import json_format
from orm import Session
from orm import User
from protos import user_pb2_grpc as user_grpc
from protos.user_types_pb2 import EmptyReply
from protos.user_types_pb2 import FollowRequest
from protos.user_types_pb2 import GetUserRequest
from protos.user_types_pb2 import LoginRequest
from protos.user_types_pb2 import SignUpRequest
from protos.user_types_pb2 import UnfollowRequest


def handle_error(callback):
  def _handle_error(instance, **args):
    try:
      res = callback(instance, **args)
      return json_format.MessageToDict(res)
    except grpc.RpcError as err:
      print('details    =', err.details())
      print('code.name  =', err.code().name)
      print('code.value =', err.code().value)
  return _handle_error


class Client(object):
  def __init__(self, session_token):
    # connect to gRPC user service
    self.channel = grpc.insecure_channel('localhost:50051')
    self.service = user_grpc.UserStub(self.channel)
    self._auth = [('session_token', session_token)]

  @handle_error
  def sign_up(self, email, password, phone, name):
    request = SignUpRequest(email=email, password=password, phone=phone, name=name)
    return self.service.SignUp(request)

  @handle_error
  def get_user(self, user_id):
    return self.service.GetUser(GetUserRequest(user_id=user_id))

  @handle_error
  def login(self, email, password):
    return self.service.Login(LoginRequest(email=email, password=password))

  @handle_error
  def follow(self, followee_id):
    req = FollowRequest(followee_user_id=followee_id)
    return self.service.Follow(req, metadata=self._auth)

  @handle_error
  def unfollow(self, followee_id):
    req = UnfollowRequest(followee_user_id=followee_id)
    return self.service.Unfollow(req, metadata=self._auth)



if __name__ == '__main__':
  emma_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJlbW1hQGdtYWlsLmNvbSIsInVzZXJfaWQiOjF9LCJleHAiOjE1NTQzNTYxNDB9.Lprcm2gWhSHM0ox5zfaRxTDAGE_zTQRGRTCB7cXY45I'
  chen_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2luZm8iOnsiZW1haWwiOiJjaGVuQGdtYWlsLmNvbSIsInVzZXJfaWQiOjJ9LCJleHAiOjE1NTQzOTkwNzN9.j8gzJMXarxav8LahKU_PJDg7NkyGeHX_8-f2e5bgBGs'

  client = Client(emma_token)
  # resp = client.sign_up(email="emma@gmail.com",
  #                       password="fake_password",
  #                       phone="2063542951",
  #                       name="emma lin")
  # resp = client.sign_up(email="chen@gmail.com",
  #                       password="fake_password",
  #                       phone="2063542951",
  #                       name="chen wei lee")
  # resp = client.sign_up(email="winter@gmail.com",
  #                       password="fake_password",
  #                       phone="2063542951",
  #                       name="winter darling")
  # resp = client.sign_up(email="spring@gmail.com",
  #                       password="fake_password",
  #                       phone="2063542951",
  #                       name="spring darling")

  # resp = client.get_user(user_id=7)

  resp = client.login(email="winter@gmail.com", password="fake_password")


  # resp = client.follow(followee_id=8)


  print(resp)


  # r = jwt.decode(resp['token'], settings.JWT_SECRET, algorithms=['HS256'])
  # print(r)





