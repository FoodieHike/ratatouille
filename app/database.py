import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from config import CONN_PARAMS
from models import UserReg


class Database:
    @staticmethod
    def get_connection():
        return psycopg2.connect(**CONN_PARAMS)


# функции для работы с таблицей записей походов (campaign)

class CampaignTable:
    def __init__(self, conn):
        self.conn = conn

    # получение записи из таблицы campaign
    def get_campaign(self, campaign_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM campaign WHERE id = %s;"),
                (campaign_id,))
            return cursor.fetchone()

    def create_campaign(self, campaign):        # создание записи в campaign
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'INSERT INTO campaign (startdate, enddate, '
                    'firstfood, lastfood) VALUES (%s, %s, %s, %s) RETURNING *;'
                ),
                (
                    campaign.startdate, campaign.enddate,
                    campaign.firstfood, campaign.lastfood
                )
                )
            self.conn.commit()
            return cursor.fetchone()

    # метод для добавления всех строк в таблицу админки
    @staticmethod
    def get_campaign_all(conn):        # получение всех записей пользователя
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM campaign;'
                )
            )
            return cursor.fetchall()

    @staticmethod
    def delete_campaign(conn, id):
        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM campaign WHERE id = %s',
                (id,)
            )
            conn.commit()

    @staticmethod
    def add_campaign(conn, startdate, enddate, firstfood, lastfood, user_id=0):
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO campaign (startdate, enddate,'
                'firstfood, lastfood, user_tg_id) VALUES (%s, %s, %s, %s, %s)',
                (startdate, enddate, firstfood, lastfood, user_id)
            )
            conn.commit()

    @staticmethod
    def update_campaign(
        conn, startdate, enddate, firstfood, lastfood, id, user_tg_id=0
    ):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'UPDATE campaign SET startdate=%s, enddate=%s,'
                    'firstfood=%s, lastfood=%s, user_tg_id=%s WHERE id=%s'
                ), (startdate, enddate, firstfood, lastfood, user_tg_id, id)
            )
            conn.commit()


class BotCampaignTable(CampaignTable):
    # создание записи в campaign
    def create_campaign(self, campaign, u_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    '''INSERT INTO campaign (startdate, enddate, firstfood,
                    lastfood, user_tg_id) VALUES
                    (%s, %s, %s, %s, %s) RETURNING *;'''
                ),
                (
                    campaign['startdate'], campaign['enddate'],
                    campaign['firstfood'], campaign['lastfood'], u_id
                ))
            self.conn.commit()
            return cursor.fetchone()

    # получение последней записи из таблицы campaign
    def get_campaign_last(self, uid):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    '''SELECT * FROM campaign WHERE User_tg_id=%s
                        ORDER BY id DESC LIMIT 1;'''
                ),
                (uid,))
            return cursor.fetchone()

    # получение всех записей пользователя
    def get_campaign_all(self, uid):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM campaign WHERE user_tg_id=%s;'
                ), (uid,)
            )
            return cursor.fetchall()

    # получение конкретной записи пользователя
    def get_campaign_by_id(self, uid, record_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM campaign WHERE user_tg_id=%s and id=%s;'
                ), (uid, record_id)
            )
            return cursor.fetchone()

# функции для работы с таблицей пользователей (users)


class UsersTable:
    def __init__(self, conn):
        self.conn = conn

    # проверка, есть ли пользователь в базе
    def table_users_check(self, uid):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM users WHERE tg_id=%s;'
                ), (uid,)
            )
            return cursor.fetchone()

    def create_user_bot_auto(self, user: UserReg, password, tgid):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    '''INSERT INTO users (name, password, tg_id)
                        VALUES (%s, %s, %s) RETURNING *;'''
                ), (user['name'], password, tgid)
            )
            self.conn.commit()
            return cursor.fetchone()

    # для добавления пользователя через админку:
    @staticmethod
    def add_user(conn, name, password, tg_id=None):
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    '''INSERT INTO users (name, password, tg_id)
                        VALUES (%s, %s, %s)'''
                ),
                (name, password, tg_id)
            )
            conn.commit()

    @staticmethod
    def get_users_all(conn):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    'SELECT * FROM users'
                )
            )
            return cursor.fetchall()

    @staticmethod
    def delete_user(conn, id):
        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM users WHERE id = %s',
                (id,)
            )
            conn.commit()

    @staticmethod
    def update_users(conn, id, name, password, tg_id):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    '''UPDATE users SET name=%s, password=%s, tg_id=%s
                        WHERE id=%s'''
                ), (name, password, tg_id, id)
            )
            conn.commit()


# функции для таблицы записей в меню
class MenuTable:
    def __init__(self, conn):
        self.conn = conn

    def get_menu(self, feedtype):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL(
                    '''SELECT productname, quantity, units, feedname FROM menu
                        WHERE feedtype=%s;'''
                ), (feedtype,)
            )
            return cursor.fetchall()

    @staticmethod
    def get_menu_all(conn):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM menu'
            )
            return cursor.fetchall()
