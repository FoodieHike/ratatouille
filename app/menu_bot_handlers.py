from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from psycopg2.errors import InvalidTextRepresentation



from database import Database, BotCampaignTable, MenuTable
from utils import callback_date_converter
import utils
import pdf_creator
from camp_bot_handlers import bot

routerMenu=Router()


'''class MenuStates(StatesGroup):
    wait_for_people_amount=State()'''


class ChooseIDStates(StatesGroup):
    wait_for_id=State()
    wait_for_people_amount=State()



#хэндлеры для рассчета меню

#хэндлер для начала работы с меню
@routerMenu.callback_query(lambda cb:cb.data=='food_menu_button')
async def menu_handller(qry:CallbackQuery, state:FSMContext):
    row=[[InlineKeyboardButton(text='Выбрать по ID', callback_data='chooseID')], [InlineKeyboardButton(text='Последняя запись', callback_data='lastone')]]
    mrkp=InlineKeyboardMarkup(inline_keyboard=row)
    await qry.message.answer('Меню для конкретного похода, или Вашей последней записи?', reply_markup=mrkp)
    await state.clear()



    
    
    

#хэндлеры для выбора записи по ID:
    
#первый 
@routerMenu.callback_query(lambda cb:cb.data=='chooseID')
async def id_for_meny_hsndler(qry:CallbackQuery, state:FSMContext):
    await state.clear()
    await qry.message.answer('Напишите ID записи похода:')
    await qry.message.edit_reply_markup(reply_markup=None)
    await state.set_state(ChooseIDStates.wait_for_id)

    
    

#хэндлер для выбора записи по ID (второй)
@routerMenu.message(ChooseIDStates.wait_for_id)
async def choose_id_handler(msg:Message, state:FSMContext):
    try:
        record=BotCampaignTable(Database.get_connection())
        record=record.get_campaign_by_id(uid=msg.from_user.id, record_id=msg.text)
        lenght=record['enddate']-record['startdate']
    except TypeError:
        await msg.answer('У вас пока нет записей')
    else:
        await state.set_data({'days_amount':lenght.days+1})
        data=await state.get_data()
        data['first_meal']=int(record['firstfood'])
        data['last_meal']=int(record['lastfood'])
        data['startdate']=record['startdate']
        data['enddate']=record['enddate']
        data['B1']=0
        data['B2']=0

        #определяем количество дополнительных приемов пищи:
        if record['firstfood']=='1':
            firstday_feed_amount=3
        elif record['firstfood']=='2':
            firstday_feed_amount=2
        else:
            firstday_feed_amount=1

        if record['lastfood']=='1':
            lastday_feed_amount=1
        elif record['lastfood']=='2':
            lastday_feed_amount=2
        else:
            lastday_feed_amount=3
            
        extra_meal=firstday_feed_amount+lastday_feed_amount

        data['extra_meal']=extra_meal
        await state.set_data(data)


        await msg.answer('На сколько человек планируете поход?')
        await state.set_state(ChooseIDStates.wait_for_people_amount)



#Хэндлер рассчитывает количество всех приемов пищи
@routerMenu.message(ChooseIDStates.wait_for_people_amount)
async def menu_process(msg:Message, state:FSMContext):
    data=await state.get_data()
    data['people_amount']=int(msg.text)
    full_days=data['days_amount']-2 #определение дней с полным набором приемов пищи
    feeds=full_days*3        #количество приемов в полных днях

    meals_full_amount=feeds+data['extra_meal']


    await msg.answer(f'В этом походе, у вас получается всего {meals_full_amount} приемов пищи.\nДавайте определим, что вы будете в них есть.\nХранилище данных:{data}')
    first_meal=data['first_meal']
    count_days=data['days_amount']
    last_meal=data['last_meal']
    row=[[InlineKeyboardButton(text='Овсянка и бутер с сыром', callback_data='B1')],[InlineKeyboardButton(text='Пшенка с ковбаськой', callback_data='B2')]]
    mrkp=InlineKeyboardMarkup(inline_keyboard=row)
    
    meals_count=0
    for day in range(1, count_days+1):
        if day==count_days:
            for meal in range(1,last_meal+1):
                meals_count+=1
                if meal==1:
                    feed_type='завтрак'
                elif meal==2:
                    feed_type='обед'
                else:
                    feed_type='ужин'
                meal_msg=await msg.answer(f'День {day};  Прием пищи -  {feed_type}', reply_markup=mrkp)
                message_value='$'.join([str(day), feed_type])
                data[''.join(['msg_id',str(meal_msg.message_id)])]= message_value #запись информации о приеме пищи для распределения данных в конечном сообщении
                

        else:
            for meal in range(first_meal,4):
                meals_count+=1
                if meal==1:
                    feed_type='завтрак'
                elif meal==2:
                    feed_type='обед'
                else:
                    feed_type='ужин'
                meal_msg=await msg.answer(f'День {day};  Прием пищи -  {feed_type}', reply_markup=mrkp)
                message_value='$'.join([str(day), feed_type])
                
                data[''.join(['msg_id',str(meal_msg.message_id)])]= message_value #запись информации о приеме пищи для распределения данных в конечном сообщении
                first_meal+=1
                if first_meal>3:
                    first_meal=1
                    break
    await state.set_data(data)
    
#хэндлер для Овсянка и бутер с сыром
@routerMenu.callback_query(lambda cb:cb.data=='B1')
async def feedtype_b1_handler(qry:CallbackQuery, state:FSMContext):
    data=await state.get_data()
    data['B1']+=1

    record=MenuTable(Database.get_connection())
    record=record.get_menu('B1')
    full_list=[]
    for obj in record:      #формируем сообщение с нужными пропорциями еды (надо будет отдельно функцию написать и бромсить в утилиты)
        temp_row=' '.join([str(obj['quantity']*data['people_amount']),obj['units'],obj['productname']])
        full_list.append(temp_row)
    res='\n'.join(full_list)


    crude_row=data[''.join(['msg_id',str(qry.message.message_id)])]      #достаем информацию о дне и приеме пище (в словаре состояний под номером id сообщения со встроенной кнопкой)

    day,meal=crude_row.split('$')       #распределяем по переменным

    #формирование списка продуктов и счетчика меню
    meal_products=f'Количество продуктов на всех участников похода\n(День похода - {day}, прием пищи - {meal}):\n{res}'
    await qry.message.answer(f'Количество продуктов на всех участников похода (День похода - {day}, прием пищи - {meal}):\n{res}')
    await qry.message.answer(f'cчетчик овсянок - {data["B1"]}')

    products_list=''.join(['prod', str(qry.message.message_id)])     #формирование ключа для записи в pdf

    data[products_list]=meal_products       #запись строки с продуктами для формирования pdf документа

    #работа с удалением сообщения и записи в словаре
    await bot.delete_message(chat_id=qry.message.chat.id, message_id=qry.message.message_id)
    del data[''.join(['msg_id',str(qry.message.message_id)])]
    await state.set_data(data)

    found_key=False

    for key in data:
        if key.startswith('msg_id'):       # проверяем, есть ли неудаленные сообщения, не оконена ли запись
            found_key=True
            break

    if found_key:
        pass
        
    else:
        records_list=[]
        for key in data:
            if key.startswith('prod'):
                records_list.append(data[key])

        await qry.message.answer('Формируем pdf и отправляем...')
        result=pdf_creator.pdf_creation(*records_list, filename=qry.message.chat.id, startdate=data['startdate'], enddate=data['enddate'])
        await qry.message.answer(f'{result}')
        

 
        


        
    

    

    





#хэндлер для пшенки с ковбаськой
@routerMenu.callback_query(lambda cb:cb.data=='B2')
async def feedtype_b1_handler(qry:CallbackQuery, state:FSMContext):
    data=await state.get_data()
    data['B2']+=1
    
    record=MenuTable(Database.get_connection())
    record=record.get_menu('B2')
    full_list=[]
    for obj in record:      #формируем сообщение с нужными пропорциями еды (надо будет отдельно функцию написать и бромсить в утилиты)
        temp_row=' '.join([str(obj['quantity']*data['people_amount']),obj['units'],obj['productname']])
        full_list.append(temp_row)
    res='\n'.join(full_list)

    crude_row=data[''.join(['msg_id',str(qry.message.message_id)])]      #достаем информацию о дне и приеме пище (в словаре состояний под номером id сообщения со встроенной кнопкой)

    day,meal=crude_row.split('$')       #распределяем по переменным

    #формирование списка продуктов и счетчика меню
    meal_products=f'Количество продуктов на всех участников похода\n(День похода - {day}, прием пищи - {meal}):\n{res}'
    await qry.message.answer(f'Количество продуктов на всех участников похода (День похода - {day}, прием пищи - {meal}):\n{res}')
    await qry.message.answer(f'счетчик пшенок - {data["B2"]}')

    products_list=''.join(['prod', str(qry.message.message_id)])     #формирование ключа для записи в pdf

    data[products_list]=meal_products       #запись строки с продуктами для формирования pdf документа

    #работа с удалением сообщения и записи в словаре
    await bot.delete_message(chat_id=qry.message.chat.id, message_id=qry.message.message_id)
    del data[''.join(['msg_id',str(qry.message.message_id)])]
    await state.set_data(data)

    found_key=False

    for key in data:
        if key.startswith('msg_id'):       # проверяем, есть ли неудаленные сообщения, не оконена ли запись
            found_key=True
            break

    if found_key:
        pass
        
    else:
        records_list=[]
        for key in data:
            if key.startswith('prod'):
                records_list.append(data[key])

        await qry.message.answer('Формируем pdf и отправляем...')
        pdf_creator.pdf_creation(*records_list, filename=qry.message.chat.id, startdate=data['startdate'], enddate=data['enddate'])









#хэндлер для предоставления последней записи
@routerMenu.callback_query(lambda cb:cb.data=='lastone')
async def menu_last_writing_handler(qry:CallbackQuery, state:FSMContext):
    await state.clear()
    date=await state.get_data()
    try:
        record=BotCampaignTable(Database.get_connection())
        record=record.get_campaign_last(qry.from_user.id)
        firstfood=record['firstfood']
        lastfood=record['lastfood']
        lenght=record['enddate']-record['startdate']
        if firstfood=='1':
            res='завтрак'
        elif firstfood=='2':
            res='обед'
        else:
            res='ужин' 

        if lastfood=='1':
            res_s='завтрак'
        elif lastfood=='2':
            res_s='обед'
        else:
            res_s='ужин' 
        btn=[[InlineKeyboardButton(text='Выйти в меню', callback_data='menu_button')]]
        mrkp=InlineKeyboardMarkup(inline_keyboard=btn)
        await qry.message.answer(f"Ваша запись:\nдата начала похода - {record['startdate']}\nдата окончания похода -  {record['enddate']}\nпервый прием пищи - {res}\nпоследний прием пищи - {res_s}\nдлительность- {lenght.days}\nхранилище состояний - {date}",
                         reply_markup=mrkp)
    except TypeError:
        row=[[InlineKeyboardButton(text='Создать запись',callback_data='create')],[InlineKeyboardButton(text='Вернуться в меню', callback_data='menu_button')]]
        mrkp=InlineKeyboardMarkup(inline_keyboard=row)
        await qry.message.answer('К сожалению не удалось найти ни одной записию Может хотите создать новую?', reply_markup=mrkp)
    except ValueError:
        await qry.message.answer('Неправильная форма записи!\nВведите пожалуйста корректный id (натуральное число):')
    except InvalidTextRepresentation:
        await qry.message.answer('Неправильная форма записи!\nВведите, пожалуйста, корректный ID (натуральное число).')
    else:
        await state.clear()
        await qry.message.edit_reply_markup(reply_markup=None)






 