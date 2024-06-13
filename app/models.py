from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, Date


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    tg_id = Column(Integer)


class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    startdate = Column(Date)
    enddate = Column(Date)
    firstfood = Column(Integer)
    lastfood = Column(Integer)