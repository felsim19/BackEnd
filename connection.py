from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "mysql+mysqlconnector://root:1234@localhost:3306/fixFlow"

create = create_engine(DB_URL)

sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=create)

base = declarative_base()

def get_db():
    connection = sessionLocal()
    try:
        yield connection
    finally:
        connection.close()