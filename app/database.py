import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from config import CONN_PARAMS
from models import UserReg





class Database:
    @staticmethod
    def get_connection():       
        return psycopg2.connect(**CONN_PARAMS)


#функции для работы с таблицей записей походов (campaign)
    
class CampaignTable:
    def __init__(self, conn):
        self.conn=conn


    def get_campaign(self, campaign_id):        #получение записи из таблицы campaign
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM campaign WHERE id = %s;"),
                (campaign_id,))
            return cursor.fetchone()

    def create_campaign(self, campaign):        #создание записи в campaign
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    "INSERT INTO campaign (startdate, enddate, firstfood, lastfood) VALUES (%s, %s, %s, %s) RETURNING *;"
                ),
                (campaign.startdate, campaign.enddate, campaign.firstfood, campaign.lastfood))
            self.conn.commit()
            return cursor.fetchone()



class BotCampaignTable(CampaignTable):
    def create_campaign(self, campaign, u_id):        #создание записи в campaign
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    "INSERT INTO campaign (startdate, enddate, firstfood, lastfood, user_tg_id) VALUES (%s, %s, %s, %s, %s) RETURNING *;"
                ),
                (campaign['startdate'], campaign['enddate'], campaign['firstfood'], campaign['lastfood'], u_id))
            self.conn.commit()
            return cursor.fetchone()


    def get_campaign_last(self, uid):        #получение последней записи из таблицы campaign
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM campaign WHERE User_tg_id=%s ORDER BY id DESC LIMIT 1;"), (uid,))
            return cursor.fetchone()
        
    def get_campaign_all(self, uid):        #получение всех записей пользователя
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM campaign WHERE user_tg_id=%s;'
                ), (uid,)
            )   
            return cursor.fetchall()
        
    def get_campaign_by_id(self, uid, record_id):     #получение конкретной записи пользователя
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM campaign WHERE user_tg_id=%s and id=%s;'
                ), (uid, record_id)
            )
            return cursor.fetchone()

#функции для работы с таблицей пользователей (users)
        
class UsersTable:
    def __init__(self, conn):
        self.conn=conn

    def table_users_check(self, uid):       #проверка, есть ли пользователь в базе
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM users WHERE tg_id=%s;'
                ), (uid,)
            )
            return cursor.fetchone()

        
    def create_user_bot_auto(self, user:UserReg, password, tgid):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'INSERT INTO users (name, password, tg_id) VALUES (%s, %s, %s) RETURNING *;'
                ), (user['name'], password, tgid)
            )
            self.conn.commit()
            return cursor.fetchone()
        



#функции для таблицы записей в меню
    

class MenuTable:
    def __init__(self, conn):
        self.conn=conn


    def get_menu(self, feedtype):     
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT productname, quantity, units, feedname FROM menu WHERE feedtype=%s;'
                ), (feedtype,)
            )
            return cursor.fetchall()

    
    
    
    