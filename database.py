from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import String

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///data/signal.db"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Interaction(Base):

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String)

    original_message = Column(String)

    rewritten_message = Column(String)

    toxicity = Column(Float)

    accepted = Column(Boolean)


Base.metadata.create_all(bind=engine)