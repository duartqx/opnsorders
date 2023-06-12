from ..enums import BackgroundType, BodyType
from core.models.managers import Model

from dataclasses import dataclass
from datetime import date as Date
from functools import cached_property
from typing import Set


@dataclass
class Order(Model):
    date: Date
    total: int
    paid: bool

    @cached_property
    def order_item_set(self) -> Set["Model"]:
        if self.id is None:
            raise ValueError("Id is not set")
        return OrderItem.filter(**{"order_id": int(self.id)}).all()


@dataclass
class OrderItem(Model):
    order_id: int
    ref: str
    price: int
    persons_nb: int
    kids_pets_nb: int
    type: BodyType
    background: BackgroundType
    details: str
    done: bool

    @cached_property
    def order(self) -> "Model":
        return Order.filter(**{"id": int(self.order_id)}).first()
