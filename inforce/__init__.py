from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from inforce.config import Configuration
from flask_migrate import Migrate
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
import logging
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy()
engine = Configuration.SQLALCHEMY_DATABASE_URI
session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()

migrate = Migrate(app, db)
docs = FlaskApiSpec()
jwt = JWTManager()

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

# from inforce.models import *
# Base.metadata.create_all(bind=engine)

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(msg)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


from inforce.employee.views import employee
from inforce.restaurant.views import restaurant_app
from inforce.users.views import users

app.register_blueprint(restaurant_app)
app.register_blueprint(users)
app.register_blueprint(employee)


docs.init_app(app)
jwt.init_app(app)
