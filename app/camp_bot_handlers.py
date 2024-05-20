from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from aiogram.enums.parse_mode import ParseMode
from psycopg2.errors import InvalidTextRepresentation


import database
import utils
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
async def create_inline_handler(query: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    try:
        user = await database.users_check(tguid=query.from_user.id)
        if user:
            mrkp = utils.months_creator(4)
            await query.message.answer(
                'Выберите месяц для похода:', reply_markup=mrkp
            )
            await query.answer('Будет создана новая запись')
            await state.set_state(DBCreateContext.wait_for_startdate_one)
        else:
            await query.message.answer(
                '''Добро пожаловать в бот! Пропишите имя пользователя\
                    для использования нашего функционала:'''
            )
            await state.set_state(UserRegistration.register)
    except Exception as e:
        await query.message.answer(f'Exception in command camp!!!\n{e}')


# Создание нового пользователя (сработает, если чекер не найдет его в таблице)
@routerCampaign.message(UserRegistration.register)
async def registration_handler(message: Message, state: FSMContext):
    data = {'name': message.text}
    # заглушка для пароля (пока хз, зачем он)
    passgen = ''.join(
        [str(message.from_user.full_name), '_', str(message.from_user.id)[-4:]]
    )
    await database.create_user(
        name=data['name'], password=passgen, tguid=message.from_user.id
    )
    user = await database.users_check(tguid=message.from_user.id)
    if user:
        await message.answer(
            f'отлично, {message.text}, теперь можно приступить к записи похода'
        )
        # входная точка для создания записи вы бд
        mrkp = utils.months_creator(4)
        await message.answer('Выберите месяц для похода:', reply_markup=mrkp)
        await state.set_state(DBCreateContext.wait_for_startdate_one)


# тест новой библиотеки на боте
@routerCampaign.message(Command('create'))
async def camp_create_handler(message: Message, state: FSMContext):
    try:
        user = await database.users_check(tguid=message.from_user.id)
        if user:
            mrkp = utils.months_creator(4)
            await message.answer(
                'Выберите месяц для похода:', reply_markup=mrkp
            )
            await message.answer('Будет создана новая запись')
            await state.set_state(DBCreateContext.wait_for_startdate_one)
        else:
            await message.answer(
                '''Добро пожаловать в бот! Пропишите имя пользователя
                    для использования нашего функционала:'''
            )
            await state.set_state(UserRegistration.register)
    except Exception as e:
        await message.answer(f'Exception in command camp!!!\n{e}')


@routerCampaign.callback_query(DBCreateContext.wait_for_startdate_one)
async def process_startdate(query: CallbackQuery, state: FSMContext):
    month = int(query.data)
    year = datetime.now()
    year = year.strftime('%Y')
    markup = utils.calendar(year, month)
    await query.message.answer(text='Выберите дату:', reply_markup=markup)
    await state.set_state(DBCreateContext.wait_for_startdate_two)


# Обработчик для ввода startdate второй
@routerCampaign.callback_query(DBCreateContext.wait_for_startdate_two)
async def process_startdate_second(query: CallbackQuery, state: FSMContext):
    await query.message.answer(f'Дата начала похода:\n{query.data}')
    await state.set_data({'startdate': query.data})
# открываем новый календарь для следующей даты
    mrkp = utils.months_creator(4)
    await query.message.answer(
        'Выберите месяц окончания похода:', reply_markup=mrkp
    )
    await state.set_state(DBCreateContext.wait_for_enddate_one)


# обработчик для enddate первый
@routerCampaign.callback_query(DBCreateContext.wait_for_enddate_one)
async def process_enddate(query: CallbackQuery, state: FSMContext):
    month = int(query.data)
    year = datetime.now()
    year = year.strftime('%Y')
    markup = utils.calendar(year, month)
    await query.message.answer(
        text='Выберите дату окончания похода:', reply_markup=markup
    )
    await state.set_state(DBCreateContext.wait_for_enddate_two)


# обработчик для enddate второй
@routerCampaign.callback_query(DBCreateContext.wait_for_enddate_two)
async def process_enddate_second(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await query.message.answer(f'Дата окончания:\n{query.data}')
    data['enddate'] = query.data
    await state.set_data(data)
    row = [
        InlineKeyboardButton(text='Завтрак', callback_data='1'),
        InlineKeyboardButton(text='Обед', callback_data='2'),
        InlineKeyboardButton(text='Ужин', callback_data='3')
    ]
    rows = [row]
    mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
    await query.message.answer(
        'Введите первый прием пищи:', reply_markup=mrkp
    )
    await state.set_state(DBCreateContext.wait_for_firstfood)


# Обработчик для ввода firstfood
@routerCampaign.callback_query(DBCreateContext.wait_for_firstfood)
async def process_firstfood(query: CallbackQuery, state: FSMContext):
    # Получаем текущие данные
    data = await state.get_data()
    data['firstfood'] = int(query.data)
    await state.set_data(data)
    row = [
        InlineKeyboardButton(text='Завтрак', callback_data='1'),
        InlineKeyboardButton(text='Обед', callback_data='2'),
        InlineKeyboardButton(text='Ужин', callback_data='3')
    ]
    rows = [row]
    mrkp = InlineKeyboardMarkup(inline_keyboard=rows)
    await query.message.answer(
        'Введите последний прием пищи:', reply_markup=mrkp
    )
    await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@routerCampaign.callback_query(DBCreateContext.wait_for_lastfood)
async def process_lastfood(query: CallbackQuery, state: FSMContext):
    # Получаем текущие данные
    data = await state.get_data()
    data['lastfood'] = int(query.data)
    data['startdate'] = datetime.strptime(data['startdate'], '%Y-%m-%d')
    data['enddate'] = datetime.strptime(data['enddate'], '%Y-%m-%d')
    await state.set_data(data)
    record = await database.create_campaign_bot(
        campaign=data, tguid=query.from_user.id
    )

    # определяем длину похода
    lenght = data['enddate'] - data['startdate']
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
        await query.message.answer(
            f'''Спасибо, данные у меня.\n
            Длительность похода составляет {lenght} день.\n
            ID Вашей записи - {record["id"]}''', reply_markup=mrkp
        )
    elif (
        str(lenght).endswith('2')
        or str(lenght).endswith('3')
        or str(lenght).endswith('4')
    ):
        await query.message.answer(
            f'''Спасибо, данные у меня.\n
            Длительность похода составляет {lenght} дня.\n
            ID Вашей записи - {record["id"]}''', reply_markup=mrkp
        )
    else:
        await query.message.answer(
            f'''Спасибо, данные у меня.\n
            Длительность похода составляет {lenght} дней.\n
            ID Вашей записи - {record["id"]}''', reply_markup=mrkp
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
async def show_all_handler(query: CallbackQuery):
    try:
        await bot.delete_message(
            chat_id=query.message.chat.id, message_id=query.message.message_id
        )
        response = database.get_campaign_all(tguid=query.from_user.id)
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
            await query.message.answer(
                'Ваши данные:\n'+'\n'.join(records), reply_markup=mrkp)
        else:
            btn = [[InlineKeyboardButton(
                text='Выйти в меню', callback_data='menu_button')]]
            mrkp = InlineKeyboardMarkup(inline_keyboard=btn)
            await query.message.answer(
                'У Вас пока нет записей, но можете их создать:',
                reply_markup=mrkp)
    except Exception as e:
        await query.message.answer(f'Exception!!!\n{e.args}')


# хэндлер для выведения конкретной записи:
@routerCampaign.callback_query(lambda cb: cb.data == 'current')
async def show_current_handler(query: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id)
    response = database.get_campaign_all(tguid=query.from_user.id)
    if response:
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
        response = database.get_campaign_by_id(
            tguid=message.from_user.id, record_id=message.text
        )
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
        await message.answer(
            f'''Ваша запись:\n
            дата начала похода - {response['startdate']}\n
            дата окончания похода -  {response['enddate']}\n
            первый прием пищи - {res}\n
            последний прием пищи - {res_s}''',
            reply_markup=mrkp
        )
    except TypeError:
        await message.answer('Такой в ваших записях нет. Попробуйте другой id')
    except ValueError:
        await message.answer('''Неправильная форма записи!\n
                         Введите пожалуйста,
                         корректный id (натуральное число):''')
    except InvalidTextRepresentation:
        await message.answer('''Неправильная форма записи!\n
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
