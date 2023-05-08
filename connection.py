import sqlite3


class __Connection:
    def __init__(self, db: str = "oohpns") -> None:
        self.db = db
        self._conn = sqlite3.connect(self.db)
        self._conn.row_factory = sqlite3.Row
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
                    paid BOOL NOT NULL DEFAULT 0
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
                    done BOOL NOT NULL DEFAULT 0,
                    FOREIGN KEY (order_id) REFERENCES Order(_id)
                );
            """
        )


class __ConnectionManager:
    def __init__(self) -> None:
        self.__C = __Connection()

    @property
    def C(self) -> __Connection:
        return self.__C

    def __setattr__(self, __name: str, __value: Any) -> None:  # type: ignore
        raise AttributeError("Not allowed")


__CONNECTION_MANAGER = __ConnectionManager()


def get_connection() -> __Connection:
    return __CONNECTION_MANAGER.C
