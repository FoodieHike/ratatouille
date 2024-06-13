import re
from collections import defaultdict

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


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
    import re
from collections import defaultdict

def meal_total_count(data):
    if not isinstance(data, list):
        data = [data]

    product_groups = defaultdict(int)  # Изменено на int для подсчета суммы
    product_row = re.compile(r'(\d+ [^\n]+)')  # Шаблон для выделения строки с продуктами и количествами
    digits = re.compile(r'\d+')  # Шаблон для выделения чисел

    for item in data:
        products = product_row.findall(item)  # Находим строки с продуктами и количествами
        for product in products:
            clean_product = re.sub(r'\d+ ', '', product)  # Выделяем название продукта
            amount = sum(map(int, digits.findall(product)))  # Подсчитываем сумму всех количеств
            product_groups[clean_product] += amount  # Суммируем количества для каждого продукта

    # Конвертируем ключи и значения словаря в строки и объединяем их одной строкой
    converted = '\n'.join(' '.join([key, str(value)]) for key, value in product_groups.items())

    # Переносим единицы измерения в конец строки
    pattern = r"^(гр|шт)\s+(.*?)(?:\s+\1)?$"
    result = re.sub(pattern, r"\2 \1", converted, flags=re.MULTILINE)
    
    return result

# утилита для создания pdf файла с меню для похода
def pdf_creation(*meal_products, filename, startdate, enddate, total):
    # Регистрируем шрифт, поддерживающий кириллицу
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    # Регистрация жирного шрифта
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

    pdf_catalog = f'/pdf_files/hike_menu_{filename}.pdf'

    # Создаем объект canvas с размером страницы A4
    page = canvas.Canvas(pdf_catalog, pagesize=A4)
    width, height = A4  # Ширина и высота страницы A4

    # Начальная позиция
    y_position = height - 50

    # Добавляем изображение
    image_path = '/images/bot_logo.png'
    page.drawImage(image_path, x=200, y=y_position-100, width=180, height=150)

    # Заголовок
    title = f'Походное меню (период с {startdate} по {enddate})'

    y_position -= 150
    # Установка жирного шрифта
    page.setFont('DejaVuSans-Bold', 12)

    for row in title.split('\n'):
        page.drawString(120, y_position, row)

    # Устанавливаем шрифт и размер
    page.setFont('DejaVuSans', 12)
    if y_position > 50:
        for row in meal_products:

            # Добавляем текст после изображения
            y_position -= 50  # Смещаем позицию для текста после изображения
            for product in row.split('\n'):
                page.drawString(50, y_position,  product)
                y_position -= 15
                if y_position < 50:
                    page.showPage()
                    y_position = 800
                    page.setFont('DejaVuSans', 12)
    else:
        page.showPage()
        y_position = 800

    fin = 'Общее количество всех продуктов на поход'

    y_position -= 100

    # Установка жирного шрифта
    page.setFont('DejaVuSans-Bold', 12)

    if y_position > 80:
        for row in fin.split('\n'):
            page.drawString(120, y_position, row)
    else:
        page.showPage()
        y_position = 800
        # Установка жирного шрифта
        page.setFont('DejaVuSans-Bold', 12)
        for row in fin.split('\n'):
            page.drawString(120, y_position, row)

    y_position -= 30
    # Устанавливаем шрифт и размер
    page.setFont('DejaVuSans', 12)
    if y_position > 50:
        for row in total.split('\n'):
            page.drawString(50, y_position,  row)
            y_position -= 15
            if y_position < 50:
                page.showPage()
                y_position = 800
                page.setFont('DejaVuSans', 12)
    else:
        page.showPage()
        y_position = 800

    # Завершаем
    # страницу и сохраняем PDF
    page.showPage()
    page.save()
