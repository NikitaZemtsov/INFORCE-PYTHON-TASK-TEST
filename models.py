from app import db, jwt
from slugify import slugify
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, current_user
from datetime import timedelta
import re


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()


def take_role(**kwargs):
    role = kwargs.get("role", "restaurant")
    role = RoleModel.query.filter_by(name=role).first()
    return role


def restaurant_access():
    restaurant = RestaurantModel.query.filter_by(id=current_user.restaurant_id).first()
    if restaurant:
        return restaurant
    return



class RoleModel(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "{name}".format(name=self.name)


users_roles = db.Table("users_roles",
                       db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                       db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))

users_meals = db.Table("users_meals",
                       db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                       db.Column("dish_id", db.Integer, db.ForeignKey("dishes.id")))


class DishModel(db.Model):
    __tablename__ = "dishes"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    user = db.relationship('UserModel', secondary=users_meals, backref="dishes", lazy=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))

    def __init__(self, date, restaurant, *args, **kwargs):
        super(DishModel, self).__init__(*args, **kwargs)
        self.date = date
        self.restaurant_id = restaurant.id

    @classmethod
    def take_date(cls, dict):
        for key, value in dict.items():
            key = re.search(r'\d{4}\-\d{2}\-\d{2}', key)
            if key:
                date = datetime.strptime(key.group(), "%Y-%m-%d")
                return date.date()
        return

class RestaurantModel(db.Model):
    """
    Добавлять рестораны могут только авторизированные пользователи с ролью "restaurant"
    """
    __tablename__ = "restaurants"
    id = db.Column(db.Integer(), primary_key=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    users = db.relationship('UserModel', backref="restaurant")  # Юзеры которые могу добавлять блюда
    dishes = db.relationship('DishModel', backref="restaurant")

    def __init__(self, *args, **kwargs):
        super(RestaurantModel, self).__init__(*args, **kwargs)
        if self.name:
            self.slug = slugify(str(self.name))

    def __repr__(self):
        return "{name}".format(name=self.name)


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registration = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    role = db.relationship('RoleModel', secondary=users_roles, backref="user", lazy=True)  # заглушка на масштабирование

    def __init__(self, **kwargs):
        """
        Планируется 3 роли
        "restaurant"
        "employee"
        "admin"
        Создание юзера делиться на два варианта:
        1) Создание юзера с ролью "restaurant". Рестораны могут сами регестрироваться.
        2) Создание юзера "employee".
            Данного юзера может создавать только пользователь с правами "admin".
        """
        self.password = generate_password_hash(kwargs.get('password')).decode("utf-8")
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.email = kwargs.get("email") # Необходима проверка уникальности




    def get_token(self, expire_time=8):
        expire_delta = timedelta(expire_time)
        token = create_access_token(
            identity=self.id,
            expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email).one()
        if not check_password_hash(user.password, password):
            raise Exception("Uncorrected email or password ")
        return user








