import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from config import CONN_PARAMS


def get_connection():       
    return psycopg2.connect(**CONN_PARAMS)

def get_campaign(conn, campaign_id):        #получение записи из таблицы campaign
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL("SELECT * FROM campaign WHERE id = %s;"),
            (campaign_id,))
        return cursor.fetchone()

def create_campaign(conn, campaign):        #создание записи в campaign
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                "INSERT INTO campaign (startdate, enddate, firstfood, lastfood) VALUES (%s, %s, %s, %s) RETURNING *;"
            ),
            (campaign.startdate, campaign.enddate, campaign.firstfood, campaign.lastfood))
        conn.commit()
        return cursor.fetchone()
