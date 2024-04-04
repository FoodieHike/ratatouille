from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch




def pdf_creation(*meal_products, filename, startdate, enddate):
    # Регистрируем шрифт, поддерживающий кириллицу
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    # Регистрация жирного шрифта
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

    pdf_catalog=f'/pdf_files/hike_menu_{filename}.pdf'

    # Создаем объект canvas с размером страницы A4
    c = canvas.Canvas(pdf_catalog, pagesize=A4)
    width, height = A4  # Ширина и высота страницы A4

    # Начальная позиция
    y_position = height - 50


    # Добавляем изображение
    image_path = '/images/bot_logo.png'  # Замените на путь к вашему изображению
    c.drawImage(image_path, x=200, y=y_position-100, width=180, height=150)  # Регулируйте размер и положение под ваш случай




    # Заголовок
    title=f'Походное меню (период с {startdate} по {enddate})'


    y_position-=150

    c.setFont('DejaVuSans-Bold', 12) # Установка жирного шрифта

    for row in title.split('\n'):
        c.drawString(120, y_position, row)

    # Устанавливаем шрифт и размер
    c.setFont('DejaVuSans', 12)
    if y_position>50:
        for row in meal_products:

            # Добавляем текст после изображения
            y_position -= 50  # Смещаем позицию для текста после изображения
            for product in row.split('\n'):
                c.drawString(50, y_position,  product)
                y_position -= 15
                if y_position<50:
                    c.showPage()
                    y_position=800
                    c.setFont('DejaVuSans', 12)
                    
    else:
        c.showPage()
        y_position=800


    # Завершаем страницу и сохраняем PDF
    c.showPage()
    c.save()
