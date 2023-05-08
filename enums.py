from enum import Enum
from functools import cached_property


class EnumDisplay(Enum):
    @cached_property
    def display(self) -> str:
        return self.name.replace("_", " ").capitalize()


class BodyType(EnumDisplay):
    FULL_BODY = 1
    HALF_BODY = 2


class Background(EnumDisplay):
    BEACH = 1
    CHURCH = 2
    COUCH = 3
    COUCH_HALLOWEEN = 4
    COUCH_NOEL = 5
    COUCH_VALENTINE = 6
    CUSTOM = 7
    EASTER_HOUSE = 8
    FACTORY = 9
    HALLOWER_HOUSE = 10
    HOUSE = 11
    SCHOOL = 12
    SKY = 13
    VALENTINE = 14
