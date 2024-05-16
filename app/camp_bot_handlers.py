from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from aiogram.enums.parse_mode import ParseMode
from psycopg2.errors import InvalidTextRepresentation


import utils
import models
from database import UsersTable, Database, BotCampaignTable
from camp_bot_models import DBCreateContext, UserRegistration, ShowStates

from dotenv import load_dotenv
import os

current_file_dir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(current_file_dir, '..', '.env')

load_dotenv(dotenv_path=env_path)

BOT_API = os.getenv('BOT_API')


# глобальные переменные:
today = datetime.now()
today = today.strftime('%Y-%m-%d')


# объекты для функционирования бота:

routerCampaign = Router()

bot = Bot(token=BOT_API, parse_mode=ParseMode.HTML)


# хэндлеры


# стартовый хэндлер:

@routerCampaign.message(Command('start'))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    btn_create = InlineKeyboardButton(
        text='Создать новый поход', callback_data='create'
    )
    btn_show = InlineKeyboardButton(
        text='Показать запись похода', callback_data='show'
    )
    btn_menu = InlineKeyboardButton(
        text='Составить меню для похода', callback_data='food_menu_button'
    )
    row = [[btn_create], [btn_show], [btn_menu]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)
    await msg.answer(text='''Привет. Меня зовут Hike Helper.
                     Я помогу тебе разработать меню для твоего похода
                     и рассчитаю все необходимые для него продукты.
                     Выбери, что будем делать дальше:''',
                     reply_markup=mrkp)


# хэндлеры для команды create:

# альтернативный обработчик под встроенную кнопку:
@routerCampaign.callback_query(lambda cb: cb.data == 'create')
async def create_inline_handler(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        user = UsersTable(Database.get_connection())
        user = user.table_users_check(uid=qry.from_user.id)
        if user:
            mrkp = utils.months_creator(4)
            await qry.message.answer(
                'Выберите месяц для похода:', reply_markup=mrkp
            )
            await qry.answer('Будет создана новая запись')
            await state.set_state(DBCreateContext.wait_for_startdate_one)
        else:
            await qry.message.answer(
                '''Добро пожаловать в бот! Пропишите имя пользователя
                    для использования нашего функционала:'''
            )
            await state.set_state(UserRegistration.register)
    except Exception as e:
        await qry.message.answer(f'Exception in command camp!!!\n{e}')


# Обработчик начальной команды для взаимодействий с таблицей походов
@routerCampaign.message(Command('create'))
async def create_camp_handler(msg: Message, state: FSMContext):
    await state.clear()
    try:
        user = UsersTable(Database.get_connection())
        user = user.table_users_check(uid=msg.from_user.id)
        if user:
            mrkp = utils.months_creator(4)
            await msg.answer('Выберите месяц для похода:', reply_markup=mrkp)
            await state.set_state(DBCreateContext.wait_for_startdate_one)
        else:
            await msg.answer(
                '''Добро пожаловать в бот! Пропишите имя пользователя
                    для использования нашего функционала:'''
            )
            await state.set_state(UserRegistration.register)
    except Exception as e:
        await msg.answer(f'Exception in create_camp_handler!!!\n{e}')


# Создание нового пользователя (сработает, если чекер не найдет его в таблице)
@routerCampaign.message(UserRegistration.register)
async def registration_handler(msg: Message, state: FSMContext):
    data = {'name': msg.text}
    # заглушка для пароля (пока хз, зачем он)
    passgen = ''.join(
        [str(msg.from_user.full_name), '_', str(msg.from_user.id)[-4:]]
    )
    creation = UsersTable(Database.get_connection())
    creation.create_user_bot_auto(
        password=passgen, tgid=msg.from_user.id, user=data
    )
    await msg.answer(
        f'отлично, {msg.text}, теперь можно приступить к записи похода'
    )
    mrkp = utils.months_creator(4)
    await msg.answer('Выберите месяц для похода:', reply_markup=mrkp)
    await state.set_state(DBCreateContext.wait_for_startdate_one)


# Обработчик для ввода startdate  первый
@routerCampaign.callback_query(DBCreateContext.wait_for_startdate_one)
async def process_startdate(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        month = int(qry.data)
        year = datetime.now()
        year = year.strftime('%Y')
        markup = utils.calendar(year, month)
        await qry.message.answer(text='Выберите дату:', reply_markup=markup)
    except Exception as e:
        await qry.message.answer(
            f'Произошла чудовищная ошибка в process_startdate!\n{e}'
        )
    else:
        await state.set_state(DBCreateContext.wait_for_startdate_two)


# Обработчик для ввода startdate второй
@routerCampaign.callback_query(DBCreateContext.wait_for_startdate_two)
async def process_startdate_second(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        # валидируем дату и закидываем в хранилище данных состояний
        if qry.data < today:
            raise ValueError
        else:
            await qry.message.answer(f'Дата начала похода:\n{qry.data}')
            await state.set_data({'startdate': qry.data})

        # открываем новый календарь для следующей даты
            mrkp = utils.months_creator(4)
            await qry.message.answer(
                'Выберите месяц окончания похода:', reply_markup=mrkp
            )

    # Обработчики ошибок
    except ValueError:
        mrkp = utils.months_creator(4)
        await qry.message.answer(
            '''Введенная дата должна быть не ранее сегодняшнего дня!\n
            Введите корректную дату:''', reply_markup=mrkp
        )
        await state.set_state(DBCreateContext.wait_for_startdate_one)
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_one)


# обработчик для enddate первый
@routerCampaign.callback_query(DBCreateContext.wait_for_enddate_one)
async def process_enddate(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        month = int(qry.data)
        year = datetime.now()
        year = year.strftime('%Y')
        markup = utils.calendar(year, month)
        await qry.message.answer(
            text='Выберите дату окончания похода:', reply_markup=markup
        )
    except Exception as e:
        await qry.message.answer(
            f'Произошла чудовищная ошибка в process_enddate!\n{e}'
        )
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_two)


# обработчик для enddate второй
@routerCampaign.callback_query(DBCreateContext.wait_for_enddate_two)
async def process_enddate_second(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        data = await state.get_data()
        if data['startdate'] > qry.data:
            raise ValueError
        else:
            await qry.message.answer(f'Дата окончания:\n{qry.data}')
            data = await state.get_data()
            data['enddate'] = qry.data
            await state.set_data(data)
    except ValueError:
        mrkp = utils.months_creator(4)
        await qry.message.answer(
            '''Введенная дата должна быть позже введенной даты начала похода!\n
            Введите корректную дату:''', reply_markup=mrkp
        )
        await state.set_state(DBCreateContext.wait_for_enddate_one)
    else:
        row = [
            InlineKeyboardButton(text='Завтрак', callback_data='1'),
            InlineKeyboardButton(text='Обед', callback_data='2'),
            InlineKeyboardButton(text='Ужин', callback_data='3')
        ]
        rows = [row]
        mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
        await qry.message.answer(
            'Введите первый прием пищи:', reply_markup=mrkp
        )
        await state.set_state(DBCreateContext.wait_for_firstfood)


# Обработчик для ввода firstfood
@routerCampaign.callback_query(DBCreateContext.wait_for_firstfood)
async def process_firstfood(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        models.FeedType(qry.data)
    except Exception as e:
        await qry.message.answer(
            f'Произошла чудовищная ошибка в process_firstfood:\n{e}'
        )
    else:
        # Получаем текущие данные
        data = await state.get_data()
        data['firstfood'] = qry.data
        await state.set_data(data)
        row = [
            InlineKeyboardButton(text='Завтрак', callback_data='1'),
            InlineKeyboardButton(text='Обед', callback_data='2'),
            InlineKeyboardButton(text='Ужин', callback_data='3')
        ]
        rows = [row]
        mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
        await qry.message.answer(
            'Введите последний прием пищи:', reply_markup=mrkp
        )
        await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@routerCampaign.callback_query(DBCreateContext.wait_for_lastfood)
async def process_lastfood(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    try:
        models.FeedType(qry.data)
    except Exception as e:
        await qry.message.answer(f'We got an exception here:\n{e}')
    else:
        # Получаем текущие данные
        data = await state.get_data()
        data['lastfood'] = qry.data
        await state.set_data(data)
        creation = BotCampaignTable(Database.get_connection())
        creation.create_campaign(campaign=data, u_id=qry.from_user.id)
        response = creation.get_campaign_last(qry.from_user.id)

        # определяем длину похода
        lenght = utils.callback_date_converter(
            data['enddate']
        )-utils.callback_date_converter(data['startdate'])
        lenght = lenght.days+1
        btn = [
            [InlineKeyboardButton(
                text='Выйти в меню',
                callback_data='menu_button'
            )],
            [InlineKeyboardButton(
                text='Заполнить меню для похода',
                callback_data='food_menu_button'
            )]
        ]
        mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
        if str(lenght).endswith('1'):
            await qry.message.answer(
                f'''Спасибо, данные у меня.\n
                Длительность похода составляет {lenght} день.\n
                ID Вашей записи - {response["id"]}''', reply_markup=mrkp
            )
        elif str(lenght).endswith('2') or str(lenght).endswith('3') or str(lenght).endswith('4'):
            await qry.message.answer(
                f'''Спасибо, данные у меня.\n
                Длительность похода составляет {lenght} дня.\n
                ID Вашей записи - {response["id"]}''', reply_markup=mrkp
            )
        else:
            await qry.message.answer(
                f'''Спасибо, данные у меня.\n
                Длительность похода составляет {lenght} дней.\n
                ID Вашей записи - {response["id"]}''', reply_markup=mrkp
            )
        await state.clear()


# Обработчики команды show для просмотра данных из бд:


# альтернативный обработчик под встроенную кнопку:
@routerCampaign.callback_query(lambda cb: cb.data == 'show')
async def show_inline_handler(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id
    )
    await state.clear()
    row = [
        InlineKeyboardButton(
            text='Показать все записи', callback_data='all'
        ),
        InlineKeyboardButton(
            text='Показать конкретную', callback_data='current'
        )
    ]
    rows = [row]
    mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
    await qry.message.answer(text='Выбирете опцию:', reply_markup=mrkp)


# первый хэндлер для начала работы:
@routerCampaign.message(Command('show'))
async def get_camp_handler(msg: Message, state: FSMContext):
    await state.clear()
    row = [
        InlineKeyboardButton(
            text='Показать все записи', callback_data='all'
        ),
        InlineKeyboardButton(
            text='Показать конкретную', callback_data='current'
        )
    ]
    rows = [row]
    mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
    await msg.answer(text='Выбирете опцию:', reply_markup=mrkp)


# хэндлер для выведения всех записей:
@routerCampaign.callback_query(lambda cb: cb.data == 'all')
async def show_all_handler(qry: CallbackQuery):
    try:
        await bot.delete_message(
            chat_id=qry.message.chat.id, message_id=qry.message.message_id
        )
        response = BotCampaignTable(Database.get_connection())
        response = response.get_campaign_all(uid=str(qry.from_user.id))
        if response:
            records = []
            count = 0
            for row in response:
                firstfood = row['firstfood']
                lastfood = row['lastfood']
                if firstfood == '1':
                    res = 'завтрак'
                elif firstfood == '2':
                    res = 'обед'
                else:
                    res = 'ужин'

                if lastfood == '1':
                    res_s = 'завтрак'
                elif lastfood == '2':
                    res_s = 'обед'
                else:
                    res_s = 'ужин'
                count += 1
                records.append(
                    'Запись ' +
                    str(count) +
                    ':\n ID записи - ' +
                    str(row['id']) +
                    '; дата начала похода - ' +
                    str(row['startdate']) +
                    '; дата окончания похода - ' +
                    str(row['enddate']) +
                    ';\n' +
                    'первый прием пищи - ' +
                    res +
                    '; последний прием пищи - ' +
                    res_s + '\n'
                )
            btn = [[InlineKeyboardButton(
                text='Выйти в меню', callback_data='menu_button'
            )]]
            mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
            await qry.message.answer(
                'Ваши данные:\n'+'\n'.join(records), reply_markup=mrkp)
        else:
            btn = [[InlineKeyboardButton(
                text='Выйти в меню', callback_data='menu_button')]]
            mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
            await qry.message.answer(
                'У Вас пока нет записей, но можете их создать:',
                reply_markup=mrkp)
    except Exception as e:
        await qry.message.answer(f'Exception!!!\n{e.args}')


# хэндлер для выведения конкретной записи:
@routerCampaign.callback_query(lambda cb: cb.data == 'current')
async def show_current_handler(qry: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=qry.message.chat.id, message_id=qry.message.message_id)
    response = BotCampaignTable(Database.get_connection())
    response = response.get_campaign_all(uid=str(qry.from_user.id))
    if response:
        await qry.message.answer('Введите ID записи:')
        await state.set_state(ShowStates.putID)
    else:
        btn = [[InlineKeyboardButton(
            text='Выйти в меню', callback_data='menu_button')]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
        await qry.message.answer(
            'У Вас пока нет записей, но можете их создать:',
            reply_markup=mrkp)


# хэндлер для выведения конкретной записи (второй):
@routerCampaign.message(ShowStates.putID)
async def show_current_process(msg: Message, state: FSMContext):
    try:
        response = BotCampaignTable(Database.get_connection())
        response = response.get_campaign_by_id(
            uid=msg.from_user.id, record_id=msg.text)
        firstfood = response['firstfood']
        lastfood = response['lastfood']
        if firstfood == '1':
            res = 'завтрак'
        elif firstfood == '2':
            res = 'обед'
        else:
            res = 'ужин'

        if lastfood == '1':
            res_s = 'завтрак'
        elif lastfood == '2':
            res_s = 'обед'
        else:
            res_s = 'ужин'
        btn = [[InlineKeyboardButton(
            text='Выйти в меню', callback_data='menu_button')]]
        mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
        await msg.answer(f'''Ваша запись:\n
                         дата начала похода - {response['startdate']}\n
                         дата окончания похода -  {response['enddate']}\n
                         первый прием пищи - {res}\n
                         последний прием пищи - {res_s}''',
                         reply_markup=mrkp)
    except TypeError:
        await msg.answer('Такой в ваших записях нет. Попробуйте другой id')
    except ValueError:
        await msg.answer('''Неправильная форма записи!\n
                         Введите пожалуйста,
                         корректный id (натуральное число):''')
    except InvalidTextRepresentation:
        await msg.answer('''Неправильная форма записи!\n
                         Введите, пожалуйста,
                         корректный ID (натуральное число).''')
    else:
        await state.clear()


# хэндлер для обработки Меню:

@routerCampaign.callback_query(lambda cb: cb.data == 'menu_button')
async def menu_handler(qry: CallbackQuery):
    btn_create = InlineKeyboardButton(
        text='Создать запись', callback_data='create')
    btn_show = InlineKeyboardButton(
        text='Показать запись', callback_data='show')
    btn_menu = InlineKeyboardButton(
        text='Составить меню для похода', callback_data='food_menu_button')
    row = [[btn_create], [btn_show], [btn_menu]]
    mrkp = InlineKeyboardMarkup(inline_keyboard=row)
    await qry.message.answer(text='Что будем делать дальше?',
                             reply_markup=mrkp)


# хэндлер-заглушка для help:


@routerCampaign.message(Command('help'))
async def help_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Здесь пока ничего нет, опция в разработке...')
