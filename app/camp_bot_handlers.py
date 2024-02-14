from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import Command
import psycopg2


from psycopg2 import sql
from config import CONN_PARAMS
from psycopg2.extras import RealDictCursor



router=Router()


@router.message(Command('start'))
async def start_handler(msg:Message):
    await msg.answer('Здорово, ебола! запустил меня наконец.')




conn= psycopg2.connect(**CONN_PARAMS)


def get_campaign(conn, campaign_id):      
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            sql.SQL("SELECT * FROM campaign WHERE id = %s;"),
            (campaign_id,))
        return cursor.fetchone()

@router.message()
async def camp_handler(msg:Message):
    response=get_campaign(conn=conn, campaign_id=int(msg))
    await msg.answer(f'Нужная запись: {response}')