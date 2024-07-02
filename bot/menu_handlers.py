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
async def menu_handller(message: Message, state: FSMContext):
    row = [[InlineKeyboardButton(
        text='Выбрать по ID', callback_data='chooseID'
    )], [InlineKeyboardButton(
        text='Последняя запись', callback_data='lastone'
    )]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)
    await message.answer('''Меню для конкретного похода,\
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
        data = {
            'days_amount': lenght.days+1,
            'firstfood': int(record['firstfood']),
            'lastfood': int(record['lastfood']),
            'startdate': record['startdate'],
            'enddate': record['enddate'],
            'extra_meal': utils.extra_meal_counter(record)
        }
        await state.set_data(data)
        await message.answer('На сколько человек планируете поход?')
        await state.set_state(ChooseIDStates.wait_for_people_amount)


# Хэндлер рассчитывает количество всех приемов пищи
@routerMenu.message(ChooseIDStates.wait_for_people_amount)
async def menu_process(message: Message, state: FSMContext):
    data = await state.get_data()
    data['people_amount'] = int(message.text)

    # определение дней с полным набором приемов пищи
    full_days = data['days_amount']-2
    feeds = full_days*3        # количество приемов в полных днях
    # количество приемов пищи
    meals_full_amount = feeds+data['extra_meal']
    await message.answer(
        f'В этом походе, у вас получается всего'
        f' {meals_full_amount} приемов пищи.'
        f'\nДавайте определим, что вы будете в них есть.'
    )

    first_meal = data['firstfood']
    days_amount = data['days_amount']
    last_meal = data['lastfood']

    records = await database.get_menu_all()
    feednames_dict = {
        record['feedname']: record['feedtype'] for record in records
    }

    # Устанавливаем клавиатуру с меню для каждого сообщения
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=feedtype)]
        for name, feedtype in feednames_dict.items()
    ]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)

    for day in range(1, days_amount+1):
        if day == days_amount:
            for meal in range(1, last_meal + 1):
                await utils.create_meal_message(
                    day,
                    mrkp,
                    message,
                    data,
                    feed_type=utils.get_meal_type(meal)
                )
        else:
            for meal in range(first_meal, 4):
                await utils.create_meal_message(
                    day,
                    mrkp,
                    message,
                    data,
                    feed_type=utils.get_meal_type(meal)
                )
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
        data = {
            'days_amount': lenght.days+1,
            'firstfood': int(record['firstfood']),
            'lastfood': int(record['lastfood']),
            'startdate': record['startdate'],
            'enddate': record['enddate'],
            'extra_meal': utils.extra_meal_counter(record)
        }
        await state.set_data(data)
        await query.message.answer('На сколько человек планируете поход?')
        await state.set_state(ChooseIDStates.wait_for_people_amount)


# хэндлер для обработки кнопок составления еды
@routerMenu.callback_query(F.data.startswith('B'))
async def feedtype_handler(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    record = await database.get_menu(feedtype=query.data)
    meal_products, meal, day = utils.get_daily_menu(record, data, query)

    # формирование ключа для записи в pdf
    # в значении текст дневного меню
    data[f'daily_menu,{day},{meal}'] = meal_products
    # работа с удалением сообщения и записи в словаре
    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )

    # удаляем из словаря состояний лишнюю инфу об удаленном сообщении
    del data[f'message_id{query.message.message_id}']
    await state.set_data(data)

    undeleted_messages = [
        message_id
        for message_id in data.keys()
        if message_id.startswith('message_id')
    ]
    # если сообщений больше не осталось и пользователь выбрал меню на
    if not undeleted_messages:
        # создаем массив данных с записями ключей с инфой о походах
        total, daily_menu = utils.get_data_for_pdf(data)
        total = utils.meal_total_count(total)
        # создание файлика
        utils.pdf_creation(
            *daily_menu, filename=query.from_user.id,
            startdate=data['startdate'], enddate=data['enddate'], total=total
        )
        pdf_file = FSInputFile(
            f'/pdf_files/hike_menu_{query.from_user.id}.pdf'
        )
        await query.message.answer_document(pdf_file)
