from main import app
import pytest
from models import RoleModel, RestaurantModel, DishModel, UserModel
from datetime import datetime
from conftest import user, roles


def test_roles(roles):
    assert len(roles) == 3
    assert roles[0].name == "restaurant"
    assert roles[1].name == "employee"
    assert roles[2].name == "admin"


def test_model(user):
    assert user.first_name == "Alex"
    assert user.role[0].name == 'restaurant'
    assert user.role[0].description == 'pass'


parametez_register = [{"first_name": "Bob",
                       "email": "Bob@gmail.com",
                       "last_name": "Bear",
                       "password": "2222"}]


@pytest.mark.parametrize("json", parametez_register)
def test_register(json, client):
    req = client.post("/register", json=json)
    assert req.status_code == 201
    assert req.json.get("access_token") != ""

parametez_register = [({"first_name": "Jack",
                       "email": "Jack@gmail.com",
                       "last_name": "Back",
                       "password": "2222",
                       "role": "employee"},{"code":201})]


@pytest.mark.parametrize("json, response", parametez_register)
def test_register_employee(json,response, user_admin, admin_headers, client):

    """test register user(admin) with access to add new employee"""

    req = client.post("/register", headers=admin_headers, json=json)
    assert req.status_code == response.get("code")
    assert req.json.get("access_token") != ""
    employee = UserModel.query.filter_by(email=json.get("email")).first()
    assert employee.role[0].name == json.get("role")
    assert employee.first_name == json.get("first_name")
    assert employee.last_name == json.get("last_name")


parametez_fall_register = [({"first_name": "Mack",
                       "email": "Mack@gmail.com",
                       "last_name": "Duck",
                       "password": "2222",
                       "role": "employee"}, {"code":201})]


@pytest.mark.parametrize("json, response", parametez_fall_register)
def test_fall_register_employee(json, response, user_headers, client):

    """test register user without access to add new employee"""

    req = client.post("/register", headers=user_headers, json=json)
    assert req.status_code == response.get("code")
    assert req.json.get("access_token") != ""
    employee = UserModel.query.filter_by(email=json.get("email")).first()
    assert employee.role[0].name == "restaurant"
    assert employee.first_name == json.get("first_name")
    assert employee.last_name == json.get("last_name")




parametez_login = [({"email": "alex@gmail.com",
                     "password": "1111"},
                    {"code": 202}),
                   ({"email": "fall@gmail.com",
                     "password": "1111"},
                    {"code": 401, "msg": "Bad username or password"}),
                   ({"email": "alex@gmail.com",
                     "password": "FALL"},
                    {"code": 401, "msg": "Bad username or password"})]


@pytest.mark.parametrize("json, response", parametez_login)
def test_login(json, response, client):
    req = client.post("/login", json=json)
    assert req.status_code == response.get("code")
    assert req.json.get("msg") == response.get("msg")


def test_add_restaurant(user_headers, client):
    res = client.post("/restaurants",
                      headers=user_headers,
                      json={"name": "NaMe"})
    restaurant_slug = res.json.get("restaurant_slug")
    assert restaurant_slug == "name"
    restaurant = RestaurantModel.query.filter_by(slug=restaurant_slug).first()
    assert restaurant.name == "NaMe"
    assert restaurant.users[0].first_name == "Alex"
    assert res.status_code == 201



def test_add_restaurant_fall_token(client):
    res = client.post("/restaurants",
                      headers={"Authorization": "fall_token"},
                      json={"name": "Name"})
    assert res.status_code == 401


#
#
# def test_add_access_user():
#     with app.test_client() as test_client:
#         restaurant = test_client.post("/add_access_user",
#                                       headers={"Authorization": alex_token},
#                                       json={"slug": "name", "email": "Bob@gmail.com"})
#         assert restaurant.status_code == 201
#
#
# def test_add_access_user_fall_slug():
#     with app.test_client() as test_client:
#         restaurant = test_client.post("/add_access_user",
#                                       headers={"Authorization": alex_token},
#                                       json={"slug": "Fall", "email": "Bob@gmail.com"})
#         assert restaurant.status_code == 403
#
#
parametez_restaurant_menu = [({"2022-12-12": {"dishes": {"dish_0": {"name": "dish_1",
                                                                    "description": "description1"},
                                                         "dish_1": {"name": "dish_2",
                                                                    "description": "description2"}}}},
                              "name",
                              {"code": 204, "date": "2022-12-12", "dishes_len": 2}),
                             ({"2022-12-30": {"timedelta": "3",
                                              "dishes": {"dish_0": {"name": "dish_1",
                                                                    "description": "description1"},
                                                         "dish_1": {"name": "dish_2",
                                                                    "description": "description2"}}}},
                              "name",
                              {"code": 204, "date": "2022-12-30", "dishes_len": 6})]


@pytest.mark.parametrize("json, restaurant_slug, response", parametez_restaurant_menu)
def test_add_menu(json, restaurant_slug, response, client, user_headers):
    restaurant = client.post(f"/restaurant/{restaurant_slug}/menu",
                             headers=user_headers,
                             json=json)
    assert restaurant.status_code == response.get("code")
    dishes = DishModel.query.where(
        DishModel.date >= response.get("date")).all()
    assert len(dishes) == response.get("dishes_len")


#
#
# def test_add_menu_fall_data():
#     with app.test_client() as test_client:
#         restaurant = test_client.post("/add_menu",
#                                       headers={"Authorization": alex_token},
#                                       json={"restaurant": "FALL",
#                                             "2022-12-11": {"timedelta": "10",
#                                                            "dishes": {"dish_0": {"name": "dish_1",
#                                                                                  "description": "description1"},
#                                                                       "dish_1": {"name": "dish_2",
#                                                                                  "description": "description2"}}}})
#         assert restaurant.status_code == 403
#         assert restaurant.json.get("msg") == "You do not have access to the restaurant FALL"
#

#
# def test_today_menu():
#     with app.test_client() as test_client:
#         response = test_client.get("/menu", headers={"Authorization": alex_token}, date=datetime(2022, 12, 11))
#         assert response.status_code == 200
#         assert response.json == {'dish-0': {'description': 'description1', 'name': 'dish_1'},
#                                  'dish-1': {'description': 'description2', 'name': 'dish_2'}}
