import pytest
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

sys.path.append("..")
from main import app
from app import Base, session as db_session
from models import UserModel, RoleModel


@pytest.fixture(scope="session")
def testapp():
    _app = app
    engine = create_engine(
        "postgresql+psycopg2://postgres:bnw945jo@localhost/test_inforce")
    _app.connection = engine.connect()
    db_session.configure(bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield _app
    # Base.metadata.drop_all(bind=engine)
    _app.connection.close()


@pytest.fixture(scope="function")
def session(testapp):
    ctx = testapp.app_context()
    ctx.push()

    yield db_session

    db_session.close_all()
    ctx.pop()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def roles(session):
    roles = ["restaurant",
             "employee",
             "admin"]
    for role in roles:
        new_role = RoleModel(name=role, description="pass")
        session.add(new_role)
    session.commit()
    return RoleModel.query.all()


@pytest.fixture(scope="function")
def user(session):
    user = UserModel(**{"first_name": "Alex",
                       "email": "alex@gmail.com",
                       "last_name": "Leo",
                       "password": "11111"})
    role = RoleModel.query.filter_by(name="restaurant").first()
    user.role.append(role)
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def user_token(client):
    res = client.post("/login", json={
              "email": "alex@gmail.com",
              "password": "11111"})
    return res.json.get('access_token')


@pytest.fixture
def user_headers(user_token):
    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    return headers

@pytest.fixture(scope="function")
def user_admin(session):
    user = UserModel(**{"first_name": "admin",
                       "email": "admin@gmail.com",
                       "last_name": "ADMIN",
                       "password": "admin"})
    role = RoleModel.query.filter_by(name="admin").first()
    user.role.append(role)
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def user_admin_obj():
    admin = UserModel.query.filter_by(email="admin@gmail.com").first()
    return admin

@pytest.fixture
def admin_token(client):
    res = client.post("/login", json={
              "email": "admin@gmail.com",
              "password": "admin"})
    return res.json.get('access_token')


@pytest.fixture
def admin_headers(admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    return headers









