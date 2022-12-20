from flask import Blueprint, request, jsonify
from inforce import session, logger, docs
from inforce.view import take_date
from inforce.schemas import RestaurantSchema, DishesSchema, OrderSchema
from flask_apispec import use_kwargs, marshal_with
from inforce.models import RestaurantModel, DishModel
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity

restaurant_app = Blueprint("restaurant_app", __name__)


@restaurant_app.route("/restaurants", methods=["POST"])
@jwt_required()
@use_kwargs(RestaurantSchema)
@marshal_with(RestaurantSchema(only=["slug"]))
def restaurants(**kwargs):
    """
    Endpoint add restaurant to RestaurantModel.
    """
    user_id = get_jwt_identity()
    if request.method == "POST":
        try:
            restaurant = RestaurantModel(**kwargs)
            restaurant.users.append(current_user)
            session.add(restaurant)
            session.commit()
        except Exception as err:
            logger.warning(f"user_id:{user_id}, restaurants - add restaurant action failed with error: {err}")
            return {"msg": str(err)}, 400
        return restaurant, 201


@restaurant_app.route("/restaurants/<restaurant_slug>/menu", methods=["POST"])
@jwt_required()
@use_kwargs(DishesSchema(many=True))
def menu(*args, restaurant_slug):
    """
    Endpoint add menu to DishModel.
    """
    user_id = get_jwt_identity()
    if request.method == "POST":
        try:
            if restaurant_slug != current_user.restaurant.slug:
                return jsonify({"msg": "You do not have access to the restaurant {}".format(restaurant_app)}), 403
            menu_date_period = take_date(request.args.get('date_period'))
            dishes_to_commit = []
            for date in menu_date_period:
                for dish in args:
                    new_dish = DishModel(date=date, restaurant=current_user.restaurant, **dish)
                    dishes_to_commit.append(new_dish)
            session.add_all(dishes_to_commit)
            session.commit()
        except Exception as err:
            logger.warning(f"user_id:{user_id}, restaurant_slug:{restaurant_slug}, add menu - add menu action failed with error: {err}")
            return {"msg": str(err)}, 400
        return {}, 204


@restaurant_app.route("/order", methods=["GET"])
@jwt_required()
@marshal_with(OrderSchema(many=True))
def order():
    """
    Result of today votes
    :return: List of dishes with vote count
    """
    user_id = get_jwt_identity()
    try:
        date_period = take_date(request.args.get("date_period"))
        dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
        return dishes, 200
    except Exception as err:
        logger.warning(f"user_id:{user_id}, voting -  voting action failed with error: {err}")
        return {"msg": str(err)}, 400


@restaurant_app.errorhandler(422)
def error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"invalid input params: {messages}")
    if headers:
        return {"msg": messages}, 400, headers
    else:
        return {"msg": messages}, 400


docs.register(restaurants, blueprint="restaurant_app")
docs.register(menu, blueprint="restaurant_app")
docs.register(order, blueprint="restaurant_app")
