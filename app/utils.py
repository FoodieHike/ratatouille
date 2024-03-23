from datetime import datetime, date

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton





#Функции для календаря:
    
def calendar(year, month):      #функция для построения клавиатуры с календарем:
    year=int(year)
    month=int(month)
    row=[]
    rows=[]
    week=['пн', 'вт','ср','чт','пт','сб','вс']
    first_day=datetime(year,month,1)
    empty=first_day.weekday()
    #первая строка с днями недели:
    for day in week:
        row.append(InlineKeyboardButton(text=f'{day}', callback_data='weekday'))
    rows.append(row)
    row=[]
    #добавляем пустые кнопки в сетку календаря:
    for place in range(empty):
        row.append(InlineKeyboardButton(text=' ', callback_data='ignore'))
    #прописываем числа календаря:
    days_amount=(datetime(year,month+1,1) if month<12 else datetime(year+1,1,1)) -first_day
    days_amount=days_amount.days
    for day in range(1, days_amount+1):
        if month<10 and day<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-0{month}-0{day}'))
        elif month<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-0{month}-{day}'))
        elif day<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-{month}-0{day}'))
        else:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-{month}-{day}'))
        if len(row)==7:
            rows.append(row)
            row=[]
    #прописываем последнюю строку календаря, добавляя пустые кнопки
    if row:
        if len(row)<7:
            for i in range(len(row), 7):
                row.append(InlineKeyboardButton(text=' ', callback_data='ignore'))
        rows.append(row)
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows)    
    return mrkp





def months_creator(in_row):     #создает клавиатуру с месяцами
    months=['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
    row=[InlineKeyboardButton(text=day, callback_data=str(x)) for day, x in zip(months, range(1, len(months)+1))]
    rows=[]
    rows_fin=[]
    for i in row:
        rows.append(i)
        if len(rows)==in_row:
            rows_fin.append(rows)
            rows=[]
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows_fin)
    return mrkp





def callback_date_converter(cb_date):       #конвертирует строку с датой в дату
    operand=date(int(cb_date[0:4]), int(cb_date[5:7]), int(cb_date[8:]))
    return operand


#_________________________________________________________________________________________
#Другие утилиты

def uid_creator(checker, conn, uid):        #вытаскивает tg_id из таблицы users (пока функциолнал не нужный, но может быть нужен потом, хз)
    table_row=checker(conn, uid).items()
    table_row=[list(x) for x in table_row]
    return table_row[3][1]