from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Column, Integer, String, Date


from models import Base
from config import CONN_PARAMS


app = FastAPI()


engine = create_async_engine(
    f'''postgresql+asyncpg://{CONN_PARAMS['user']}:\
{CONN_PARAMS['password']}@{CONN_PARAMS['host']}:\
{CONN_PARAMS['port']}/{CONN_PARAMS['database']}'''
)


admin = Admin(app, engine)


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


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.tg_id]


class CampaignAdmin(ModelView, model=Campaign):
    column_list = [Campaign.id, Campaign.startdate, Campaign.enddate]


admin.add_view(UserAdmin)
admin.add_view(CampaignAdmin)
