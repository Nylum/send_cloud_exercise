import base64
import unittest
from sqlalchemy_utils import database_exists, drop_database, create_database

from config import TestConfig
from manager import create_app, sql_db


def basic_auth_headers(username: str, password: str) -> dict:
    credentials = base64.b64encode(bytes(f"{username}:{password}", "utf-8")).decode("utf-8")
    return {'Authorization': 'Basic ' + credentials}


class TestWrapper(unittest.TestCase):
    app = create_app()
    client = app.test_client()
    database = sql_db
    url = TestConfig.SQLALCHEMY_DATABASE_URI

    @classmethod
    def setUpClass(cls):
        from tests.utils import generate_setup
        if database_exists(cls.url):
            drop_database(cls.url)
        create_database(cls.url)

        with cls.app.app_context():
            sql_db.create_all()
            items = generate_setup()
            sql_db.session.add_all(items)
            sql_db.session.commit()
