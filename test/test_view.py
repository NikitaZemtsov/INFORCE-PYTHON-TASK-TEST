from main import app
import pytest

alex_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2ODgwOTc1NSwianRpIjoiNmY0MTgxNDgtZTc2Ni00NTRmLWJhZjktOWZlOWE5YmQ3ZGNmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjY4ODA5NzU1LCJleHAiOjE2Njk1MDA5NTV9.zScsvPGef2IQM6G7L0u3hE8-umCue9RC4ZZng7Nwy2o"
all_token = {}

parametez = [{"first_name": "Alex",
              "email": "alex@gmail.com",
              "last_name": "Leo",
              "password": "1111"},
             {"first_name": "Bob",
              "email": "Bob@gmail.com",
              "last_name": "Bear",
              "password": "2222"}]


@pytest.mark.parametrize("json", parametez)
def test_register(json):
    with app.test_client() as test_client:
        user = test_client.post("/register", json=json)
        assert user.status_code == 201
        token = user.json.get("access_token")
        all_token[json.get("first_name")] = token
        assert token != ""


# alex_token = all_token.get("Alex")
# bob_token = all_token.get("Bob")

def test_login():
    with app.test_client() as test_client:
        login = test_client.post("/login",
                                 headers={"Authorization": alex_token},
                                 json={"email": "alex@gmail.com", "password": "1111"})
        assert login.status_code == 202
        assert login.json.get("access_token") != ""


def test_login_fall_password():
    with app.test_client() as test_client:
        login = test_client.post("/login",
                                 headers={"Authorization": alex_token},
                                 json={"email": "alex@gmail.com", "password": "fall"})
        print(login.status_code, login.json)
        assert login.status_code == 401
        assert login.json.get("msg") == "Bad username or password"


def test_login_fall_email():
    with app.test_client() as test_client:
        login = test_client.post("/login",
                                 headers={"Authorization": alex_token},
                                 json={"email": "fall", "password": "1111"})
        assert login.status_code == 401
        assert login.json.get("msg") == "Bad username or password"


def test_add_restaurant():
    with app.test_client() as test_client:
        restaurant = test_client.post("/add_restaurant",
                                      headers={"Authorization": alex_token},
                                      json={"name": "NaMe"})
        assert restaurant.json.get("restaurant_slug") == "name"


def test_add_restaurant_fall_token():
    with app.test_client() as test_client:
        restaurant = test_client.post("/add_restaurant",
                                      headers={"Authorization": "fall_token"},
                                      json={"name": "Name"})
        assert restaurant.status_code == 401


def test_add_access_user():
    with app.test_client() as test_client:
        restaurant = test_client.post("/add_access_user",
                                      headers={"Authorization": alex_token},
                                      json={"slug": "name", "email": "Bob@gmail.com"})
        assert restaurant.status_code == 201


def test_add_access_user_fall_slug():
    with app.test_client() as test_client:
        restaurant = test_client.post("/add_access_user",
                                      headers={"Authorization": alex_token},
                                      json={"slug": "Fall", "email": "Bob@gmail.com"})
        assert restaurant.status_code == 403


def test_add_menu():
    with app.test_client() as test_client:
        restaurant = test_client.post("/add_menu",
                                      headers={"Authorization": alex_token},
                                      json={"restaurant": "name",
                                            "2022-12-11": {"timedelta": "10",
                                                           "dishes": {"dish_0": {"name": "dish_1",
                                                                                 "description": "description1"},
                                                                      "dish_1": {"name": "dish_2",
                                                                                 "description": "description2"}}}})
        assert restaurant.status_code == 204

test_add_menu()
