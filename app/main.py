from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



import psycopg2
import database, models
from starlette.middleware.wsgi import WSGIMiddleware

from config import CONN_PARAMS
from admin import app as flask_app







#Создаем приложение и интегрируем к нему фласк админскую приложуху
app = FastAPI()

templates= Jinja2Templates(directory='templates')

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount('/administration/', WSGIMiddleware(flask_app))



@app.post("/campaign/", response_model=models.Campaign)
async def create_campaign(campaign: models.CampaignCreate):       #эндпоинт для наполнения таблицы campaign
    conn = database.get_connection()
    try:
        new_campaign = database.create_campaign(conn, campaign)
        if new_campaign:
            return new_campaign
        raise HTTPException(status_code=404, detail='Not found')
    finally:
        conn.close()

@app.get('/')
async def read_root(request:Request):
    return templates.TemplateResponse('main.html', {'request':request})


@app.get('/admin/')
async def admin(request:Request):
    return templates.TemplateResponse('fastapi_index.html', {'request':request})