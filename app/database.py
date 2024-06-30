import asyncpg

from app.config import CONN_PARAMS


# хэндлеры для таблицы campaign
async def create_campaign(campaign):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO campaigns (startdate, enddate,
            firstfood, lastfood)
            VALUES ($1, $2, $3, $4);''',
        campaign.startdate,
        campaign.enddate,
        campaign.firstfood,
        campaign.lastfood,
    )
    row = await conn.fetchrow(
        '''SELECT * FROM campaigns
            ORDER BY id
            DESC LIMIT 1;'''
    )
    await conn.close()
    return dict(row)


async def create_campaign_bot(campaign, tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO campaigns (startdate, enddate,
            firstfood, lastfood, user_tg_id)
            VALUES ($1, $2, $3, $4, $5);''',
        campaign['startdate'],
        campaign['enddate'],
        campaign['firstfood'],
        campaign['lastfood'],
        tguid
    )
    row = await conn.fetchrow(
        '''SELECT * FROM campaigns
            ORDER BY id
            DESC LIMIT 1;'''
    )
    await conn.close()
    return dict(row)


async def get_campaign_all(tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetch(
        '''SELECT * FROM campaigns
        WHERE user_tg_id = $1''',
        tguid
    )
    await conn.close()
    return row


async def get_campaign_by_id(tguid, record_id):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM campaigns
        WHERE user_tg_id = $1 and id = $2''',
        int(tguid),
        int(record_id)
    )
    await conn.close()
    return row


async def get_campaign_last(tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM campaigns
        WHERE user_tg_id=$1
        ORDER BY id DESC LIMIT 1''',
        int(tguid)
    )
    await conn.close()
    return row


# хэндлеры для таблицы users
async def users_check(tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM users
            WHERE tg_id = $1;''',
        tguid
    )
    await conn.close()
    return row


async def get_user_by_name(username):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM users
        WHERE username=$1''',
        username
    )
    if row:
        return row


async def create_user(name, password, tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO users (username, password, tg_id, disabled)
        VALUES ($1, $2, $3, $4);''',
        name,
        password,
        tguid,
        True
    )
    await conn.close()


# хэндлеры для таблицы menu
async def get_menu(feedtype):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetch(
        '''SELECT productname, quantity, units, feedname
        FROM menu
        WHERE feedtype=$1''',
        feedtype
    )
    await conn.close()
    return row


async def get_menu_all():
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetch(
        '''SELECT * FROM menu'''
    )
    await conn.close()
    return row
