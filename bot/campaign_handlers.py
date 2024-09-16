from aiogram import Router, Bot, F
from aiogram.types import Message, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiogram.enums.parse_mode import ParseMode
import secrets

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, \
    get_user_locale


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app.utils as utils
from app.strings import *
import app.database as database
from bot_schemas import DBCreateContext, UserRegistration, ShowStates
from app.schemas import FeedTypes

from dotenv import load_dotenv


current_file_dir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(current_file_dir, '..', '.env')

load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')


# объекты для функционирования бота:

routerCampaign = Router()

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)


# хэндлеры

# стартовый хэндлер:
@routerCampaign.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    buttons = [
        [InlineKeyboardButton(
            text=CREATE_NEW_CAMPAIGN, callback_data='create'
        )],
        [InlineKeyboardButton(
            text=SHOW_CAMPAIGN, callback_data='show'
        )],
        [InlineKeyboardButton(
            text=CREATE_MENU, callback_data='menu'
        )]
    ]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        text=BOT_WELCOME_MESSAGE,
             reply_markup=mrkp
    )


# хэндлеры для команды create:
# хэндлер под команду:
@routerCampaign.message(Command('create'))
async def create_command_handler(message: Message, state: FSMContext):
    await state.clear()
    await create_handler(message, state, message=message)


# хэндлер под встроенную кнопку:
@routerCampaign.callback_query(F.data == 'create')
async def create_button_handler(query: CallbackQuery, state: FSMContext):
    await create_handler(query, state)


async def create_handler(event_type,
                         state: FSMContext,
                         message: Message = None):
    if isinstance(event_type, CallbackQuery):
        await bot.delete_message(
            chat_id=event_type.message.chat.id,
            message_id=event_type.message.message_id
        )
        message = event_type.message
    user = await database.users_check(event_type.from_user.id)
    if user:
        await message.answer(
            CHOOSE_START_DATE,
            reply_markup=await SimpleCalendar(
                locale=await get_user_locale(event_type.from_user)
            ).start_calendar()
        )
    else:
        await message.answer(
            BOT_WELCOME_MESSAGE_AND_CREATE_USER
        )
        await state.set_state(UserRegistration.register)


# Создание нового пользователя (сработает, если чекер не найдет его в таблице)
@routerCampaign.message(UserRegistration.register)
async def registration_handler(message: Message, state: FSMContext):
    data = {'name': message.text}
    # заглушка для пароля (пока хз, зачем он)
    await database.create_user(
        name=data['name'],
        password=secrets.token_hex(16),
        tguid=message.from_user.id
    )
    user = await database.users_check(tguid=message.from_user.id)
    if user:
        await message.answer(
            START_CAMPAIGN_CREATE_1+message.text+START_CAMPAIGN_CREATE_2,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(
                    text=BUTTON_GO_TO_RECORD, callback_data='create',
                )]]
            )
        )


# хэндлер для календаря, реагирует на календарные ивенты
@routerCampaign.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(
    query: CallbackQuery,
    callback_data: CallbackData,
    state: FSMContext
):
    calendar = SimpleCalendar(
        locale=await get_user_locale(query.from_user), show_alerts=True
    )
    calendar.set_dates_range(
        datetime.now()-timedelta(days=1), datetime.now()+timedelta(days=365)
    )
    selected, date = await calendar.process_selection(query, callback_data)
    if selected:
        data = await state.get_data()
        try:
            data['startdate']
        except KeyError:
            data['startdate'] = date
            await state.set_data(data)
            await query.message.answer(
                START_DATE+date.strftime("%Y-%m-%d"),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text=BUTTON_DATE_SELECTION, callback_data=' '
                        )]
                    ])
            )
            await state.set_state(DBCreateContext.wait_for_enddate)
        else:
            data['enddate'] = date
            await state.set_data(data)
            await query.message.answer(
                END_DATE+date.strftime("%Y-%m-%d")
            )
            buttons = [[
                InlineKeyboardButton(text=BUTTON_BREAKFAST, callback_data='1'),
                InlineKeyboardButton(text=BUTTON_LUNCH, callback_data='2'),
                InlineKeyboardButton(text=BUTTON_DINNER, callback_data='3')
            ]]
            mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.answer(
                ENTER_FIRST_MEAL, reply_markup=mrkp
            )
            await state.set_state(DBCreateContext.wait_for_firstfood)


# обработчик для enddate
@routerCampaign.callback_query(DBCreateContext.wait_for_enddate)
async def process_enddate(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        CHOOSE_END_DATE,
        reply_markup=await SimpleCalendar(
            locale=await get_user_locale(query.from_user)
        ).start_calendar()
    )
    await query.message.edit_reply_markup(reply_markup=None)


# Обработчик для ввода firstfood
@routerCampaign.callback_query(DBCreateContext.wait_for_firstfood)
async def process_firstfood(query: CallbackQuery, state: FSMContext):
    # Получаем текущие данные
    data = await state.get_data()
    data['firstfood'] = int(query.data)
    await state.set_data(data)
    buttons = [[
        InlineKeyboardButton(text=BUTTON_BREAKFAST, callback_data='1'),
        InlineKeyboardButton(text=BUTTON_LUNCH, callback_data='2'),
        InlineKeyboardButton(text=BUTTON_DINNER, callback_data='3')
    ]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
    await query.message.answer(
        ENTER_LAST_MEAL, reply_markup=mrkp
    )
    await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@routerCampaign.callback_query(DBCreateContext.wait_for_lastfood)
async def process_lastfood(query: CallbackQuery, state: FSMContext):
    # Получаем текущие данные
    data = await state.get_data()
    data['lastfood'] = int(query.data)
    await state.set_data(data)
    record = await database.create_campaign_bot(
        campaign=data, tguid=query.from_user.id
    )

    # определяем длину похода
    lenght = data['enddate'] - data['startdate']
    lenght = lenght.days+1
    btn = [
        [InlineKeyboardButton(
            text=BUTTON_GO_TO_MENU,
            callback_data='menu_button'
        )],
        [InlineKeyboardButton(
            text=BUTTON_CREATE_MENU,
            callback_data='menu'
        )]
    ]
    mrkp = InlineKeyboardMarkup(inline_keyboard=btn)

    await query.message.answer(
        FINAL_CAMP_CREATE_MSG_1+
        str(lenght)+' '+
        str(utils.syntax_specifier(lenght))+
        FINAL_CAMP_CREATE_MSG_2+
        str(record["id"]),
        reply_markup=mrkp
    )
    await state.clear()


# кнопочный хэндлер для отображения записи похода
@routerCampaign.callback_query(F.data == 'show')
async def show_button_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_handler(query, state)


# командный хэндлер для отображения записи похода
@routerCampaign.message(Command('show'))
async def show_command_handler(message: Message, state: FSMContext):
    await state.clear()
    await show_handler(message, state, message=message)


async def show_handler(event_type, state: FSMContext, message: Message = None):
    if isinstance(event_type, CallbackQuery):
        await bot.delete_message(
            chat_id=event_type.message.chat.id,
            message_id=event_type.message.message_id
        )
        message = event_type.message
    buttons = [
        [InlineKeyboardButton(
            text=BUTTON_SHOW_ALL, callback_data='all'
        )],
        [InlineKeyboardButton(
            text=BUTTON_SHOW_SPECIFIC, callback_data='current'
        )]
    ]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text=BUTTON_CHOOSE_OPTION, reply_markup=mrkp)


# хэндлер для выведения всех записей:
@routerCampaign.callback_query(F.data == 'all')
async def show_all_handler(query: CallbackQuery):
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    record = await database.get_campaign_all(tguid=query.from_user.id)
    btn = [[InlineKeyboardButton(
        text=BUTTON_GO_TO_MENU, callback_data='menu_button'
    )]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
    if record:
        rows = [
             SHOW_ALL_MESSAGE_1+str(count + 1)+':'+
            SHOW_ALL_MESSAGE_2+str(row["id"])+';'+
            SHOW_ALL_MESSAGE_3+str(row["startdate"])+';'+
            SHOW_ALL_MESSAGE_4+str(row["enddate"])+';'+
            SHOW_ALL_MESSAGE_5+FeedTypes.from_num(int(row["firstfood"]))+';'+
            SHOW_ALL_MESSAGE_6+FeedTypes.from_num(int(row["firstfood"]))+'\n'
            for count, row in enumerate(record)
        ]

        await query.message.answer(
            'Ваши данные:\n'+'\n'.join(rows),
            reply_markup=mrkp
        )
    else:
        await query.message.answer(
            'У Вас пока нет записей, но можете их создать:',
            reply_markup=mrkp
        )


# хэндлер для выведения конкретной записи:
@routerCampaign.callback_query(F.data == 'current')
async def show_current_handler(query: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id)
    record = await database.get_campaign_all(tguid=query.from_user.id)
    if record:
        await query.message.answer('Введите ID записи:')
        await state.set_state(ShowStates.putID)
    else:
        btn = [[InlineKeyboardButton(
            text='Выйти в меню', callback_data='menu_button')]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
        await query.message.answer(
            'У Вас пока нет записей, но можете их создать:',
            reply_markup=mrkp)


# хэндлер для выведения конкретной записи (второй):
@routerCampaign.message(ShowStates.putID)
async def show_current_process(message: Message, state: FSMContext):
    try:
        record = await database.get_campaign_by_id(
            tguid=message.from_user.id, record_id=message.text
        )
        firstfood = FeedTypes.from_num(int(record['firstfood']))
        lastfood = FeedTypes.from_num(int(record['lastfood']))

        btn = [[InlineKeyboardButton(
            text='Выйти в меню', callback_data='menu_button')]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
        await message.answer(
            f'Ваша запись:\n'
            f'дата начала похода - {record["startdate"]}\n'
            f'дата окончания похода -  {record["enddate"]}\n'
            f'первый прием пищи - {firstfood}\n'
            f'последний прием пищи - {lastfood}',
            reply_markup=mrkp
        )
    except TypeError:
        await message.answer('Такой в ваших записях нет. Попробуйте другой id')
    except ValueError:
        await message.answer(
            '''Неправильная форма записи!
Введите пожалуйста, корректный id (натуральное число):'''
        )
    else:
        await state.clear()


# хэндлер для обработки Меню:
@routerCampaign.callback_query(F.data == 'menu_button')
async def menu_handler(query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(
            text='Создать запись', callback_data='create'
        )],
        [InlineKeyboardButton(
            text='Показать запись', callback_data='show'
        )],
        [InlineKeyboardButton(
            text='Составить меню для похода', callback_data='menu'
        )]
    ]
    mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)
    await query.message.answer(
        text='Что будем делать дальше?',
        reply_markup=mrkp
    )


# хэндлер-заглушка для help:
@routerCampaign.message(Command('help'))
async def help_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Здесь пока ничего нет, опция в разработке...')
