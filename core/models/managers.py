from .connection import get_connection
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set, Tuple, Type, Union


__C = get_connection()


@dataclass
class Model:

    id: Union[int, None] = field(init=False, default=None)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {getattr(self, 'id')}"

    def __post_init__(self) -> None:

        # Sets the delete method after instantiating
        self.delete = self.__instance__delete

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

        __C.execute(
            f"""
                INSERT INTO {self.__class__.__name__}
                {columns} VALUES ({', '.join('?' * len(values))})
            """,
            values,
        )
        __C.commit()
        if self.id is None:
            self.id = __C.lastrowid
        return self

    @classmethod
    def filter(
        cls: Type["Model"],
        OP: str = "AND",
        **kwargs: Dict[str, Union[str, int, Iterable[Union[str, int]]]],
    ) -> Type["Model"]:

        keys: List[str] = list(cls.__annotations__.keys())
        where: str = ""
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
            "where": where,
            "values": values,
            "columns": columns,
        }

        return cls

    @classmethod
    def _select(cls):
        return __C.execute(
            f"SELECT * FROM {cls.__name__} WHERE {cls.query['where']};",
            cls.query["values"],
        )

    @classmethod
    def __instantitate_row(
        cls, dict_row: Dict[str, Union[str, int]]
    ) -> "Model":

        # Grabs the id
        _id: int = dict_row.pop("id")  # type: ignore

        # Instantiate with all the other values but not id
        instance = cls(**dict_row)

        # Sets the id with the private method
        instance.id = _id

        return instance

    @classmethod
    def all(cls: Type["Model"]) -> Set["Model"]:
        if getattr(cls, "query", None) is not None:
            return set(
                cls.__instantitate_row(dict(row))
                for row in cls._select().fetchall()
            )
        raise ValueError("Missing query!")

    @classmethod
    def first(cls: Type["Model"]) -> "Model":
        if getattr(cls, "query", None) is not None:
            return cls.__instantitate_row(dict(cls._select().fetchone()))
        raise ValueError("Missing query!")

    @classmethod
    def update(
        cls: Type["Model"],
        **kwargs: Dict[str, Union[str, int, bool]],
    ) -> int:

        if getattr(cls, "query", None) is None:
            raise ValueError("Missing query!")
        elif not kwargs:
            raise ValueError("No attribute passed to be updated!")

        keys: List[str] = list(cls.__annotations__.keys())
        update_str: str = ""
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

        values += tuple(cls.query["values"])

        __C.execute(
            f"UPDATE {cls.__name__} SET {update_str} WHERE {cls.query['where']};",
            values,
        )
        __C.commit()

        return __C.rowcount

    @classmethod
    def get(
        cls: Type["Model"],
        **kwargs: Dict[str, Union[str, int, bool]],
    ):
        for v in kwargs.values():
            if not isinstance(v, (str, int, bool)):
                raise ValueError("Get method can't return more than one")
        return cls.filter(**kwargs).first()

    @classmethod
    def delete(cls: Type["Model"]):
        if getattr(cls, "query", None) is None:
            raise ValueError("Missing query!")
        __C.execute(f"DELETE FROM {cls.__name__} WHERE {cls.query['where']};")
        __C.commit()

    def __instance__delete(self: "Model"):
        if self.id is None:
            raise ValueError("Cannot delete unsaved instances!")
        __C.execute(
            f"DELETE FROM {self.__class__.__name__} WHERE id = {self.id};"
        )
        __C.commit()
