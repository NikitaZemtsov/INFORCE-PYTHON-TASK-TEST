from flask import Flask
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Configuration)
engine = create_engine('postgresql+psycopg2://postgres:bnw945jo@localhost/inforce_vote_for_food')
session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()

migrate = Migrate(app, db)
jwt = JWTManager(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


#
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
#
# from models import UserModel, RoleModel, RestaurantModel, DishModel
# admin = Admin(app)
# admin.add_view(ModelView(RoleModel, db.session))
# admin.add_view(ModelView(UserModel, db.session))
# admin.add_view(ModelView(RestaurantModel, db.session))
# admin.add_view(ModelView(DishModel, db.session))







