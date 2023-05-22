from connection import get_connection
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple, Type, Union


__C = get_connection()


@dataclass
class Model:
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {getattr(self, 'id')}"

    def __post_init__(self) -> None:
        for f, t in self.__annotations__.items():
            if t == bool and isinstance(getattr(self, f), int):
                # If field is bool makes the convertion from int to bool
                setattr(self, f, bool(getattr(self, f)))

    def create(self):
        columns: Tuple[str, ...] = tuple(
            filter(
                lambda x: getattr(self, x) is not None,
                self.__annotations__.keys(),
            )
        )
        values: Tuple[str, ...] = tuple()
        for column in columns:
            value = getattr(self, column)
            if isinstance(value, bool):
                value = int(value)
            values += (str(value),)

        __C.cursor.execute(
            f"""
                INSERT INTO {self.__class__.__name__}
                {columns} VALUES ({', '.join('?' * len(values))})
            """,
            values,
        )
        __C.conn.commit()
        if self.id is None:
            self.id = __C.cursor.lastrowid
        return self

    @classmethod
    def filter(
        cls: Type["Model"],
        OP: str = "AND",
        **kwargs: Dict[str, Union[str, int, Iterable[Union[str, int]]]],
    ) -> Type["Model"]:

        keys: List[str] = list(cls.__annotations__.keys())
        where: str = "WHERE"
        values: Tuple[str, ...] = tuple()
        columns: Tuple[str, ...] = tuple()
        counter = 0

        for attr, value in kwargs.items():

            if attr not in keys:
                raise AttributeError(
                    f"{cls.__name__} does not have {attr} attribute!"
                )

            columns += (attr,)

            if counter > 0:
                where += OP

            if isinstance(value, bool):
                value = int(value)

            if isinstance(value, (list, tuple)):
                where += f" {attr} IN ({','.join('?' * len(value))}) "
                values += tuple(value)
            else:
                where += f" {attr} = ? "
                values += (str(value),)

            counter += 1

        cls.query = {
            "select": f"SELECT * FROM {cls.__name__} ",
            "where": where,
            "values": values,
            "columns": columns,
        }

        return cls

    @classmethod
    def _select(cls):
        return __C.cursor.execute(
            f"{cls.query['select']} {cls.query['where']};", cls.query["values"]
        )

    @classmethod
    def all(cls: Type["Model"]) -> Set["Model"]:
        if getattr(cls, "query", None) is not None:
            return set(cls(**dict(row)) for row in cls._select().fetchall())
        raise ValueError("Missing query!")

    @classmethod
    def first(cls: Type["Model"]) -> "Model":
        if getattr(cls, "query", None) is not None:
            return cls(**dict(cls._select().fetchone()))
        raise ValueError("Missing query!")

    @classmethod
    def update(
        cls: Type["Model"],
        OP: str = "AND",
        **kwargs: Dict[str, Union[str, int, bool]],
    ) -> int:

        if getattr(cls, "query", None) is None:
            raise ValueError("Missing query!")
        elif not kwargs:
            raise ValueError("No attribute passed to be updated!")

        keys: List[str] = list(cls.__annotations__.keys())
        update_str: str = f"UPDATE {cls.__name__} SET "
        values: Tuple[str, ...] = tuple()

        for attr, value in kwargs.items():

            if attr not in keys:
                raise AttributeError(
                    f"{cls.__name__} does not have {attr} attribute!"
                )

            if isinstance(value, bool):
                value = int(value)

            update_str += f" {attr} = ?,"

            values += (str(value),)

        if update_str.endswith(","):
            update_str = update_str.rstrip(",")

        update_str += f" {cls.query['where']}"

        values += tuple(cls.query["values"])

        __C.cursor.execute(update_str, values)
        __C.conn.commit()

        return __C.cursor.rowcount

    @classmethod
    def delete(cls: Type["Model"]):
        pass
