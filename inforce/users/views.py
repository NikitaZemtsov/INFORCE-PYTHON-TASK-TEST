from flask import Blueprint
from inforce import session, logger, docs
from inforce.schemas import UserSchema, AuthSchema, LoginSchema
from flask_apispec import use_kwargs, marshal_with
from inforce.models import UserModel, take_role
from flask_jwt_extended import jwt_required, current_user, get_jwt_header, get_jwt_identity

users = Blueprint('users', __name__)


@users.route("/register", methods=["POST"])
@jwt_required(optional=True)
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    """
    Endpoint add user to UserModel.
    """
    user_id = get_jwt_identity()
    try:
        user = UserModel(**kwargs)
        role = take_role(**kwargs) if get_jwt_identity() and (current_user.role[0].name == "admin") else take_role()
        user.role.append(role)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as err:
        logger.warning(f"user_id:{user_id}, register - registration action failed with error: {err}")
        return {"msg": str(err)}, 400
    return {"access_token": token}, 201


@users.route("/login", methods=["POST"])
@use_kwargs(LoginSchema)
@marshal_with(AuthSchema)
def login(**kwargs):
    """
    Endpoint login user.
    """
    try:
        user = UserModel.authenticate(**kwargs)
        token = user.get_token()
    except Exception as err:
        logger.warning(f"login - login with email: {kwargs.get('email')} failed with error: {err}")
        return {"msg": str(err)}, 400
    return {"access_token": token}, 202


@users.errorhandler(422)
def error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"invalid input params: {messages}")
    if headers:
        return {"msg": messages}, 400, headers
    else:
        return {"msg": messages}, 400


docs.register(register, blueprint="users")
docs.register(login, blueprint="users")
