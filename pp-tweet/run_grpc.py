import sys
sys.path.append("/ws-py/pp-orm")
sys.path.append("/ws-py/pp-middleware")
sys.path.append("/ws-py/pp-config")
sys.path.append("/ws-py/pp-protos")

import grpc
import logging
import time
import tweet_pb2_grpc as tweet_grpc

from concurrent import futures
from service import TweetService

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def _unary_unary_rpc_terminator():
  def terminate(ignored_request, context):
    context.abort(grpc.StatusCode.PERMISSION_DENIED, "Invalid access jwt token")
  return grpc.unary_unary_rpc_method_handler(terminate)

class AuthenticationInterceptor(grpc.ServerInterceptor):
  def intercept_service(self, continuation, details):
    session_token = dict(details.invocation_metadata)['session_token']
    # TODO: we can move the auth code here instead of using a decorator
    return continuation(details)


def run():
  # create an interceptor
  interceptors = [AuthenticationInterceptor()]
  # create a grpc server and gives it some threads
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors)
  # associate my tweet service to serer
  tweet_grpc.add_TweetServicer_to_server(TweetService(), server)
  # add port
  server.add_insecure_port('[::]:50052')
  # start the server
  server.start()

  print(f"Start {TweetService.__name__}...")
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == '__main__':
  logging.basicConfig()
  run()

