from typing import Dict, Iterable, Set, List, Union, Type
from connection import get_connection


__C = get_connection()


class Model:
    __objects = None

    @classmethod
    @property
    def objects(cls):
        if cls.__objects is None:
            cls.__objects = Manager(cls)
        return cls.__objects


class Manager:
    def __init__(self, model: Type[Model]) -> None:
        self.model = model

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.model.__name__}"  # type: ignore

    def get(
        self,
        OP: str = "AND",
        **kwargs: Dict[str, Union[str, int, Iterable[Union[str, int]]]],
    ) -> Set[Model]:
        keys: List[str] = list(self.model.__annotations__.keys())
        counter = 0

        class_name: str = self.model.__name__  # type: ignore
        query: str = "SELECT * FROM %s WHERE"
        params: tuple[str] = (class_name,)  # type: ignore

        for attr, value in kwargs.items():
            if attr not in keys:
                raise AttributeError(
                    f"{class_name} does not have {attr} attribute!"  # type: ignore
                )

            if isinstance(value, (list, tuple)):
                eq_or_in = "IN"
            else:
                eq_or_in = "="

            query += f" %s {eq_or_in} %s"
            params += (attr, value)  # type: ignore

            if counter > 0:
                query += f" {OP}"

            counter += 1

        return set(
            self.model(**dict(row))  # type: ignore
            for row in __C.cursor.execute(query, params).fetchall()  # type: ignore
        )
