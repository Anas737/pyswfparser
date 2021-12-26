from enum import Enum


class LangagueCode(Enum):
    LATIN = 1
    JAPANESE = 2
    KOREAN = 3
    SIMPLIFIED_CHINESE = 4
    TRADITIONAL_CHINESE = 5


class ValueType(Enum):
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


class VarsMethod(Enum):
    NONE = 0
    GET = 1
    POST = 2


class BlendMode(Enum):
    NORMAL_0 = 0
    NORMAL_1 = 1
    LAYER = 2
    MULTIPLY = 3
    SCREEN = 4


class FillStyleType(Enum):
    SOLID = 0x00
    LINEAR_GRADIENT = 0x10
    RADIAL_GRADIENT = 0x12
    FOCAL_RADIAL_GRADIENT = 0x13
    REPEATING_BITMAP = 0x40
    CLIPPED_BITMAP = 0x41
    NON_SMOOTHED_REPEATING_BITMAP = 0x42
    NON_SMOOTHED_CLIPPED_BITMAP = 0x43


class CapStyleType(Enum):
    ROUND = 0
    NONE = 1
    MITER = 2


class JoinStyleType:
    ROUND = 0
    BEVEL = 1
    MITER = 2
