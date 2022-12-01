import datetime
import pandas as pd
from app import app, db, session
from models import UserModel,  RoleModel, RestaurantModel, DishModel, take_role
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt_header, get_jwt_identity
from datetime import datetime, timedelta


@app.route("/register", methods=["POST"])
@jwt_required(optional=True)
def register():
    """Endpoint add user to UserModel.
         request:
            Json param:
                required:
                        "first_name"
                        "last_name"
                        "email"
                        "password"
            request example:
                            { "first_name": "first_name",
                              "last_name": "last_name",
                              "email":"email",
                              "password":"password"}
         response:
                200:
                    json:
                        {"access":"token"}
            """
    params = request.json
    user = UserModel(**params)
    role = take_role(**params) if get_jwt_identity() and (current_user.role[0].name == "admin") else take_role()
    user.role.append(role)
    session.add(user)
    session.commit()
    token = user.get_token()
    return jsonify({"access_token": token}), 201


@app.route("/login", methods=["POST"])
def login():
    """Endpoint login user.
               required:
                        "email"
                        "password"
                    request example:
                                    { "email":"email",
                                      "password":"password"}
                response:
                        202:
                            json:
                                {"access":"token"}
                """
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    try:
        user = UserModel.authenticate(email=email, password=password)
    except Exception:
        return jsonify({"msg": "Bad username or password"}), 401

    return jsonify(access_token=user.get_token()), 202


@app.route("/restaurants", methods=["POST"])
@jwt_required()
def restaurant():
    """Endpoint add restaurant to RestaurantModel.
         request:
            POST
            Json param:
                required:
                        "name"
            request example:
                            { "name": "name"}
         return
            Json param:
                required:
                        "restaurant_slug" - unique identificator
         response:
                201:
                    json:
                        {"restaurant_slug":"slug"}
        """
    if request.method == "POST":
        params = request.json
        restaurant = RestaurantModel(**params)
        restaurant.users.append(current_user)
        session.add(restaurant)
        session.commit()
        return jsonify({"restaurant_slug": restaurant.slug}), 201


# @app.route("/add_access_user", methods=["POST"])
# @jwt_required()
# def add_access_user():
#     """Endpoint grant access to the user to "add_menu" for the restaurant.
#          request:
#             Json param:
#                 required:
#                         "slug" - unique restaurant slag
#                         "email" - user to whom access is granted
#
#             request example:
#                             { "slug": "slug", "email":"email"}
#
#                 {"restaurant_slug": slug, "email": email}
#          response:
#                 201:
#                     json:
#                         {"restaurant_slug":"slug", "email": "email"}
#             """
#     params = request.json
#     email = params.get("email")
#     q_slug = params.get("slug")
#     restaurant = restaurant_access()
#     if restaurant.slug == q_slug:
#         user = UserModel.query.filter_by(email=email).first()
#         restaurant.users.append(user)
#         db.session.commit()
#         return jsonify({"restaurant_slug": q_slug, "email": email}), 201
#     return jsonify({"msg": "This action is not available to you"}), 403


@app.route("/restaurant/<restaurant_slug>/menu", methods=["POST"])
@jwt_required()
def menu(restaurant_slug):
    """Endpoint add menu to DishModel.
     If "timedelta" is True add this menu available for period from "DD.MM.YYYY" to "DD.MM.YYYY" + "timedelta"
    Json param:
        required:
                "YYYY.MM.DD" - Date with which this menu is available
                "dishes"
                "dish_0"
        not required:
                "timedelta":"days" - period of dish`s life(available)
    request example:
                      {"YYYY-MM-DD":{"timedelta":"DD",                 # Может масштабироваться. Дата может быть не одна.
                                     "dishes":{"dish_0":{"name":"name",
                                                         "description":"description"},
                                               "dish_1":{"name":"name",
                                                         "description":"description"}
                                                                                    ...}}}
     response:
        204:
            json:
                {}
        """
    if request.method == "POST":
        restaurant = restaurant_slug
        if restaurant != current_user.restaurant.slug:
            return jsonify({"msg": "You do not have access to the restaurant {}".format(restaurant)}), 403
        menu = request.json
        menu_date_period = take_date(request.args.get('date_period'))
        dishes_to_commit = []
        for date in menu_date_period:
            for _, dish in menu.items():
                new_dish = DishModel(date=date, restaurant=current_user.restaurant, **dish)
                dishes_to_commit.append(new_dish)
        session.add_all(dishes_to_commit)
        session.commit()
        return jsonify(), 204


@app.route("/menu", methods=["GET"])
@app.route("/menu/<dish_id>", methods=["POST"])
@jwt_required()
def menu_vote(dish_id=None):
    """Endpoint respond today menu.
                request:
                   slug:
                       not required:
                                    /<YYYY-MM-DD> - response  menu by date
                   request example:
                                   /menu - today menu
                                   /menu/2022-12-11 - menu on date
                response:
                        200:
                            json:
                               {"dish_0":{"name":"name",
                                         "description":"description"},
                                "dish_1":{"name":"name",
                                         "description":"description"....}
    """
    if current_user.role[0].name == "restaurant":
        return jsonify({"msg": "You do not have access to do this"}), 403
    if request.method == "GET":
        date_period = take_date(request.args.get("date_period"))
        dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
        i = 0
        menu = {}
        for d in dishes:
            menu["dish-{}".format(i)] = d.dish_represent
            i += 1
        return jsonify(menu), 200
    if request.method == "POST":
        dish = DishModel.query.filter_by(id=int(dish_id)).first()
        dish.user.append(current_user)
        session.add(dish)
        session.commit()
        return jsonify({"user": current_user.first_name,
                        "dish": f"{dish.id} - {dish.name}"}), 200


@app.route("/order", methods=["GET"])
@jwt_required()
def order():
    date_period = take_date(request.args.get("date_period"))
    dishes = DishModel.query.where(DishModel.date.in_(date_period)).all()
    i = 0
    menu = {}
    for d in dishes:
        count = len(d.user)
        dish_dict = d.dish_represent
        dish_dict["count"]= count
        menu["dish-{}".format(i)] = dish_dict
        i += 1
    return jsonify(menu), 200


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
