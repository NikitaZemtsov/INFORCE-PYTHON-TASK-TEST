import datetime

from app import app, db
from models import UserModel,  RoleModel, RestaurantModel, DishModel, take_role, restaurant_access, admin_access
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime


@app.route("/register", methods=["POST"])
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
    role = take_role(**params)
    user.role.append(role)
    db.session.add(user)
    db.session.commit()
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


@app.route("/add_restaurant", methods=["POST"])
@jwt_required()
def add_restaurant():
    """Endpoint add restaurant to RestaurantModel.
         request:
            Json param:
                required:
                        "name"
            request example:
                            { "name": "name", "email":"email"}
         return
            Json param:
                required:
                        "restaurant_slug" - unique identificator
         response:
                201:
                    json:
                        {"restaurant_slug":"slug"}
        """
    params = request.json
    restaurant = RestaurantModel(**params)
    restaurant.users.append(current_user)
    db.session.add(restaurant)
    db.session.commit()
    return jsonify({"restaurant_slug": restaurant.slug}), 201


@app.route("/add_access_user", methods=["POST"])
@jwt_required()
def add_access_user():
    """Endpoint grant access to the user to "add_menu" for the restaurant.
         request:
            Json param:
                required:
                        "slug" - unique restaurant slag
                        "email" - user to whom access is granted

            request example:
                            { "slug": "slug", "email":"email"}

                {"restaurant_slug": slug, "email": email}
         response:
                201:
                    json:
                        {"restaurant_slug":"slug", "email": "email"}
            """
    params = request.json
    email = params.get("email")
    q_slug = params.get("slug")
    restaurant = restaurant_access()
    if restaurant.slug == q_slug:
        user = UserModel.query.filter_by(email=email).first()
        restaurant.users.append(user)
        db.session.commit()
        return jsonify({"restaurant_slug": q_slug, "email": email}), 201
    return jsonify({"msg": "This action is not available to you"}), 403


@app.route("/add_menu", methods=["POST"])
@jwt_required()
def add_menu():
    """Endpoint add menu to DishModel.
     If "timedelta" is True add this menu available for period from "DD.MM.YYYY" to "DD.MM.YYYY" + "timedelta"
    Json param:
        required:
                "restaurant"
                "YYYY.MM.DD" - Date with which this menu is available
                "dishes"
                "dish_0"
        not required:
                "timedelta":"days" - period of dish`s life(available)
    request example:
                    { "restaurant": "slug",
                      "YYYY-MM-DD":{"timedelta":"DD",                 # ?????????? ????????????????????????????????. ???????? ?????????? ???????? ???? ????????.
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
    menu = request.json
    restaurant = menu.get("restaurant")
    if restaurant != current_user.restaurant.slug:
        return jsonify({"msg":"You do not have access to the restaurant {}".format(restaurant)}), 403
    date = DishModel.take_date(menu)
    menu_for_date = menu.get(str(date))
    # menu_timedelta = menu_for_date.get("timedelta") Preparation for creating a menu for a certain period
    dishes = menu_for_date.get("dishes")
    dishes_to_commit = []
    for dish in dishes:
        dish_dict = dishes.get(dish)
        new_dish = DishModel(date=date, restaurant=current_user.restaurant, **dish_dict)
        dishes_to_commit.append(new_dish)
    db.session.add_all(dishes_to_commit)
    db.session.commit()
    return jsonify(), 204


@app.route("/create_employee", methods=["POST"])
@jwt_required()
def create_employee():
    """Endpoint create user with employee role.
             request:
                Json param:
                    required:
                            "first_name"
                            "last_name"
                            "email"
                            "password"
                            "role":"employee" - required value param
                request example:
                                { "first_name": "first_name",
                                "last_name": "last_name",
                                "password": ""password""
                                "email":"email",
                                "role":"employee" }
             response:
                    201:
                        json:
                            {"access":"token"}
                """
    params = request.json
    user = UserModel(**params)
    db.session.add(user)
    token = user.get_token()
    db.session.commit()
    return jsonify({"access_token": token}), 201


@app.route("/menu", methods=["GET"])
@app.route("/menu/<date>", methods=["GET"])
@jwt_required()
def menu(date=datetime.utcnow().date()):
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
    dishes = DishModel.query.filter_by(date=datetime(2022, 12, 11)).all()
    i = 0
    menu = {}
    for d in dishes:
        menu["dish-{}".format(i)] = d.dish_dict
        i += 1
    return jsonify(menu), 200
