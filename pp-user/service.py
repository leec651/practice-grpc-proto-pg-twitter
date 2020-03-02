import grpc

from auth import Authenticator
from auth import get_user_info_from_context
from config import settings
from datetime import datetime
from datetime import timezone
from middleware import HandleGenericError
from middleware import handle_resp
from orm import Follow
from orm import Session
from orm import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from structlog import get_logger
from user_pb2_grpc import UserServicer
from user_types_pb2 import EmptyReply
from user_types_pb2 import TokenReply
from user_types_pb2 import UserReply

def to_pb_user(db_user):
  """converts db user object to proto user object"""
  created_at = Timestamp()
  created_at.FromJsonString(db_user.created_at.isoformat())
  last_login_at = Timestamp()
  last_login_at.FromJsonString(db_user.last_login_at.isoformat())
  return ProtoUser(id=db_user.id, email=db_user.email, phone=db_user.phone,
                   name=db_user.name, latitude=db_user.latitude,
                   longtitude=db_user.longtitude, created_at=created_at,
                   last_login_at=last_login_at)


class UserService(UserServicer):
  """User service gRPC implementation"""

  def SignUp(self, request, context):
    """Creates a new db user object"""
    log = get_logger()
    result = TokenReply()
    try:
      log = log.bind(password=request.password, email=request.email)
      if len(request.password) < 6:
        raise ValueError(f"Password too short. Received length {request.password}")

      token = User.create(email=request.email.lower(), password=request.password,
                          phone=request.phone, name=request.name)
      if token:
        result = TokenReply(token=token)
    except IntegrityError as err:
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details(f"Duplicate email {request.email}")
    except ValueError as err:
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details(str(err))
    except Exception as err:
      context.set_code(grpc.StatusCode.INTERNAL)
      context.set_details(str(err))
    finally:
      handle_resp('signup', context, log)
      return result

  def Login(self, request, context):
    """Login user and return a JWT token if succeed"""
    log = get_logger()
    result = TokenReply()
    try:
      email = request.email.lower()
      password = request.password
      log = log.bind(email=email, method="login")
      token = User.login(email, password)
      if token:
        result = TokenReply(token=token)
    except NoResultFound as err:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details('Invalid username')
    except ValueError as err:
      context.set_code(grpc.StatusCode.PERMISSION_DENIED)
      context.set_details(str(err))
    except Exception as err:
      context.set_code(grpc.StatusCode.INTERNAL)
      context.set_details(str(err))
    finally:
      handle_resp('login', context, log)
      return result






  # other routes.... they use handle generic error decorator

  @HandleGenericError(response_class=UserReply)
  def GetUser(self, request, context):
    """Returns db user object for the input user ID"""
    user_id = request.user_id
    try:
      with Session() as session:
        user = session.query(User).filter(User.id == user_id).one()
        return UserReply(user=to_pb_user(user))
    except NoResultFound as err:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details(f"Unable to find user with ID {user_id}")


  @Authenticator(response_class=EmptyReply, jwt_key=settings.JWT_SECRET)
  @HandleGenericError(response_class=EmptyReply)
  def Follow(self, request, context):
    """Follow another user as the logged in user"""
    return self.__follow_helper(request, context, Follow.follow)


  @Authenticator(response_class=EmptyReply, jwt_key=settings.JWT_SECRET)
  @HandleGenericError(response_class=EmptyReply)
  def Unfollow(self, request, context):
    """Unfollow another user as the logged in user"""
    return self.__follow_helper(request, context, Follow.unfollow)


  def __follow_helper(self, request, context, func):
    """Helper function to reduce duplicate code for follow and unfollow routes"""
    followee_id = request.followee_user_id
    follower_id = get_user_info_from_context(settings.JWT_SECRET, context)["user_id"]
    if followee_id == follower_id:
      context.set_details("Cannot follow or unfollow yourself")
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
    else:
      try:
        func(follower_id, followee_id)
        return EmptyReply()
      except IntegrityError as err:
        context.set_details(f"No user found with ID {followee_id}")
        context.set_code(grpc.StatusCode.NOT_FOUND)