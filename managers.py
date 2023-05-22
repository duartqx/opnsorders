from connection import get_connection
from dataclasses import dataclass
from typing import Dict, Iterable, Set, List, Union, Type, Tuple


__C = get_connection()


@dataclass
class Model:
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {getattr(self, '_id')}"

    def __post_init__(self) -> None:
        for f, t in self.__annotations__.items():
            if t == bool and isinstance(getattr(self, f), int):
                # If field is bool makes the convertion from int to bool
                setattr(self, f, bool(getattr(self, f)))

    def create(self):
        columns: Tuple[str] = tuple(
            filter(
                lambda x: getattr(self, x) is not None,
                self.__annotations__.keys(),
            )
        )
        values: Tuple[str] = tuple()
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
        self._id = __C.cursor.lastrowid
        return self

    @classmethod
    def get(
        cls: Type["Model"],
        OP: str = "AND",
        **kwargs: Dict[str, Union[str, int, Iterable[Union[str, int]]]],
    ) -> Type["Model"]:
        keys: List[str] = list(cls.__annotations__.keys())

        query: str = f"SELECT * FROM {cls.__name__} WHERE"
        values: Tuple[str, ...] = tuple()
        counter = 0

        for attr, value in kwargs.items():
            if attr not in keys:
                raise AttributeError(
                    f"{cls.__name__} does not have {attr} attribute!"
                )

            if counter > 0:
                query += OP

            if isinstance(value, bool):
                value = int(value)

            if isinstance(value, (list, tuple)):
                query += f" {attr} IN ({','.join('?' * len(value))}) "
                values += tuple(value)
            else:
                query += f" {attr} = ? "
                values += (str(value),)

            counter += 1

        query += ";"
        cls.query = __C.cursor.execute(query, values)
        return cls

    @classmethod
    def all(cls: Type["Model"]) -> Set["Model"]:
        if getattr(cls, "query", None) is not None:
            return set(
                cls(**dict(row))
                for row in cls.query.fetchall()
            )
        raise ValueError("Missing query!")

    @classmethod
    def first(cls: Type["Model"]) -> "Model":
        if getattr(cls, "query", None) is not None:
            return cls(**dict(cls.query.fetchone()))
        raise ValueError("Missing query!")

    @classmethod
    def update(cls: Type["Model"]):
        pass

    @classmethod
    def delete(cls: Type["Model"]):
        pass
