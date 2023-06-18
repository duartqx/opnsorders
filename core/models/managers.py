from .connection import get_connection
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set, Tuple, Type, Union


__C = get_connection()


class IdIsNotNoneError(ValueError):
    pass


class NotFoundError(ValueError):
    pass


@dataclass
class Model:

    id: Union[int, None] = field(init=False, default=None)

    def __str__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}: {getattr(self, 'id')}"

    def __post_init__(self) -> None:
        """
        Post init tasks:
            1 - Replaces the delete method of the class to the appropriate
                method for instances
            2 - Converts field values to their appropriate data types, in
                particular integers to boolean
        """

        # Sets the delete method after instantiating
        self.delete = self.__instance__delete

        for field, field_type in self.__annotations__.items():
            if field_type == bool and isinstance(getattr(self, field), int):
                # If field is bool makes the convertion from int to bool
                setattr(self, field, bool(getattr(self, field)))

    @classmethod
    def _select(cls):
        """Executes SQLite SELECT and returns the cursor"""

        # Checks if there's sql where (if not, it means the filter method was
        # not executed)
        cls_sql_where: str = getattr(cls, f"_{cls.__name__}__sql_where", "")

        if cls_sql_where:
            return __C.execute(
                f"SELECT * FROM {cls.__name__} WHERE {cls_sql_where};",
                cls.__sql_values,
            )

        return __C.execute(f"SELECT * FROM {cls.__name__};")

    @classmethod
    def __instantitate_row(
        cls, dict_row: Dict[str, Union[str, int]]
    ) -> "Model":
        """Instantiate cls using the contents of a SQLite3 dict converted row"""

        # Grabs the id
        _id: int = dict_row.pop("id")  # type: ignore

        # Instantiate with all the other values but not id
        cls_instance = cls(**dict_row)

        # Sets the id with the private method
        cls_instance.id = _id

        return cls_instance

    def create(self):
        """Saves the current instance to the database, if the id is not set"""

        if self.id is not None:
            raise IdIsNotNoneError("Id must be None!")

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
        """Builds the SQLite WHERE SQL string using the keys and values of kwargs"""

        columns: List[str] = list(cls.__annotations__.keys())

        cls.__sql_where: str = ""
        cls.__sql_values: Tuple[str, ...] = tuple()

        counter = 0

        for column, value in kwargs.items():

            if column not in columns:
                raise AttributeError(
                    f"{cls.__name__} does not have {column} attribute!"
                )

            if counter > 0:
                cls.__sql_where += OP

            if isinstance(value, bool):
                value = int(value)

            if isinstance(value, (list, tuple)):
                cls.__sql_where += (
                    f" {column} IN ({','.join('?' * len(value))}) "
                )
                cls.__sql_values += tuple(value)
            else:
                cls.__sql_where += f" {column} = ? "
                cls.__sql_values += (str(value),)

            counter += 1

        return cls

    @classmethod
    def all(cls: Type["Model"]) -> Set["Model"]:
        """
        Executes a SELECT query to the database and returns a set of
        instantiated cls with the results of fetchall
        """

        dict_rows: List[Dict[str, Union[str, int]]] = [
            dict(row)
            for row in cls._select().fetchall()
        ]

        if not dict_rows:
            return set()

        return set(
            cls.__instantitate_row(dict_row)
            for dict_row in dict_rows
        )

    @classmethod
    def first(cls: Type["Model"]) -> Union["Model", None]:
        """Executes a SELECT query and returns a instance of cls or None if the
        query returned nothing"""
        row_dict: Dict[str, Union[str, int]] = dict(cls._select().fetchone())
        if not row_dict:
            return None
        return cls.__instantitate_row(row_dict)

    @classmethod
    def get(
        cls: Type["Model"],
        **kwargs: Dict[str, Union[str, int, bool]],
    ):
        """Executes a SELECT and returns a instance of cls or None"""
        for v in kwargs.values():
            if not isinstance(v, (str, int, bool)):
                raise ValueError(f"Value not allowed for get method: {v}")
        return cls.filter(**kwargs).first()

    @classmethod
    def update(
        cls: Type["Model"],
        **kwargs: Dict[str, Union[str, int, bool]],
    ) -> int:
        """
        Executes a UPDATE query and returns the count of rows that where updated.
        It is required to first execute the filter method before update
        """

        cls_sql_where: str = getattr(cls, f"_{cls.__name__}__sql_where", "")
        if not cls_sql_where:
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

        values += tuple(cls.__sql_values)

        __C.execute(
            f"UPDATE {cls.__name__} SET {update_str} WHERE {cls.__sql_where};",
            values,
        )
        __C.commit()

        return __C.rowcount

    @classmethod
    def delete(cls: Type["Model"]) -> int:
        """
        Executes a DELETE query with the contents of filter.
        It is required to first execute the filter method
        """

        cls_sql_where: str = getattr(cls, f"_{cls.__name__}__sql_where", "")
        if not cls_sql_where:
            raise ValueError("Missing query!")

        __C.execute(f"DELETE FROM {cls.__name__} WHERE {cls.__sql_where};")
        __C.commit()

        return __C.rowcount

    def __instance__delete(self: "Model") -> int:
        """
        Executes a DELETE query and deletes the current instance from the
        database
        """

        if self.id is None:
            raise ValueError("Cannot delete unsaved instances!")
        elif self.__class__.get(**{"id": self.id}) is None:
            raise NotFoundError("Can't delete non existing instance!")

        __C.execute(
            f"DELETE FROM {self.__class__.__name__} WHERE id = {self.id};"
        )
        __C.commit()

        return __C.rowcount