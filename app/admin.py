from flask import Flask, render_template, request, redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView



from database import UsersTable, Database, CampaignTable




app = Flask(__name__)



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

#для стартовой страницы
@app.get('/')
def index():
    return render_template('index.html')



#хэндлер для удаления записи из таблицы
@app.route('/admin/users/delete/<int:id>', methods=['POST'])
def delete(id):
    UsersTable.delete_user(Database.get_connection(), id)
    return redirect('/administration/admin/users/')


#для добавления записи в таблицу
@app.route('/admin/users/add', methods=['POST'])
def create_user():
    name = request.form['name']
    password = request.form['password']
    tg_id = request.form['tg_id']
    conn = Database.get_connection()
    UsersTable.add_user(conn=conn, name=name, password=password, tg_id=tg_id)
    return redirect('/administration/admin/users/')
    

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
    




# организация дашборда, прописывание нужных разделов

admin = Admin(app, name='Моя админка', template_mode='bootstrap3', endpoint='admin', index_view=DashBoard())
admin.add_view(Users(name='Пользователи'))
admin.add_view(Campaign(name='Походы'))



if __name__ == '__main__':
    app.run(debug=True)