from dataclasses import dataclass


@dataclass
class OrderList:
    order_id: int
    s_name: str
    c_name: str
    status: str
