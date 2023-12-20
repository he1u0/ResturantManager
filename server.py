from flask import Flask, redirect, request, url_for
from jinja2 import Environment, PackageLoader

import data_list
import server_db as db
from data_list import OrderList

app = Flask(__name__)
get = Environment(loader=PackageLoader('server', 'templates')).get_template


@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('user_name', '')
    response.set_cookie('role', '')
    response.set_cookie('uid', '')
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
    if request.method == 'POST':
        # 获取菜品ID
        cid = request.form.get('cid')
        # 获取用户ID
        uid = request.cookies.get('uid')
        # 创建新的订单
        local_db = db.open_database()
        db.add_order(local_db, uid, cid)
        local_db.commit()
        orders = db.get_order_by_id(db.open_database(), request.cookies.get('uid'), 0)
        order_list = []
        for _order in orders:
            _id = _order[0]
            _uid = _order[1]
            _sid = _order[2]
            _cid = _order[3]
            _status = _order[4]
            _user_name = db.get_user_by_id(local_db, _uid)
            _business_name = db.get_user_by_id(local_db, _sid)
            _dish_name = db.get_dish_name_by_id(local_db, _cid)
            _status_str = data_list.get_status(_status)
            order_list.append(
                OrderList(order_id=_id, user_name=_user_name, business_name=_business_name, dish_name=_dish_name,
                          status=_status_str)
            )
        local_db.close()
        return get('order_list.html').render(user_name=user_name, orders=order_list)
    all_course = db.get_all_menu(db.open_database())
    return get('order.html').render(cp=all_course, user_name=user_name)


@app.route('/pay')
def pay():
    return get('pay_success.html').render()


if __name__ == '__main__':
    app.debug = True
    app.run('127.0.0.1', 1080)
