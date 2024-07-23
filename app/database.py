import asyncpg

from app.config import CONN_PARAMS


# хэндлеры для таблицы campaign
async def create_campaign(campaign):
    conn = await asyncpg.connect(**CONN_PARAMS)
    await conn.execute(
        '''INSERT INTO campaigns (startdate, enddate,
            firstfood, lastfood, user_tg_id)
            VALUES ($1, $2, $3, $4, $5);''',
        campaign.startdate,
        campaign.enddate,
        campaign.firstfood,
        campaign.lastfood,
        campaign.user_tg_id
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
        await conn.close()
        return row
    await conn.close()


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
        '''SELECT product_name, quantity, units, feed_name
        FROM menu
        WHERE feed_type=$1''',
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


async def get_total_menu(multiplier, data):
    conn = await asyncpg.connect(**CONN_PARAMS)
    feedtype_keys = data["feedtypes_amount"].keys()
    case_expressions = ' '.join(
        [f'WHEN feed_type = ${i[0] + 2} '
         f'THEN {data["feedtypes_amount"][i[1]]}'
         for i in enumerate(data['feedtypes_amount'])]
    )
    feedtypes_amount = ', '.join(
        [f'${num + 2 + len(data["feedtypes_amount"])}'
         for num in range(len(data['feedtypes_amount']))]
    )

    query = f'''
        SELECT
            product_name,
            SUM(Quantity * $1 * (
                CASE {case_expressions} END
            )) AS Quantity,
            Units
        FROM menu
        WHERE feed_type IN ({feedtypes_amount})
        GROUP BY product_name, Units
        ORDER BY product_name;
    '''

    row = await conn.fetch(query, multiplier, *feedtype_keys, *feedtype_keys)
    await conn.close()

    return row


async def get_daily_menu(multiplier, feedtype):
    conn = await asyncpg.connect(**CONN_PARAMS)
    row = await conn.fetch(
        '''SELECT feed_name,
        product_name,
        quantity * $1 as quantity,
        units, feed_name
        FROM menu
        WHERE feed_type=$2''',
        multiplier,
        feedtype
    )
    await conn.close()
    return row
