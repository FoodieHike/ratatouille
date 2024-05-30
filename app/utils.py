import re
from collections import defaultdict


# утилита для распределения типов приемов пищи по порядку
def meals_distributor(first_meal, meals_amount):
    day_meals = [1, 2, 3]
    meals_amount = [x for x in range(1, meals_amount+1)]
    result = {}

    if first_meal == 3:
        count = 2
    elif first_meal == 2:
        count = 1
    else:
        count = 0
    for meal in meals_amount:
        result[meal] = day_meals[count]
        count += 1
        if count > 2:
            count = 0
    return result


# для подсчета всех продуктов
def meal_total_count(data):
    if not isinstance(data, list):
        data = [data]
    product_groups = defaultdict(list)
    #  шаблон для выделения строки
    # с информацией по количеству определенного продукта
    # product_row=re.compile(r'(\d+ гр [^\n]+|\d+ шт [^\n]+)')
    product_row = re.compile(r'(\d+ [^\n]+)')
    # шаблон для выделния количества
    digits = re.compile(r'\d+')
    for item in data:
        #  находим строку с продуктами и количеством по шаблону
        products = product_row.findall(item)
        for product in products:
            #  выделяем только название продукта для ключа в словаре
            clean_product = re.sub(r'\d+ ', '', product)
            amount = digits.findall(product)

            # цикл для преобразования
            # строчных значений массива amount в целые числа
            for index in range(len(amount)):
                amount[index] = int(amount[index])
            # закидываем все колличественные значения в словарь
            # (ключ - наименование продукта)
            product_groups[clean_product].extend(amount)
        # складываем все значения в списках словаря продуктов
        for key in product_groups:
            x = 0
            for amount in product_groups[key]:
                x += amount
            product_groups[key] = x
    # конвертируем ключи и значения словаря
    # в строки, послек чего соединяем их в одну строку
    converted = [
        ' '.join([key, str(value)]) for key, value in product_groups.items()
    ]
    temp_res = '\n'.join(converted)
    # переносим единицы в конец строки
    pattern = r"^(гр|шт)\s+(.*?)(?:\s+\1)?$"
    result = re.sub(pattern, r"\2 \1", temp_res, flags=re.MULTILINE)
    return result
