from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from database import SQLALCHEMY_DATABASE_URL

def create_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Database created at {SQLALCHEMY_DATABASE_URL}")
    else:
        print(f"Database already exists at {SQLALCHEMY_DATABASE_URL}")

if __name__ == "__main__":
    create_db()
