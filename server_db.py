# 对于食堂这个应用 需要建立三个数据库
# user:     存储用户相关内容 用户ID 账号 密码 角色
# role:     角色 0:顾客  1:商家
# cai ping: 存储菜品相关内容 菜品ID 菜名 描述 价格 商家账号
# ding dan: 存储订单内容 订单ID 顾客ID 商家ID 菜品ID 订单状态
# status:   状态：0:等待接单  1:正在制作  2:正在派送  3:订单完成

import os
import sqlite3
from collections import namedtuple


def open_database(path='database.db'):
    is_new_db = not os.path.exists(path)
    db = sqlite3.connect(path)
    if is_new_db:
        c = db.cursor()
        # 创建用户表
        c.execute('CREATE TABLE user (id INTEGER PRIMARY KEY, uname TEXT, upw TEXT, urole INTEGER, utext TEXT)')
        add_user(db, 'zhang', '123456', 0, '测试用户1')
        add_user(db, 'li', '123456', 0, '测试用户2')
        add_user(db, 'ma', '123456', 1, '大胡子面片')
        add_user(db, 'zhao', '123456', 1, '小赵炒饭')

        # 创建菜品表
        c.execute('Create Table caiping (id Integer Primary Key,'
                  'cname Text, cdis Text, uid Integer, utxt Text, cprice Integer)')
        add_goods(db, '炒面片', '香喷喷的羊肉面片', 3, 10)
        add_goods(db, '烩面片', '纯羊肉汤面片', 3, 8)
        add_goods(db, '蛋炒饭', '醇香炒饭，回味无穷', 4, 8)
        add_goods(db, '扬州炒饭', '正宗淮扬菜味道', 4, 12)

        # 创建订单表
        c.execute('Create Table dingdan (id Integer Primary Key,'
                  'uid, sid, cid, status)')
        add_order(db, 1, 1)
        add_order(db, 2, 3)
        # 创建订单表
        db.commit()
    return db


# 创建订单
# 数据库  用户ID  菜品ID
def add_order(db, uid, cid):
    # 根据菜品ID 获取 商家ID
    sql_str = 'select uid from caiping where id = {}'.format(cid)
    c = db.cursor()
    c.execute(sql_str)
    row_data = namedtuple('Row', [tup[0] for tup in c.description])
    result = [row_data(*row) for row in c.fetchall()]
    if len(result) > 0:
        sid = result[0].uid
    else:
        print('无法找到菜品ID为 {} 的商家ID'.format(cid))
        return
    # 写入数据库
    db.cursor().execute('insert into dingdan (uid, sid, cid, status)'
                        ' values (?, ?, ?, 0)', (uid, sid, cid))


# 新建菜品
def add_goods(db, cname, cdis, uid, cprice):
    sql_str = 'select utext from user where id = {}'.format(uid)
    c = db.cursor()
    c.execute(sql_str)
    Row = namedtuple('Row', [tup[0] for tup in c.description])
    result = [Row(*row) for row in c.fetchall()]
    u_text = result[0].utext

    db.cursor().execute('insert into caiping (cname, cdis, uid, utxt, cprice)'
                        ' values (?, ?, ?, ?, ?)', (cname, cdis, uid, u_text, cprice))


# 获取所有菜品
def get_all_menu(db):
    # 以饭馆分组，获取所有菜品
    cursor = db.cursor()
    cursor.execute('select * from caiping order by uid')
    Row = namedtuple('Row', [tup[0] for tup in cursor.description])
    all_cp = [Row(*row) for row in cursor.fetchall()]
    last_id = -1
    cp = []
    temp_goods = []
    for oneRow in all_cp:
        # 判断是否新的商家
        is_new_seller = (last_id != -1) and (last_id != oneRow.uid)
        if is_new_seller:  # 新商家
            cp.append(temp_goods)
            temp_goods = []

        temp_goods.append(oneRow)
        last_id = oneRow.uid
    if len(temp_goods) > 0:
        cp.append(temp_goods)
    return cp


# 创建用户
def add_user(db, uname, pwd, role, text):
    cursor = db.cursor()
    cursor.execute('insert into user (uname, upw, urole, utext)'
                   ' values (?, ?, ?, ?)', (uname, pwd, role, text))
    cursor.connection.commit()


# 基于用户ID获取订单
# u_or_s 0:u  1:s
def get_order_by_id(db, id, u_or_s):
    cursor = db.cursor()
    if u_or_s == 0:
        cursor.execute("select * from dingdan where uid = ? ", (id,))
    else:
        cursor.execute("select * from dingdan where sid = ? ", (id,))
    rows = cursor.fetchall()
    return rows


# 基于用户名获取用户所有信息
def get_user_by_name(db, uname):
    c = db.cursor()
    c.execute("select * from user where uname = ? ", (uname,))
    Row = namedtuple('Row', [tup[0] for tup in c.description])
    return [Row(*row) for row in c.fetchall()]


# 检查用户是否存在 以及对密码进行验证
def check_user(db, uname, upw):
    user = get_user_by_name(db, uname)
    if len(user) == 0:
        return 1, '用户不存在'
    elif user[0].upw != upw:
        return 2, '密码错误'
    else:
        return 0, user[0].urole, user[0].id


# 根据用户id获取用户名
def get_user_by_id(db, user_id_to_retrieve):
    cursor = db.cursor()
    cursor.execute("select * from user where id = ? ", (user_id_to_retrieve,))
    _user = cursor.fetchone()
    if _user:
        return _user[1]
    return None


# 根据菜品id获取菜名
def get_dish_name_by_id(db, dish_id):
    cursor = db.cursor()
    cursor.execute("select * from caiping where id = ? ", (dish_id,))
    _dish = cursor.fetchone()
    if _dish:
        return _dish[1]
    return None


# 获取菜品
def get_cp(db, id):
    c = db.cursor()
    c.execute("select * from caiping where id = ? ", (id,))
    Row = namedtuple('Row', [tup[0] for tup in c.description])
    return [Row(*row) for row in c.fetchall()]


# 更新订单状态
def update_order_status(db, order_id, status=1):
    cursor = db.cursor()
    cursor.execute("update dingdan set status = ? where id = ?", (status, order_id,))
    cursor.connection.commit()


if __name__ == '__main__':
    init_db = open_database()
    get_all_menu(init_db)
