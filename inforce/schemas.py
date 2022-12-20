from marshmallow import Schema, validate, fields, validates, ValidationError, pre_dump, post_dump
from inforce.models import UserModel, RestaurantModel


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    restaurant_id = fields.Integer(dump_only=True)
    password = fields.String(load_only=True, required=True, validates=[validate.Length(min=5, max=255)])
    first_name = fields.String(required=True, validates=[validate.Length(max=255)])
    last_name = fields.String(required=True, validates=[validate.Length(max=255)])
    email = fields.Email(required=True)
    registration = fields.DateTime(dump_only=True)
    role = fields.String(validates=[validate.OneOf(choices=["admin", "restaurant", "employee"])])

    @validates("email")
    def validate_email(self, email):
        email = UserModel.query.filter_by(email=email).first()
        if email:
            raise ValidationError("User with this email already exists")
        return True


class LoginSchema(Schema):
    password = fields.String(load_only=True, required=True, validates=[validate.Length(min=5, max=255)])
    email = fields.Email(required=True)


class DishesSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validates=[validate.Length(max=255)])
    description = fields.String(required=True, validates=[validate.Length(max=255)])
    date = fields.DateTime(required=True, dump_only=True)
    restaurant = fields.String(dump_only=True)


class OrderSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    date = fields.DateTime(required=True, dump_only=True)
    count = fields.Integer()

    @pre_dump
    def make_count(self, dish, many, **kwargs):
        dish.__dict__["count"] = len(dish.user)
        return dish


class RestaurantSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(dump_only=True)
    name = fields.String(required=True, validates=[validate.Length(max=255)])
    users = fields.Nested(UserSchema, many=True, dump_only=True)
    dishes = fields.Nested(DishesSchema, many=True, dump_only=True)

    @validates
    def validate_name(self, name):
        name = RestaurantModel.query.filter_by(name=name).first()
        if name:
            raise ValidationError("Restaurant with this name already exists")
        return True


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    msg = fields.String(dump_only=True)
