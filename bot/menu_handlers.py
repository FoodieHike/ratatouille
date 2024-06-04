from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, FSInputFile
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


import os
import sys

import app.database as database
import app.utils as utils
import app.pdf_creator as pdf_creator
from campaign_handlers import bot


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

routerMenu = Router()


class ChooseIDStates(StatesGroup):
    wait_for_id = State()
    wait_for_people_amount = State()


# хэндлеры для рассчета меню

# хэндлер для начала работы с меню
@routerMenu.callback_query(F.data == 'food_menu_button')
async def callback_menu_handller(query: CallbackQuery, state: FSMContext):
    row = [[InlineKeyboardButton(
        text='Выбрать по ID', callback_data='chooseID'
    )],
           [InlineKeyboardButton(
               text='Последняя запись', callback_data='lastone'
           )]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)
    await query.message.answer(
        '''Меню для конкретного похода,\
 или возьмем последнюю запись?''', reply_markup=mrkp
    )
    await state.clear()


# хэндлер для начала работы с меню (через команду)
@routerMenu.message(Command('menu'))
async def menu_handller(msg: Message, state: FSMContext):
    row = [[InlineKeyboardButton(
        text='Выбрать по ID', callback_data='chooseID'
    )], [InlineKeyboardButton(
        text='Последняя запись', callback_data='lastone'
    )]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)
    await msg.answer('''Меню для конкретного похода,\
 или возьмем последнюю запись?''', reply_markup=mrkp)
    await state.clear()


# хэндлеры для выбора записи по ID:

# первый
@routerMenu.callback_query(F.data == 'chooseID')
async def id_for_meny_hsndler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer('Напишите ID записи похода:')
    await query.message.edit_reply_markup(reply_markup=None)
    await state.set_state(ChooseIDStates.wait_for_id)


# хэндлер для выбора записи по ID (второй)
@routerMenu.message(ChooseIDStates.wait_for_id)
async def choose_id_handler(message: Message, state: FSMContext):
    try:
        record = await database.get_campaign_by_id(
            tguid=message.from_user.id, record_id=message.text
        )
        lenght = record['enddate']-record['startdate']
    except TypeError:
        await message.answer('У вас пока нет записей')
    else:
        await state.set_data({'days_amount': lenght.days+1})
        data = await state.get_data()
        data['first_meal'] = int(record['firstfood'])
        data['last_meal'] = int(record['lastfood'])
        data['startdate'] = record['startdate']
        data['enddate'] = record['enddate']
        data['B1'] = 0
        data['B2'] = 0

        # определяем количество дополнительных приемов пищи:
        if record['firstfood'] == '1':
            firstday_feed_amount = 3
        elif record['firstfood'] == '2':
            firstday_feed_amount = 2
        else:
            firstday_feed_amount = 1

        if record['lastfood'] == '1':
            lastday_feed_amount = 1
        elif record['lastfood'] == '2':
            lastday_feed_amount = 2
        else:
            lastday_feed_amount = 3

        extra_meal = firstday_feed_amount+lastday_feed_amount

        data['extra_meal'] = extra_meal
        await state.set_data(data)

        await message.answer('На сколько человек планируете поход?')
        await state.set_state(ChooseIDStates.wait_for_people_amount)


# Хэндлер рассчитывает количество всех приемов пищи
@routerMenu.message(ChooseIDStates.wait_for_people_amount)
async def menu_process(msg: Message, state: FSMContext):
    data = await state.get_data()
    data['people_amount'] = int(msg.text)
    # определение дней с полным набором приемов пищи
    full_days = data['days_amount']-2
    feeds = full_days*3        # количество приемов в полных днях

    meals_full_amount = feeds+data['extra_meal']

    await msg.answer(
                    f'''В этом походе, у вас получается всего\
    {meals_full_amount} приемов пищи.\
        \nДавайте определим, что вы будете в них есть.''')
    first_meal = data['first_meal']
    count_days = data['days_amount']
    last_meal = data['last_meal']
    records = await database.get_menu_all()
    feednames = []
    feednames_dict = {}
    for record in records:
        if record['feedname'] not in feednames:
            feednames.append(record['feedname'])
            feednames_dict[record['feedname']] = record['feedtype']
    row = []
    for name in feednames:
        row.append([InlineKeyboardButton(
            text=name, callback_data=feednames_dict[name]
        )])
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)

    meals_count = 0
    for day in range(1, count_days+1):
        if day == count_days:
            for meal in range(1, last_meal+1):
                meals_count += 1
                if meal == 1:
                    feed_type = 'завтрак'
                elif meal == 2:
                    feed_type = 'обед'
                else:
                    feed_type = 'ужин'
                meal_msg = await msg.answer(
                    f'''День {day};  Прием пищи -
                    {feed_type}''', reply_markup=mrkp
                )
                message_value = '$'.join([str(day), feed_type])
                # запись информации о приеме пищи
                # для распределения данных в конечном сообщении
                data[''.join(
                    ['msg_id', str(meal_msg.message_id)]
                )] = message_value
        else:
            for meal in range(first_meal, 4):
                meals_count += 1
                if meal == 1:
                    feed_type = 'завтрак'
                elif meal == 2:
                    feed_type = 'обед'
                else:
                    feed_type = 'ужин'
                meal_msg = await msg.answer(
                    f'''День {day};  Прием пищи -
                    {feed_type}''', reply_markup=mrkp
                )
                message_value = '$'.join([str(day), feed_type])
                # запись информации о приеме пищи
                # для распределения данных в конечном сообщении
                data[''.join(
                    ['msg_id', str(meal_msg.message_id)]
                )] = message_value
                first_meal += 1
                if first_meal > 3:
                    first_meal = 1
                    break
    await state.set_data(data)


# хэндлер для предоставления последней записи
@routerMenu.callback_query(F.data == 'lastone')
async def menu_last_writing_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        record = await database.get_campaign_last(tguid=query.from_user.id)
        # определяем длительность похода
        lenght = record['enddate']-record['startdate']

    except TypeError:
        row = [[InlineKeyboardButton(
            text='Создать запись', callback_data='create'
        )], [InlineKeyboardButton(
            text='Вернуться в меню', callback_data='menu_button'
        )]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=row)
        await query.message.answer(
            '''К сожалению не удалось найти ни одной
                записи. Может хотите создать новую?''', reply_markup=mrkp
        )
    except ValueError:
        await query.message.answer(
            '''Неправильная форма записи!
            \nВведите пожалуйста корректный id (натуральное число):'''
        )
    else:
        await state.set_data({'days_amount': lenght.days+1})
        data = await state.get_data()
        data['first_meal'] = int(record['firstfood'])
        data['last_meal'] = int(record['lastfood'])
        data['startdate'] = record['startdate']
        data['enddate'] = record['enddate']

        if record['firstfood'] == 1:
            firstday_feed_amount = 3
        elif record['firstfood'] == 2:
            firstday_feed_amount = 2
        else:
            firstday_feed_amount = 1

        if record['lastfood'] == 1:
            lastday_feed_amount = 1
        elif record['lastfood'] == 2:
            lastday_feed_amount = 2
        else:
            lastday_feed_amount = 3

        # определяем количество дополнительных приемов пищи:
        extra_meal = firstday_feed_amount+lastday_feed_amount

        data['extra_meal'] = extra_meal
        await state.set_data(data)

        await query.message.answer('На сколько человек планируете поход?')
        await state.set_state(ChooseIDStates.wait_for_people_amount)


# хэндлер для обработки кнопок составления еды
@routerMenu.callback_query(F.data.startswith('B'))
async def feedtype_b1_handler(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    record = await database.get_menu(feedtype=query.data)
    full_list = []
    meal_name = False
    # формируем сообщение с нужными пропорциями еды
    # (надо будет отдельно функцию написать и бромсить в утилиты)
    for obj in record:
        temp_row = ' '.join(
            [str(
                obj['quantity']*data['people_amount']
            ), obj['units'], obj['productname']]
        )
        full_list.append(temp_row)
        if not meal_name:
            meal_name = obj['feedname']
    res = '\n'.join(full_list)
    # достаем информацию о дне и приеме пище
    # (в словаре состояний под номером id сообщения со встроенной кнопкой)
    crude_row = data[''.join(['msg_id', str(query.message.message_id)])]
    day, meal = crude_row.split('$')       # распределяем по переменным

    # формирование списка продуктов и счетчика меню
    meal_products = f'''День похода - {day}, прием пищи -
                    {meal} ({meal_name}):\n{res}'''

    if meal == 'завтрак':
        feed = 1
    elif meal == 'обед':
        feed = 2
    else:
        feed = 3
    # формирование ключа для записи в pdf
    products_list = ''.join(['prod', str(day), str(feed)])
    # запись строки с продуктами для формирования pdf документа
    data[products_list] = meal_products
    # работа с удалением сообщения и записи в словаре
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    del data[''.join(['msg_id', str(query.message.message_id)])]
    await state.set_data(data)

    found_key = False

    for key in data:
        # проверяем, есть ли неудаленные сообщения, не оконена ли запись
        if key.startswith('msg_id'):
            found_key = True
            break

    if found_key:
        pass

    else:
        # создаем массив данных с записями ключей с инфой о походах
        records_list = []
        for key in data:
            if key.startswith('prod'):
                records_list.append(key)
        records_list.sort()
        # конвертируем ключи в записи данных в массиве
        for index in range(len(records_list)):
            records_list[index] = data[records_list[index]]

        await query.message.answer('Формируем pdf и отправляем...')

        # конвертируем данные для общего подсчета и считаем
        total_data = '\n'.join(records_list)
        total = utils.meal_total_count(total_data)

        # создание файлика
        pdf_creator.pdf_creation(
            *records_list, filename=query.from_user.id,
            startdate=data['startdate'], enddate=data['enddate'], total=total
        )
        pdf_file = FSInputFile(
            f'/pdf_files/hike_menu_{query.from_user.id}.pdf'
        )
        await query.message.answer_document(pdf_file)
