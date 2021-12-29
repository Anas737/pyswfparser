from enum import Enum


class NamespaceKind(Enum):
    ns = 0x08
    package_ns = 0x16
    package_internal_ns = 0x17
    protected_ns = 0x18
    explicit_ns = 0x19
    static_protected_ns = 0x1a
    private_ns = 0x05
