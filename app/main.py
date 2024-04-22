from fastapi import FastAPI, HTTPException

import psycopg2
import database, models
from dotenv import load_dotenv
import os

from starlette.middleware.wsgi import WSGIMiddleware


from admin import app as flask_app



current_file_dir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(current_file_dir, '..', '.env')

load_dotenv(dotenv_path=env_path)

CONN_PARAMS=os.getenv('CONN_PARAMS')





#Создаем приложение и интегрируем к нему фласк админскую приложуху
app = FastAPI()

app.mount('/administration/', WSGIMiddleware(flask_app))



@app.post("/campaign/", response_model=models.Campaign)
async def create_campaign(campaign: models.CampaignCreate):       #эндпоинт для наполнения таблицы campaign
    conn = database.get_connection()
    try:
        new_campaign = database.create_campaign(conn, campaign)
        if new_campaign:
            return new_campaign
        raise HTTPException(status_code=404, detail="Ya hui znaet, gde ono")
    finally:
        conn.close()

@app.get("/")
async def root():
    conn = psycopg2.connect(**CONN_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"message": "Checkout 1488, foooood!", "db_version": db_version}
