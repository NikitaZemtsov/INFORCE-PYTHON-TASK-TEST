from flask import Flask
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec

from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Configuration)
engine = create_engine('postgresql+psycopg2://postgres:bnw945jo@localhost/inforce_vote_for_food')
session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()

docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC':APISpec(
    title="Inforce",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(description="Test task. The TOR for this API can be found at the link"),
    plugins=[MarshmallowPlugin()],
),
    "APISPEC_SWAGGER_URL":"/swagger"
})

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







