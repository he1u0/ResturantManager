from flask import Flask, redirect, request, url_for
from jinja2 import Environment, PackageLoader

import server_db as db

app = Flask(__name__)
get = Environment(loader=PackageLoader('server', 'templates')).get_template


@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('user_name', '')
    response.set_cookie('role', '')
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_name = request.form.get('user_name', '')
    password = request.form.get('password', '')
    err_info = ''
    if request.method == 'POST':
        ck = db.check_user(db.open_database(), user_name, password)
        if ck[0] == 0:
            response = redirect(url_for('order'))
            response.set_cookie('user_name', user_name)
            response.set_cookie('role', '{}'.format(ck[1]))
            response.set_cookie('uid', "{}".format(ck[2]))
            return response
        else:
            err_info = ck[1]
    return get('login.html').render(user_name=user_name, err_info=err_info)


@app.route('/manager', methods=['GET', 'POST'])
def manager():  # 用户管理
    user_name = request.cookies.get('user_name')
    return get('manager_u.html').render(user_name=user_name)


@app.route('/', methods=['GET', 'POST'])
def order():  # 定菜
    user_name = request.cookies.get('user_name')
    user_role = request.cookies.get('role')
    if user_name and user_role == '1':  # 有用户登录且用户角色为商家 则转入商家管理
        return redirect(url_for('manager'))
    # 否则进入用户定餐界面
    if request.method == 'POST':
        # 获取菜品ID
        cid = request.form.get('cid')
        # 获取用户ID
        uid = request.cookies.get('uid')
        # 创建新的订单
        db.add_order(db.open_database(), uid, cid)
    cp = db.get_all_menu(db.open_database())  # 获取所有菜品
    return get('order.html').render(cp=cp, user_name=user_name)


if __name__ == '__main__':
    app.debug = True
    app.run('127.0.0.1', 1080)
