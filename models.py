from dataclasses import dataclass
from datetime import date as Date
from enums import Background, BodyType
from functools import cached_property
from managers import Model
from typing import Set


@dataclass
class Order(Model):
    _id: int
    date: Date
    total: int
    paid: bool

    @cached_property
    def order_item_set(self) -> Set["Model"]:
        return OrderItem.filter(**{"order_id": int(self._id)})


@dataclass
class OrderItem(Model):
    _id: int
    order_id: int
    price: int
    persons_nb: int
    kids_pets_nb: int
    type: BodyType
    background: Background
    details: str
    done: bool

    @cached_property
    def order(self) -> "Model":
        return Order.get(**{"_id": self.order_id})
