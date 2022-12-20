from flask import Blueprint, request, jsonify
from inforce import session, logger, docs
from inforce.view import take_date
from inforce.schemas import DishesSchema
from flask_apispec import marshal_with
from inforce.models import DishModel
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity

employee = Blueprint("employee", __name__)


@employee.route("/menu", methods=["GET"])
@jwt_required()
@marshal_with(DishesSchema(many=True, only=["date", "description", "id", "name"]))
def menu_list():
    """
        Endpoint respond today menu.
    """
    user_id = get_jwt_identity()
    try:
        if current_user.role[0].name == "restaurant":
            return jsonify({"msg": "You do not have access to do this"}), 403
        if request.method == "GET":
            date_period = take_date(request.args.get("date_period"))
            dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
            return dishes, 200
    except Exception as err:
        logger.warning(f"user_id:{user_id}, menu -  take menu action failed with error: {err}")
        return {"msg": str(err)}, 400


@employee.route("/menu/<dish_id>", methods=["POST"])
@jwt_required()
def menu_vote(dish_id=None):
    """
    Voting for dish.

    """
    user_id = get_jwt_identity()
    try:
        if current_user.role[0].name == "restaurant":
            return jsonify({"msg": "You do not have access to do this"}), 403
        if request.method == "POST":
            dish = DishModel.query.filter_by(id=int(dish_id)).first()
            dish.user.append(current_user)
            session.add(dish)
            session.commit()
            return jsonify({"user": current_user.first_name,
                            "name": dish.name}), 200
    except Exception as err:
        logger.warning(f"user_id:{user_id}, dish_id:{dish_id}, voting -  voting action failed with error: {err}")
        return {"msg": str(err)}, 400


@employee.errorhandler(422)
def error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"invalid input params: {messages}")
    if headers:
        return {"msg": messages}, 400, headers
    else:
        return {"msg": messages}, 400


docs.register(menu_list, blueprint="employee")
docs.register(menu_vote, blueprint="employee")
