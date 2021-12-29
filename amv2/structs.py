from dataclasses import dataclass

from amv2.enums import MultinameKind, NamespaceKind


class String(str):
    @classmethod
    def unpack(cls, stream):
        size = stream.read_var_uint30()
        value = ''.join([stream.read_char() for _ in range(size)])

        return cls(value)


@dataclass
class Namespace:
    kind: NamespaceKind
    string_idx: int

    @classmethod
    def unpack(cls, stream):
        kind = NamespaceKind(stream.read_uint8())
        idx = stream.read_var_uint30()

        return cls(
            kind=kind,
            string_idx=idx,
        )


@dataclass
class NSSet:
    namespace_idx: list[int]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_var_uint30()
        idx = [stream.read_var_uint30() for _ in range(count)]

        return cls(
            namespace_idx=idx,
        )


class Multiname:
    __multinames__ = []

    @classmethod
    def multinames(cls):
        if not cls.__multinames__:
            cls.__multinames__ = {
                multiname.__kind__: multiname
                for multiname in cls.__subclasses__()
            }

        return cls.__multinames__

    @classmethod
    def unpack(cls, stream):
        kind = MultinameKind(stream.read_uint8())
        return cls.multinames()[kind].unpack(stream)


@dataclass
class QName(Multiname):
    __kind__ = MultinameKind.q_name

    namespace_idx: int
    string_idx: int

    @classmethod
    def unpack(cls, stream):
        namespace_idx = stream.read_var_uint30()
        string_idx = stream.read_var_uint30()

        return cls(
            namespace_idx=namespace_idx,
            string_idx=string_idx,
        )


@dataclass
class RTQName(Multiname):
    __kind__ = MultinameKind.rt_q_name

    string_idx: int

    @classmethod
    def unpack(cls, stream):
        string_idx = stream.read_var_uint30()

        return cls(
            string_idx=string_idx,
        )


@dataclass
class RTQNameL(Multiname):
    __kind__ = MultinameKind.rt_q_name_l
    @classmethod
    def unpack(cls, _stream):
        pass

@dataclass
class Multiname_(Multiname):
    __kind__ = MultinameKind.multiname

    string_idx: int
    ns_set_idx: int

    @classmethod
    def unpack(cls, stream):
        string_idx = stream.read_var_uint30()
        ns_set_idx = stream.read_var_uint30()

        return cls(
            string_idx=string_idx,
            ns_set_idx=ns_set_idx,
        )


@dataclass
class MultinameL(Multiname):
    __kind__ = MultinameKind.multiname_l

    ns_set_idx: int

    @classmethod
    def unpack(cls, stream):
        ns_set_idx = stream.read_var_uint30()

        return cls(
            ns_set_idx=ns_set_idx,
        )


@dataclass
class CPool:
    sintegers: list[int]
    uintegers: list[int]
    doubles: list[float]
    strings: list[String]
    namespaces: list[Namespace]
    ns_sets: list[NSSet]
    multinames: list[Multiname]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_var_uint30() - 1
        sintegers = [stream.read_var_sint32() for _ in range(count)]

        count = stream.read_var_uint30() - 1
        uintegers = [stream.read_var_uint32() for _ in range(count)]

        count = stream.read_var_uint30() - 1
        doubles = [stream.read_double() for _ in range(count)]
    
        count = stream.read_var_uint30() - 1
        strings = [String.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30() - 1
        namespaces = [Namespace.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30() - 1
        ns_sets = [NSSet.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30() - 1
        multinames = [Multiname.unpack(stream) for _ in range(count)]

        return cls(
            sintegers=sintegers,
            uintegers=uintegers,
            doubles=doubles,
            strings=strings,
            namespaces=namespaces,
            ns_sets=ns_sets,
            multinames=multinames,
        )


@dataclass
class File:
    minor_version: int
    major_version: int
    constants_pool: CPool
    methods: list[Method]
    method_bodies: list[MethodBody]
    instances: list[Instance]
    classes: list[Class]
    metadata: list[Metadata]
    scripts: list[Script]

    @classmethod
    def unpack(cls, stream):
        minor_version = stream.read_uint16()
        major_version = stream.read_uint16()

        constants_pool = CPool.unpack(stream)

        count = stream.read_var_uint30()
        methods = [Method.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        metadata = [Metadata.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        instances = [Class.unpack(stream) for _ in range(count)]
        classes = [Class.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        scripts = [Script.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        method_bodies = [MethodBody.unpack(stream) for _ in range(count)]

        return cls(
            minor_version=minor_version,
            major_version=major_version,
            constants_pool=constants_pool,
            methods=methods,
            method_bodies=method_bodies,
            instances=instances,
            classes=classes,
            metadata=metadata,
            scripts=scripts,
        )


