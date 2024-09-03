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
from app.pdf_creator import pdf_creation
from campaign_handlers import bot


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

routerMenu = Router()


class ChooseIDStates(StatesGroup):
    wait_for_id = State()
    wait_for_people_amount = State()


# хэндлеры для рассчета меню

# хэндлер меню для кнопки
@routerMenu.callback_query(F.data == 'menu')
async def menu_button_handller(query: CallbackQuery, state: FSMContext):
    await menu_handler(query, query.message, state)
    await state.clear()


# хэндлер меню для команды
@routerMenu.message(Command('menu'))
async def menu_command_handller(message: Message, state: FSMContext):
    await menu_handler(message, message, state)
    await state.clear()


async def menu_handler(event_type, message: Message, state: FSMContext):
    if isinstance(event_type, CallbackQuery):
        message = event_type.message
    buttons = [[InlineKeyboardButton(
        text='Выбрать по ID', callback_data='chooseID'
    )], [InlineKeyboardButton(
        text='Последняя запись', callback_data='lastone'
    )]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Меню для конкретного похода,'
                         'или возьмем последнюю запись?',
                         reply_markup=mrkp)
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
    try:
        data['people_amount'] = int(message.text)
        data['feedtypes_amount'] = []

        # определение дней с полным набором приемов пищи
        full_days = data['days_amount'] - 2
        feeds = full_days * 3        # количество приемов в полных днях
        # количество приемов пищи
        meals_full_amount = feeds + data['extra_meal']
        await message.answer(
            f'В этом походе, у вас получается всего'
            f' {meals_full_amount} приемов пищи.'
            f'\nДавайте определим, что вы будете в них есть.'
        )

        first_meal = data.get('firstfood')
        last_day = data.get('days_amount')
        last_meal = data.get('lastfood')

        records = await database.get_menu_all()
        feednames_dict = {
            record['feed_name']: record['feed_type'] for record in records
        }

        # Устанавливаем клавиатуру с меню для каждого сообщения
        buttons = [
            [InlineKeyboardButton(text=name, callback_data=feedtype)]
            for name, feedtype in feednames_dict.items()
        ]
        mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
        meals = utils.meal_counter(first_meal, last_day, last_meal)

        for day_n_meals in meals.items():
            for meal in day_n_meals[1]:
                meal_message = await message.answer(
                            f"День {day_n_meals[0]};  Прием пищи - {meal}",
                            reply_markup=mrkp
                        )
                utils.put_message_into_state(
                    day_n_meals[0], meal_message, data, meal
                )
        await state.set_data(data)
    except ValueError:
        await message.answer('Неверный формат данных! Необходимо ввести количество человек в цифрах.')
    


# хэндлер для предоставления последней записи
@routerMenu.callback_query(F.data == 'lastone')
async def menu_last_writing_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        record = await database.get_campaign_last(tguid=query.from_user.id)
        # определяем длительность похода
        lenght = record['enddate']-record['startdate']

    except TypeError:
        buttons = [[InlineKeyboardButton(
            text='Создать запись', callback_data='create'
        )], [InlineKeyboardButton(
            text='Вернуться в меню', callback_data='menu_button'
        )]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
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
    data['feedtypes_amount'].append(query.data)
    record = await database.get_daily_menu(data['people_amount'], query.data)
    meal_products, meal, day = utils.get_daily_menu_titled(record, data, query)
    day, meal = data[f'message_id{query.message.message_id}'].split('$')

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
        utils.total_by_feedtype(data, data['feedtypes_amount'])
        # создаем массив данных с записями ключей с инфой о походах
        daily_menu = utils.sort_daily_menu(data)
        total = await database.get_total_menu(data['people_amount'], data)
        total = utils.data_from_db_converter(total)
        # создание файлика
        pdf_creation(
            *daily_menu, filename=query.from_user.id,
            startdate=data['startdate'], enddate=data['enddate'], total=total
        )
        pdf_file = FSInputFile(
            f'/pdf_files/hike_menu_{query.from_user.id}.pdf'
        )
        await query.message.answer_document(pdf_file)
