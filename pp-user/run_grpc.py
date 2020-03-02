import sys
sys.path.append("/ws-py/pp-orm")
sys.path.append("/ws-py/pp-protos")
sys.path.append("/ws-py/pp-config")
sys.path.append("/ws-py/pp-middleware")

import grpc
import logging
import time
import user_pb2_grpc

from concurrent import futures
from service import UserService
from util.cli import print_cli_art

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def run():
  # create a grpc server and gives it some threads
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  # associate my user service to serer
  user_pb2_grpc.add_UserServicer_to_server(UserService(), server)
  # add port
  server.add_insecure_port('[::]:50051')
  # start the server
  server.start()

  print(f"Start {UserService.__name__}...")
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == '__main__':
  logging.basicConfig()
  run()
