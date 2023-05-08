import sqlite3
from dataclasses import dataclass
from datetime import date as Date
from enums import Background, Type
from functools import cached_property
from typing import Any, Dict, List


class Connection:
    def __init__(self, db: str = "oohpns") -> None:
        self.db = db
        self._conn = sqlite3.connect(self.db)
        self.cursor = self._conn.cursor()

    def close(self) -> None:
        self._conn.close()

    def initialize_db(self) -> None:
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS Order
                (
                    _id INTEGER NOT NULL PRIMARY KEY,
                    date DATE NOT NULL,
                    total INTEGER NOT NULL,
                );

                CREATE TABLE IF NOT EXISTS OrderItem
                (
                    _id INTEGER NOT NULL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    persons_nb INTEGER NOT NULL DEFAULT 0,
                    kids_pets_nb INTEGER NOT NULL DEFAULT 0,
                    type INTEGER NOT NULL,
                    background INTEGER NOT NULL,
                    details TEXT,
                    FOREIGN KEY (order_id) REFERENCES Order(_id),
                );
            """
        )
        pass


C = Connection()


@dataclass
class Order:
    _id: int
    date: Date
    total: int

    # @classmethod
    # def get(cls, **kwargs: Dict[str, Any]) -> List[cls]:
    #    pass

    # def get_order_item_set(self) -> List[OrderItem]:
    #    return Order.get_set(order_id=self._id)


@dataclass
class OrderItem:
    _id: int
    order_id: int
    price: int
    persons_nb: int
    kids_pets_nb: int
    type: Type
    background: Background
    details: str

    # @cached_property
    # def order(self) -> Order:
    #    return Order.get(_id=self.order_id)

    # @classmethod
    # def get(cls, **kwargs: Dict[str, Any]) -> List[cls]:
    #    return
