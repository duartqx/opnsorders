import sqlite3
from typing import Any, Callable, Union


class _SQLiteConnection:
    def __init__(self, db: str = "oohpns") -> None:
        self.db = db
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self) -> None:
        return self.conn.close()

    def commit(self) -> None:
        return self.conn.commit()

    @property
    def execute(self) -> Callable[..., sqlite3.Cursor]:
        return self.cursor.execute

    @property
    def lastrowid(self) -> Union[int, None]:
        return self.cursor.lastrowid

    @property
    def rowcount(self) -> int:
        return self.cursor.rowcount

    def initialize_db(self) -> None:
        # TODO: Remove from here and dynamically build the CREATE TABLE sql with
        # annotation on models fields types
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS OpnsOrder
                (
                    id INTEGER NOT NULL PRIMARY KEY,
                    date DATE NOT NULL,
                    total INTEGER NOT NULL,
                    paid BOOL NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS OrderItem
                (
                    id INTEGER NOT NULL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    details TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    persons_nb INTEGER NOT NULL DEFAULT 0,
                    kids_pets_nb INTEGER NOT NULL DEFAULT 0,
                    type INTEGER NOT NULL,
                    background INTEGER NOT NULL,
                    details TEXT,
                    done BOOL NOT NULL DEFAULT 0,
                    FOREIGN KEY (order_id) REFERENCES OpnsOrder(id)
                );
            """
        )


class __SQLiteConnectionManager:
    def __init__(self) -> None:
        self.__C: _SQLiteConnection = _SQLiteConnection()

    @property
    def C(self) -> _SQLiteConnection:
        return self.__C

    def __setattr__(self, __name: str, __value: Any) -> None:
        if hasattr(self, "_SQLiteConnectionManager__C"):
            raise AttributeError("Not allowed")
        return super().__setattr__(__name, __value)


__CONNECTION_MANAGER = __SQLiteConnectionManager()


def get_connection() -> _SQLiteConnection:
    return __CONNECTION_MANAGER.C
