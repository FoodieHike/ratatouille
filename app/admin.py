from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine


from models import User, Campaign
from config import CONN_PARAMS, SECRET_KEY
from oauth import AdminAuth

app = FastAPI()


engine = create_async_engine(
    f'''postgresql+asyncpg://{CONN_PARAMS['user']}:\
{CONN_PARAMS['password']}@{CONN_PARAMS['host']}:\
{CONN_PARAMS['port']}/{CONN_PARAMS['database']}'''
)

authentication_backend = AdminAuth(secret_key=SECRET_KEY)


admin = Admin(app, engine, authentication_backend=authentication_backend)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.tg_id]


class CampaignAdmin(ModelView, model=Campaign):
    column_list = [Campaign.id, Campaign.startdate, Campaign.enddate]


admin.add_view(UserAdmin)
admin.add_view(CampaignAdmin)
