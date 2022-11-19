from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)





from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import UserModel, RoleModel, RestaurantModel, DishModel
admin = Admin(app)
admin.add_view(ModelView(RoleModel, db.session))
admin.add_view(ModelView(UserModel, db.session))
admin.add_view(ModelView(RestaurantModel, db.session))
admin.add_view(ModelView(DishModel, db.session))







