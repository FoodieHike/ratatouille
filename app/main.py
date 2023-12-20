from fastapi import FastAPI
import psycopg2

app = FastAPI()

@app.get("/")
async def root():
    conn = psycopg2.connect(
        host="db",
        database="food_db",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"message": "Amnamnam, foooood!", "db_version": db_version}
