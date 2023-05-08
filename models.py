from dataclasses import dataclass
from datetime import date as Date
from enums import Background, BodyType
from managers import Model


@dataclass
class Order(Model):
    _id: int
    date: Date
    total: int
    paid: bool

    # @cached_property
    # def order_item_set(self) -> Set[OrderItem]:
    #     return getattr(self, "__order_item_set", None)


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

    # @cached_property
    # def order(self) -> Order:
    #    return Order.get(_id=self.order_id)

    # @classmethod
    # def get(cls, **kwargs: Dict[str, Any]) -> List[cls]:
    #    return
