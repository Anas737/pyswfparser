from enum import Enum


class NamespaceKind(Enum):
    NS = 0x08
    PACKAGE_NS = 0x16
    PACKAGE_INTERNAL_NS = 0x17
    PROTECTED_NS = 0x18
    EXPLICIT_NS = 0x19
    STATIC_PROTECTED_NS = 0x1a
    PRIVATE_NS = 0x05


class MultinameKind(Enum):
    Q_NAME = 0x07
    Q_NAME_A = 0x0d
    RT_Q_NAME = 0x0f
    RT_Q_NAME_A = 0x10
    RT_Q_NAME_L = 0x11
    RT_Q_NAME_L_A = 0x12
    MULTINAME = 0x09
    MULTINAME_A = 0x0e
    MULTINAME_L = 0x1b
    MULTINAME_L_A = 0x1c
    GENERIC_NAME = 0x1d


class MethodFlag(Enum):
    NEED_ARGUMENTS = 0x01
    NEED_ACTIVATION = 0x02
    NEED_REST = 0x04
    HAS_OPTIONAL = 0x08
    SET_DXNS = 0x40
    HAS_PARAM_NAMES = 0x80


class ConstantKind(Enum):
    SINT = 0x03
    UINT = 0x04
    DOUBLE = 0x06
    UTF8 = 0x01
    TRUE = 0x0b
    FALSE = 0x0a
    NULL = 0x0c
    UNDEFINED = 0x00
    NS = 0x08
    PACKAGE_NS = 0x16
    PACKAGE_INTERNAL_NS = 0x17
    PROTECTED_NS = 0x18
    EXPLICIT_NS = 0x19
    STATIC_PROTECTED_NS = 0x1a
    PRIVATE_NS = 0x05


class ClassFlag(Enum):
    SEALED = 0x01
    FINAL = 0x02
    INTERFACE = 0x04
    PROTECTED_NS = 0x08


class TraitType(Enum):
    SLOT = 0
    METHOD = 1
    GETTER = 2
    SETTER = 3
    CLASS = 4
    FUNCTION = 5
    CONST = 6


class TraitAttribut(Enum):
    FINAL = 1
    OVERRIDE = 2
    METADATA = 4
