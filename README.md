Шаг 1: Запустите команду "docker-compose up" для запуска контейнеров, указанных в файле docker-compose.yml.

Шаг 2: Дождитесь, пока Docker загрузит все необходимые образы и запустит контейнеры. После этого вы можете открыть ваше приложение в браузере, используя адрес localhost и порт, указанный в файле docker-compose.yml.

Шаг 3: (необязательно): Если вы хотите остановить контейнеры, нажмите Ctrl+C в командной строке или PowerShell. Если вы хотите удалить контейнеры и связанные с ними ресурсы, запустите команду "docker-compose down".

Вы можете открыть браузер и перейти по адресу http://localhost:8000, чтобы увидеть свое приложение FastAPI в действии. Вы также можете открыть браузер и перейти по адресу http://localhost:5050, чтобы увидеть интерфейс администратора pgAdmin и подключиться к базе данных PostgreSQL.

Поключение к БД, добавление таблиц и тестовых данных:

1. Откройте браузер и перейдите на страницу http://localhost:5050. Вы увидите страницу входа в pgAdmin.

2. Введите логин и пароль для входа в pgAdmin. По умолчанию, логин admin@admin.com, а пароль Admin123.

3. После успешного входа в pgAdmin, нажмите на кнопку Add New Server, чтобы добавить сервер базы данных.

4. Введите имя сервера и перейдите на вкладку Connection.

5. В разделе Host name/address введите db, так как это имя контейнера базы данных в Docker.

6. Введите имя пользователя и пароль, которые вы указали в файле docker-compose.yml для переменных POSTGRES_USER и POSTGRES_PASSWORD.

7. Нажмите на кнопку Save.

8. Теперь вы можете подключиться к базе данных, выбрав сервер, который вы только что создали.

9. Чтобы запустить SQL-запрос, выберите базу данных и откройте вкладку Query Tool.

10. Вставьте SQL-запрос в редактор и нажмите на кнопку Execute. Результаты будут показаны внизу страницы.

Сначала создаём таблицы из скрипта create_table.sql, потом наполняем данными из скрипта input_data.sql
