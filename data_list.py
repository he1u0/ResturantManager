from dataclasses import dataclass


def get_status(self):
    if self == 0:
        return "等待接单"
    elif self == 1:
        return "正在制作"
    elif self == 2:
        return "正在派送"
    elif self == 3:
        return "订单完成"
    else:
        return "未知状态"


@dataclass
class OrderList:
    order_id: int
    user_name: str
    business_name: str
    dish_name: str
    status: int
