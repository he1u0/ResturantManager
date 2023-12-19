from flask import Flask, redirect, request, url_for
from jinja2 import Environment, PackageLoader

import server_db as db
from templates.data_list import OrderList

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
    user_role = request.cookies.get('role')
    # if user_name and user_role == '1':  # 有用户登录且用户角色为商家 则转入商家管理
    #     return redirect(url_for('manager'))
    # 否则进入用户定餐界面
    if request.method == 'POST':
        # 获取菜品ID
        cid = request.form.get('cid')
        # 获取用户ID
        uid = request.cookies.get('uid')
        # 创建新的订单
        local_db = db.open_database()
        db.add_order(local_db, uid, cid)
        orders = db.get_order_by_id(db.open_database(), request.cookies.get('uid'), 0)
        # 转换一下
        order_list = []
        for order in orders:
            all_cp = db.get_order_by_id(db.open_database(), request.cookies.get('uid'), 0)
            order_list.append(OrderList(order_id=order.id,
                                        s_name=db.get_cp(db.open_database(), order.cid),
                                        c_name=db.open_database()[order.id],
                                        status="正在制作"))
            order_list.append(orders)
        local_db.commit()
        return get('order_list.html').render(user_name=user_name, orders=orders)
    all_course = db.get_all_menu(db.open_database())
    return get('order.html').render(cp=all_course, user_name=user_name)


if __name__ == '__main__':
    app.debug = True
    app.run('127.0.0.1', 1080)
