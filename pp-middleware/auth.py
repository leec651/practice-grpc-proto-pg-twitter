import grpc
import jwt

from structlog import get_logger

_SESSION_TOKEN_ERROR = 'Invalid session_token'
_SESSION_TOKEN_EXPIRED = 'Expired session_token'
_SESSION_TOKEN_UNKNOWN = 'Unable to read session_token'


def get_user_info_from_context(jwt_key, context):
  """Return encoded user info from context"""
  session_token = dict(context.invocation_metadata())['session_token']
  return jwt.decode(session_token, key=jwt_key).get('user_info')



class Authenticator(object):
  """Decorator as auth middleware. It would be nice if I can set the decoded jwt to md"""

  def __init__(self, response_class, jwt_key, is_stream=False):
    """Response class will be used to initialize and return an empty obj if authentication fails"""
    self.response_class = response_class
    self.jwt_key = jwt_key
    self.is_stream = is_stream
    self.log = get_logger()

  def __call__(self, func):
    """Decorator code"""
    def _jwt_authenticator(instance, request, context):
      has_error, details = self.__do_authentication(context)
      if has_error:
        # Return an generic permission denied error
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        context.set_details(details)
        self.log.error(f'{func.__name__.lower()}', result=grpc.StatusCode.PERMISSION_DENIED.name)
        if self.is_stream:
          return iter(())
        else:
          return self.response_class()
      else:
        return func(instance, request, context)
    return _jwt_authenticator

  def __do_authentication(self, context):
    """Attempt to decode the JWT token"""
    try:
      metadata = dict(context.invocation_metadata())
      session_token = metadata['session_token']
      self.log = self.log.bind(session_token=session_token)
      return False, jwt.decode(session_token, key=self.jwt_key)['user_info']
    except KeyError:
      self.log = self.log.bind(error=_SESSION_TOKEN_ERROR)
      return True, _SESSION_TOKEN_ERROR
    except jwt.DecodeError:
      self.log = self.log.bind(error=_SESSION_TOKEN_ERROR)
      return True, _SESSION_TOKEN_ERROR
    except jwt.ExpiredSignatureError:
      self.log = self.log.bind(error=_SESSION_TOKEN_EXPIRED)
      return True, _SESSION_TOKEN_EXPIRED
    except BaseException:
      self.log = self.log.bind(error=_SESSION_TOKEN_UNKNOWN)
      return True, _SESSION_TOKEN_UNKNOWN