from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin import Admin, BaseView, expose, AdminIndexView

from psycopg2.extras import DictCursor
import hashlib 


import utils
from database import UsersTable, Database, CampaignTable



#глобальные переменные 

app = Flask(__name__)

dict_for_update={}


#классы для отображения дашбордов и красоты))


class DashBoard(AdminIndexView):
    @expose('/')        # декоратор для указания методов в классах представлений, в админпанели
    def add_data_db(self):
        users=UsersTable.get_users_all(Database.get_connection())
        users=[dict(x) for x in users]
        campaigns=CampaignTable.get_campaign_all(Database.get_connection())
        campaigns=[dict(x) for x in campaigns]
        return self.render('admin/dashboard_index.html', users=users, campaigns=campaigns)

#для отображения списка пользователей в таблице админки
class Users(BaseView):
    @expose('/')
    def any_page(self):
        users=UsersTable.get_users_all(Database.get_connection())
        return self.render('users.html', users=users)
    

class Campaign(BaseView):
    @expose('/')
    def page(self):
        campaigns=CampaignTable.get_campaign_all(Database.get_connection())
        return self.render('campaign.html', campaigns=campaigns)


#Функции для взаимодействия с админкой


#хэндлер для удаления записи из таблицы
@app.route('/admin/users/delete/<int:id>', methods=['POST'])
def delete(id):
    UsersTable.delete_user(Database.get_connection(), id)
    return redirect('/administration/admin/users/')


#для добавления записей в таблицы

#добавление в таблицу пользователей
@app.route('/admin/users/add', methods=['POST'])
def create_user():
    name = request.form['name']
    password = request.form['password']
    tg_id = request.form['tg_id']
    conn = Database.get_connection()
    UsersTable.add_user(conn=conn, name=name, password=password, tg_id=tg_id)
    return redirect('/administration/admin/users/')
    
#добавление в таблицу походов
@app.route('/admin/campaign/add', methods=['POST'])
def add_campaign(user_id=0):
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    firstfood = request.form['firstfood']
    lastfood = request.form['lastfood']
    conn = Database.get_connection()
    print('request received')
    CampaignTable.add_campaign(conn=conn, startdate=startdate, enddate=enddate, firstfood=firstfood, lastfood=lastfood)
    return redirect('/administration/admin/campaign/')
    



#изменение записей

#изменение в таблице пользователей (для отображения страницы с формами для изменения записи)
@app.route('/admin/users/edit/<int:id>/<string:name>/<string:password>/<int:tg_id>')
def edit_user(id, name, password, tg_id):
    dict_for_update['id']=id
    dict_for_update['name']=name
    dict_for_update['password']=password
    dict_for_update['tg_id']=tg_id
    return render_template('users_edit.html')
    



#для изменения записи в таблице пользователей
@app.route('/admin/users/edit/commit', methods=['POST'])
def users_update():
    id=dict_for_update['id']
    #создаем временный словарь для соотнесения названия переменных с данными, полученными от пользователя и ключами словаря с существующими данными записи
    temp_dict={'name':request.form['name'], 'password':request.form['password'], 'tg_id':request.form['tg_id']}
    for key in temp_dict:
        if temp_dict[key]:
            dict_for_update[key]=temp_dict[key]     #если пользователь добавил данные, вносим изменения в глобальный словарь
    conn = Database.get_connection()
    UsersTable.update_users(conn=conn, id=id, tg_id=dict_for_update['tg_id'], password=dict_for_update['password'], name=dict_for_update['name'])
    dict_for_update.clear()
    return redirect('/administration/admin/users/')





#изменение в таблице походов (для отображения страницы с формами для изменения записи)
@app.route('/admin/campaign/edit/<int:id>/<string:startdate>/<string:enddate>/<int:firstfood>/<int:lastfood>/<user_tg_id>')
def edit_campaign(id, startdate, enddate, firstfood, lastfood, user_tg_id):
    dict_for_update['id']=id
    dict_for_update['startdate']=utils.callback_date_converter(startdate)
    dict_for_update['enddate']=utils.callback_date_converter(enddate)
    dict_for_update['firstfood']=firstfood
    dict_for_update['lastfood']=lastfood
    dict_for_update['user_tg_id']=user_tg_id

    return render_template('campaign_edit.html')
    



#для изменения записи в таблице походов
@app.route('/admin/campaign/edit/commit', methods=['POST'])
def campaign_update():
    id=dict_for_update['id']
    #создаем временный словарь для соотнесения названия переменных с данными, полученными от пользователя и ключами словаря с существующими данными записи
    temp_dict={'startdate':request.form['startdate'], 'enddate':request.form['enddate'], 'firstfood':request.form['firstfood'], 'lastfood':request.form['lastfood'], 'user_tg_id':dict_for_update['user_tg_id']}
    for key in temp_dict:
        if temp_dict[key]:
            dict_for_update[key]=temp_dict[key]     #если пользователь добавил данные, вносим изменения в глобальный словарь
    conn = Database.get_connection()
    CampaignTable.update_campaign(conn=conn, id=id, startdate=dict_for_update['startdate'], enddate=dict_for_update['enddate'], firstfood=dict_for_update['firstfood'], lastfood=dict_for_update['lastfood'], user_tg_id=dict_for_update['user_tg_id'])
    dict_for_update.clear()
    return redirect('/administration/admin/campaign/')






# организация дашборда, прописывание нужных разделов

admin = Admin(app, name='Моя админка', template_mode='bootstrap3', endpoint='admin', index_view=DashBoard())
admin.add_view(Users(name='Пользователи'))
admin.add_view(Campaign(name='Походы'))




#аутентификация пользователей





app.secret_key = 'wpww_1488_kkk'

def verify_password(user_password, stored_password):
    return hashlib.md5(user_password.encode()).hexdigest() == stored_password



#для стартовой страницы
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')

    else:
        return 'Вы не зарегистрированы! Хотите войти? <br><a href="/administration/login">Войти</a>'
    

#хэндлер для аутентификации пользователей по логину/паролю
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn=Database.get_connection()
        username = request.form['username']
        password = request.form['password']
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM admins WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and verify_password(password, user['password']):
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Error: Invalid Credentials'
    return render_template('login.html')

#для разлогирования
@app.route('/admin/users/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)