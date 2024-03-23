import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


from config import CONN_PARAMS
from models import UserReg


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


def create_campaign_for_bot(conn, campaign, u_id):        #создание записи в campaign
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                "INSERT INTO campaign (startdate, enddate, firstfood, lastfood, user_tg_id) VALUES (%s, %s, %s, %s, %s) RETURNING *;"
            ),
            (campaign['startdate'], campaign['enddate'], campaign['firstfood'], campaign['lastfood'], u_id))
        conn.commit()
        return cursor.fetchone()




def get_campaign_bot_demo(conn):        #получение последней записи из таблицы campaign
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL("SELECT * FROM campaign ORDER BY id DESC LIMIT 1;"))
        return cursor.fetchone()


def table_users_check(conn, uid):       #проверка, есть ли пользователь в базе
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                'SELECT * FROM users WHERE tg_id=%s;'
            ), (uid,)
        )
        return cursor.fetchone()
    

def get_campaign_all(conn, uid):        #получение всех записей пользователя
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                'SELECT * FROM campaign WHERE user_tg_id=%s;'
            ), (uid,)
        )   
        return cursor.fetchall()
    
    
def get_campaign_current(conn, uid, record_id):     #получение конкретной записи пользователя
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                'SELECT * FROM campaign WHERE user_tg_id=%s and id=%s;'
            ), (uid, record_id)
        )
        return cursor.fetchone()
    
def create_user_bot_auto(conn, user:UserReg, password, tgid):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL(
                'INSERT INTO users (name, password, tg_id) VALUES (%s, %s, %s) RETURNING *;'
            ), (user['name'], password, tgid)
        )
        conn.commit()
        return cursor.fetchone()