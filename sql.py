from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import declarative_base


db_url = "sqlite:///database.db"

engine = create_engine(db_url)

Base = declarative_base()


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer,primary_key=True)
    title = Column(String)
    description = Column(String)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

Base.metadata.create_all(engine)