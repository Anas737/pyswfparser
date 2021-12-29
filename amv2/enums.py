from enum import Enum


class NamespaceKind(Enum):
    ns = 0x08
    package_ns = 0x16
    package_internal_ns = 0x17
    protected_ns = 0x18
    explicit_ns = 0x19
    static_protected_ns = 0x1a
    private_ns = 0x05


class MultinameKind(Enum):
    q_name = 0x07
    q_name_a = 0x0d
    rt_q_name = 0x0f
    rt_q_name_a = 0x10
    rt_q_name_l = 0x11
    rt_q_name_l_a = 0x11
    multiname = 0x09
    multiname_a = 0x0e
    multiname_l = 0x1b
    multiname_l_a = 0x1c
