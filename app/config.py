from dotenv import load_dotenv
import os

current_file_dir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(current_file_dir, '..', '.env')

load_dotenv(dotenv_path=env_path)


# Настройки для базы данных
host = os.getenv('HOST')

database = os.getenv('DATABASE')

user = os.getenv('USER')

password = os.getenv('PASSWORD')

port = os.getenv('PORT')

CONN_PARAMS = {'host': host,
               'database': database,
               'user': user,
               'password': password,
               'port': port}

database_url = f'''postgresql+asyncpg://{CONN_PARAMS['user']}:\
{CONN_PARAMS['password']}@{CONN_PARAMS['host']}:\
{CONN_PARAMS['port']}/{CONN_PARAMS['database']}'''


# Настрорйки для авторизации пользователей
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
HASHED_PASSWORD = os.getenv('HASHED_PASSWORD')