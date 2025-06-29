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



Base.metadata.create_all(engine)