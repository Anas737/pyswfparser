from enums import enum


class LangagueCode(enum):
    LATIN = 1
    JAPANESE = 2
    KOREAN = 3
    SIMPLIFIED_CHINESE = 4
    TRADITIONAL_CHINESE = 5


class ValueType(enum):
    STRING = 0
    FLOAT = 1
    NULL = 2
    UNDEFINED = 3
    REGISTER = 4
    BOOL = 5
    DOUBLE = 6
    INTEGER = 7
    CONSTANT_8 = 8
    CONSTANT_16 = 9


class VarsMethod(enum):
    NONE = 0
    GET = 1
    POST = 2


class BlendMode(enum):
    NORMAL_0 = 0
    NORMAL_1 = 1
    LAYER = 2
    MULTIPLY = 3
    SCREEN = 4
