import datetime
import pandas as pd
from app import app, db, session, docs
from models import UserModel,  RoleModel, RestaurantModel, DishModel, take_role
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt_header, get_jwt_identity
from datetime import datetime, timedelta
from schemas import UserSchema, AuthSchema, RestaurantSchema, LoginSchema, DishesSchema, OrderSchema
from flask_apispec import use_kwargs, marshal_with


@app.route("/register", methods=["POST"])
@jwt_required(optional=True)
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    """
    Endpoint add user to UserModel.
    """
    user = UserModel(**kwargs)
    role = take_role(**kwargs) if get_jwt_identity() and (current_user.role[0].name == "admin") else take_role()
    user.role.append(role)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {"access_token": token}, 201


@app.route("/login", methods=["POST"])
@use_kwargs(LoginSchema)
@marshal_with(AuthSchema)
def login(**kwargs):
    """
    Endpoint login user.
    """
    try:
        user = UserModel.authenticate(**kwargs)
    except Exception:
        return {"msg": "Bad username or password"}, 401
    token = user.get_token()
    return {"access_token": token}, 202


@app.route("/restaurants", methods=["POST"])
@jwt_required()
@use_kwargs(RestaurantSchema)
@marshal_with(RestaurantSchema(only=["slug"]))
def restaurant(**kwargs):
    """
    Endpoint add restaurant to RestaurantModel.
    """
    if request.method == "POST":
        restaurant = RestaurantModel(**kwargs)
        restaurant.users.append(current_user)
        session.add(restaurant)
        session.commit()
        return restaurant, 201


@app.route("/restaurant/<restaurant_slug>/menu", methods=["POST"])
@jwt_required()
@use_kwargs(DishesSchema(many=True))
def menu(*args, restaurant_slug):
    """
    Endpoint add menu to DishModel.
    """
    if request.method == "POST":
        if restaurant_slug != current_user.restaurant.slug:
            return jsonify({"msg": "You do not have access to the restaurant {}".format(restaurant)}), 403
        menu_date_period = take_date(request.args.get('date_period'))
        dishes_to_commit = []
        for date in menu_date_period:
            for dish in args:
                new_dish = DishModel(date=date, restaurant=current_user.restaurant, **dish)
                dishes_to_commit.append(new_dish)
        session.add_all(dishes_to_commit)
        session.commit()
        return {}, 204


@app.route("/menu", methods=["GET"])
@jwt_required()
@marshal_with(DishesSchema(many=True, only=["date", "description", "id", "name"]))
def menu_list(dish_id=None):
    """
        Endpoint respond today menu.
    """
    if current_user.role[0].name == "restaurant":
        return jsonify({"msg": "You do not have access to do this"}), 403
    if request.method == "GET":
        date_period = take_date(request.args.get("date_period"))
        dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
        return dishes, 200


@app.route("/menu/<dish_id>", methods=["POST"])
@jwt_required()
def menu_vote(dish_id=None):
    """
    Voting for dish.

    """
    if current_user.role[0].name == "restaurant":
        return jsonify({"msg": "You do not have access to do this"}), 403
    if request.method == "POST":
        dish = DishModel.query.filter_by(id=int(dish_id)).first()
        dish.user.append(current_user)
        session.add(dish)
        session.commit()
        return jsonify({"user": current_user.first_name,
                        "name": dish.name}), 200


@app.route("/order", methods=["GET"])
@jwt_required()
@marshal_with(OrderSchema(many=True))
def order():
    """
    Result of today votes
    :return: List of dishes with vote count
    """
    date_period = take_date(request.args.get("date_period"))
    dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
    return dishes, 200


docs.register(register)
docs.register(login)
docs.register(restaurant)
docs.register(menu)
docs.register(menu_list)
docs.register(menu_vote)
docs.register(order)


def take_date(row_date) -> list:
    if row_date is None:
        print()
        return [datetime.utcnow().date()]
    else:
        dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in row_date.split(",")]
        if len(dates) == 2:
            start_date, end_date = dates
            return list(pd.date_range(start=start_date, end=end_date, freq="D"))
        else:
            return dates
