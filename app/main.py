from fastapi import FastAPI, HTTPException
import psycopg2
import database, models
from config import CONN_PARAMS


app = FastAPI()

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
