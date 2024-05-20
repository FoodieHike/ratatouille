import asyncpg

from config import CONN_PARAMS


# хэндлеры для таблицы campaign
async def create_campaign(campaign):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO campaign (startdate, enddate,
            firstfood, lastfood)
            VALUES ($1, $2, $3, $4);''',
        campaign.startdate,
        campaign.enddate,
        campaign.firstfood,
        campaign.lastfood,
    )
    row = await conn.fetchrow(
        '''SELECT * FROM campaign
            ORDER BY id
            DESC LIMIT 1;'''
    )
    await conn.close()
    return dict(row)


async def create_campaign_bot(campaign, tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO campaign (startdate, enddate,
            firstfood, lastfood, user_tg_id)
            VALUES ($1, $2, $3, $4, $5);''',
        campaign['startdate'],
        campaign['enddate'],
        campaign['firstfood'],
        campaign['lastfood'],
        tguid
    )
    row = await conn.fetchrow(
        '''SELECT * FROM campaign
            ORDER BY id
            DESC LIMIT 1;'''
    )
    await conn.close()
    return dict(row)


async def get_campaign_all(tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM campaign
        WHERE user_tg_id = $1''',
        tguid
    )
    return row


async def get_campaign_by_id(tguid, record_id):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM campaign
        WHERE user_tg_id = $1 and id = $2''',
        tguid,
        record_id
    )
    return row


# хэндлеры для таблицы users
async def users_check(tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetchrow(
        '''SELECT * FROM users
            WHERE tg_id = $1;''',
        tguid
    )
    return row


async def create_user(name, password, tguid):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO users (name, password, tg_id)
        VALUES ($1, $2, $3);''',
        name,
        password,
        tguid
    )
