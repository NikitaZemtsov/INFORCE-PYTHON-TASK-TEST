from main import app
import pytest
from models import RoleModel, RestaurantModel, DishModel, UserModel
from datetime import datetime
from conftest import user, roles
from view import take_date

from unittest.mock import patch


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
                        "role": "employee"}, {"code": 201})]


@pytest.mark.parametrize("json, response", parametez_register)
def test_register_employee(json, response, user_admin, admin_headers, client):
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
                             "role": "employee"}, {"code": 201})]


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



parametez_restaurant_menu = [({"dish_0": {"name": "dish_1",
                                          "description": "description1"},
                               "dish_1": {"name": "dish_2",
                                          "description": "description2"}},
                              "name", "?date_period=2022-12-12",
                              {"code": 204, "date": [datetime(year=2022, month=12, day=12).date()], "dishes_len": 2}),
                             ({"dish_0": {"name": "dish_1",
                                          "description": "description1"},
                               "dish_1": {"name": "dish_2",
                                          "description": "description2"}},
                              "name", "?date_period=2022-12-30,2023-01-01",
                              {"code": 204, "date": [datetime(year=2022, month=12, day=30).date(),
                                                     datetime(year=2022, month=12, day=31).date(),
                                                     datetime(year=2023, month=1, day=1).date()],
                                            "dishes_len": 6})]


@pytest.mark.parametrize("json, restaurant_slug, date_period, response", parametez_restaurant_menu)
def test_add_menu(json, restaurant_slug, date_period, response, client, user_headers):
    req = client.post(f"/restaurant/{restaurant_slug}/menu" + date_period,
                             headers=user_headers,
                             json=json)
    assert req.status_code == response.get("code")
    dishes = DishModel.query.where(
        DishModel.date.in_(response.get("date"))).all()
    assert len(dishes) == response.get("dishes_len")


parametez_restaurant_menu = [({"dish_0": {"name": "dish_1",
                                          "description": "description1"},
                               "dish_1": {"name": "dish_2",
                                          "description": "description2"}},
                              "name", "",
                              {"code": 204, "date": [datetime(year=2022, month=12, day=11)], "dishes_len": 2})]


@patch("view.datetime")
@pytest.mark.parametrize("json, restaurant_slug, date_period, response", parametez_restaurant_menu)
def test_add_menu_datenow(mock_date, json, restaurant_slug, date_period, response, client, user_headers):
    date_for_mock = response.get("date")[0]
    mock_date.utcnow.return_value = date_for_mock
    mock_date.date.return_value = date_for_mock.date()
    req = client.post(f"/restaurant/{restaurant_slug}/menu" + date_period,
                             headers=user_headers,
                             json=json)
    assert req.status_code == response.get("code")
    dishes = DishModel.query.where(
        DishModel.date.in_(response.get("date"))).all()
    assert len(dishes) == response.get("dishes_len")
    assert dishes[0].date == date_for_mock


parametez_restaurant_menu = [({"dish_0": {"name": "dish_1",
                                          "description": "description1"},
                               "dish_1": {"name": "dish_2",
                                          "description": "description2"}},
                              {"code": 204, "date": [datetime(year=2022, month=12, day=11)], "dishes_len": 2})]


@patch("view.datetime")
@pytest.mark.parametrize("json, response", parametez_restaurant_menu)
def test_today_menu(mock_date, json, response, client, user_headers):
    date_for_mock = response.get("date")[0]
    mock_date.utcnow.return_value = date_for_mock
    mock_date.date.return_value = date_for_mock.date()
    req = client.get("/menu", headers=user_headers)
    print(req.json)
    assert req.status_code == 200
    assert req.json == {} # Need to refactor date from datebase
