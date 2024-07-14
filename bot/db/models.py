from sqlalchemy import Column, Integer, String, DateTime, Boolean, Time

from bot.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)
    username = Column(String)
    fullname = Column(String)
    locale = Column(String, default="en")
    balance = Column(Integer, default=0)
    date = Column(DateTime)
    dead = Column(Boolean, default=False)


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    photo = Column(String)
    title = Column(String)
    desc = Column(String)
    price = Column(Integer)
    count = Column(Integer)
    fake_count = Column(Integer)


class Upper(Base):
    __tablename__ = "upper"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(Integer)
    price = Column(Integer)
    date = Column(DateTime)
    method = Column(String)


class Mailing(Base):
    __tablename__ = "mailing"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String)
    photo = Column(String)
    video = Column(String)
    markup = Column(String)
    date = Column(Time)
    schedule_id = Column(String)
