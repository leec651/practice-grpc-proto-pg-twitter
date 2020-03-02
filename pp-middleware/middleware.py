import grpc
import traceback

from sqlalchemy.exc import SQLAlchemyError
from structlog import get_logger

class HandleGenericError(object):
  """Handle generic error to remove duplicate code.
  It will return empty object if error is thrown"""
  def __init__(self, response_class, is_stream=False):
    self.response_class = response_class
    self.is_stream = is_stream

  def __call__(self, func):
    def _handle_generic_error(instance, request, context):
      try:
        return func(instance, request, context)
      except SQLAlchemyError as err:
        # in reality, we won't propagate error message to user
        context.set_details(str(err))
        context.set_code(grpc.StatusCode.INTERNAL)
      except Exception as err:
        print(type(err))
        traceback.print_tb(err.__traceback__)
        # in reality, we won't propagate error message to user
        context.set_details(str(err))
        context.set_code(grpc.StatusCode.UNKNOWN)
      finally:
        if context._state.code and context._state.code != grpc.StatusCode.OK:
          if self.is_stream:
            return iter(())
          else:
            return self.response_class()
    return _handle_generic_error


def handle_resp(name, context, log):
  if context._state.code and context._state.code.name != 'OK':
    log = log.bind(result=context._state.code.name)
    # normally this should be ok since it's a user error
    log.error(name, method=name)
  else:
    log = log.bind(result='OK')
    log.info(name, method=name)