from dataclasses import dataclass

from amv2.enums import ClassFlag, ConstantKind, MethodFlag, MultinameKind, NamespaceKind, TraitAttribut, TraitType


class String(str):
    @classmethod
    def unpack(cls, stream):
        size = stream.read_var_uint30()
        value = ''.join([stream.read_char() for _ in range(size)])

        return cls(value)


@dataclass
class Namespace:
    kind: NamespaceKind
    name_idx: int

    @classmethod
    def unpack(cls, stream):
        kind = NamespaceKind(stream.read_uint8())
        idx = stream.read_var_uint30()

        return cls(
            kind=kind,
            name_idx=idx,
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
    __multinames__ = {}
    i = 0
    @staticmethod
    def unpack(stream):
        kind = MultinameKind(stream.read_uint8())
        return Multiname.__multinames__[kind].unpack(stream)

    @staticmethod
    def register(kind):
        def decorator(cls):
            Multiname.__multinames__[kind] = cls

            cls.__kind__ = kind
            return cls
        return decorator


@dataclass
@Multiname.register(MultinameKind.Q_NAME)
class QName:
    namespace_idx: int
    name_idx: int

    @classmethod
    def unpack(cls, stream):
        namespace_idx = stream.read_var_uint30()
        name_idx = stream.read_var_uint30()

        return cls(
            namespace_idx=namespace_idx,
            name_idx=name_idx,
        )


@Multiname.register(MultinameKind.Q_NAME_A)
class QNameA(QName):
    pass


@dataclass
@Multiname.register(MultinameKind.RT_Q_NAME)
class RTQName:
    name_idx: int

    @classmethod
    def unpack(cls, stream):
        name_idx = stream.read_var_uint30()

        return cls(
            name_idx=name_idx,
        )


@Multiname.register(MultinameKind.RT_Q_NAME_A)
class RTQNameA(RTQName):
    pass


@Multiname.register(MultinameKind.RT_Q_NAME_L)
class RTQNameL:
    @classmethod
    def unpack(cls, _stream):
        pass


@Multiname.register(MultinameKind.RT_Q_NAME_L_A)
class RTQNameLA(RTQNameL):
    pass


@dataclass
@Multiname.register(MultinameKind.MULTINAME)
class Multiname_:
    name_idx: int
    namespace_idx: int

    @classmethod
    def unpack(cls, stream):
        name_idx = stream.read_var_uint30()
        namespace_idx = stream.read_var_uint30()

        return cls(
            name_idx=name_idx,
            namespace_idx=namespace_idx,
        )


@Multiname.register(MultinameKind.MULTINAME_A)
class MultinameA(Multiname_):
    pass


@dataclass
@Multiname.register(MultinameKind.MULTINAME_L)
class MultinameL:
    namespace_idx: int

    @classmethod
    def unpack(cls, stream):
        namespace_idx = stream.read_var_uint30()

        return cls(
            namespace_idx=namespace_idx,
        )


@Multiname.register(MultinameKind.MULTINAME_L_A)
class MultinameLA(MultinameL):
    pass


# https://blog.richardszalay.com/2009/02/10/generics-vector-in-the-avm2/
@dataclass
@Multiname.register(MultinameKind.GENERIC_NAME)
class GenericName:
    name_idx: int
    params: list[int]

    @classmethod
    def unpack(cls, stream):
        name_idx = stream.read_var_uint30()

        count = stream.read_var_uint30()
        params = [stream.read_var_uint30() for _ in range(count)]

        return cls(
            name_idx=name_idx,
            params=params,
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
class Option:
    value_idx: int
    kind: ConstantKind

    @classmethod
    def unpack(cls, stream):
        value_idx = stream.read_var_uint30()
        kind = ConstantKind(stream.read_uint8())

        return cls(
            value_idx=value_idx,
            kind=kind,
        )


@dataclass
class Method:
    name_idx: int
    param_names: list[int]
    param_types: list[int]
    options: list[Option]
    flags: list[MethodFlag]
    return_type: int

    @classmethod
    def unpack(cls, stream):
        param_count = stream.read_var_uint30()
        # TODO: add enum for types
        return_type = stream.read_var_uint30()
        param_types = [stream.read_var_uint30() for _ in range(param_count)]
        name_idx = stream.read_var_uint30()
        bits_flags = stream.read_uint8()

        flags = []
        for flag in MethodFlag:
            if flag.value & bits_flags != flag.value:
                continue
            flags.append(flag)

        options = []
        if MethodFlag.HAS_OPTIONAL in flags:
            option_count = stream.read_var_uint30()
            options = [Option.unpack(stream) for _ in range(option_count)]

        param_names = []
        if MethodFlag.HAS_PARAM_NAMES in flags:
            param_names = [stream.read_var_uint30() for _ in range(param_count)]
    
        return cls(
            name_idx=name_idx,
            param_names=param_names,
            param_types=param_types,
            options=options,
            flags=flags,
            return_type=return_type,
        )


@dataclass
class Item:
    key: int
    value: int

    @classmethod
    def unpack(cls, stream):
        key = stream.read_var_uint30()
        value = stream.read_var_uint30()

        return cls(
            key=key,
            value=value,
        )


@dataclass
class Metadata:
    name_idx: int
    items: list[Item]

    @classmethod
    def unpack(cls, stream):
        idx = stream.read_var_uint30()

        count = stream.read_var_uint30()
        items = [Item.unpack(stream) for _ in range(count)]

        return cls(
            name_idx=idx,
            items=items,
        )


@dataclass
class Trait:
    __traits__ = {}

    name_idx: int
    metadata: list[int]
    attributes: list[TraitAttribut]


    @staticmethod
    def unpack(stream):
        idx = stream.read_var_uint30()

        kind = stream.read_uint8()
        type = TraitType(kind & 0b1111)
        bits_attributes = kind >> 4

        instance = Trait.__traits__[type].unpack(stream)
        instance.name_idx = idx

        for attribut in TraitAttribut:
            if attribut.value & bits_attributes != attribut.value:
                continue
            instance.attributes.append(attribut)
        
        if TraitAttribut.METADATA in instance.attributes:
            count = stream.read_var_uint30()
            instance.metadata = [stream.read_var_uint30() for _ in range(count)]

        return instance

    def register(kind):
        def decorator(cls):
            kinds = kind if isinstance(kind, list) else [kind]
            for _kind in kinds:
                Trait.__traits__[_kind] = cls

            cls.__kind__ = kind
            return cls
        return decorator


@dataclass
@Trait.register([
    TraitType.SLOT,
    TraitType.CONST,
])
class SlotTrait(Trait):
    slot_id: int
    type_name_idx: int
    v_idx: int
    v_kind: ConstantKind

    @classmethod
    def unpack(cls, stream):
        id = stream.read_var_uint30()
        type_name_idx = stream.read_var_uint30()
        v_idx = stream.read_var_uint30()
        v_kind = ConstantKind(stream.read_uint8()) if v_idx != 0 else None

        return cls(
            name_idx=None,
            metadata=[],
            attributes=[],
            slot_id=id,
            type_name_idx=type_name_idx,
            v_idx=v_idx,
            v_kind=v_kind,
        )


@dataclass
@Trait.register(TraitType.CLASS)
class ClassTrait(Trait):
    slot_id: int
    class_idx: int

    @classmethod
    def unpack(cls, stream):
        id = stream.read_var_uint30()
        idx = stream.read_var_uint30()

        return cls(
            name_idx=None,
            metadata=[],
            attributes=[],
            slot_id=id,
            class_idx=idx,
        )


@dataclass
@Trait.register(TraitType.FUNCTION)
class FunctionTrait(Trait):
    slot_id: int
    function_idx: int

    @classmethod
    def unpack(cls, stream):
        id = stream.read_var_uint30()
        idx = stream.read_var_uint30()

        return cls(
            name_id=None,
            metadata=[],
            attributes=[],
            slot_id=id,
            function_idx=idx,
        )


@dataclass
@Trait.register([
    TraitType.METHOD,
    TraitType.GETTER,
    TraitType.SETTER,
])
class MethodTrait(Trait):
    disp_id: int
    method_idx: int

    @classmethod
    def unpack(cls, stream):
        id = stream.read_var_uint30()
        idx = stream.read_var_uint30()

        return cls(
            name_idx=None,
            metadata=[],
            attributes=[],
            disp_id=id,
            method_idx=idx,
        )


@dataclass
class Instance:
    name_idx: int
    super_name_idx: int
    flags: list[ClassFlag]
    protected_ns: int
    interfaces: list[int]
    init_method_idx: int
    traits: list[Trait]

    @classmethod
    def unpack(cls, stream):
        name_idx = stream.read_var_uint30()
        super_name_idx = stream.read_var_uint30()

        bits_flags = stream.read_uint8()
        flags = []
        for flag in ClassFlag:
            if flag.value & bits_flags != flag.value:
                continue
            flags.append(flag)

        protected_ns = None
        if ClassFlag.PROTECTED_NS in flags:
            protected_ns = stream.read_var_uint30()

        count = stream.read_var_uint30()
        interfaces = [stream.read_var_uint30() for _ in range(count)]

        init_method_idx = stream.read_var_uint30()

        count = stream.read_var_uint30()
        traits = [Trait.unpack(stream) for _ in range(count)]

        return cls(
            name_idx=name_idx,
            super_name_idx=super_name_idx,
            flags=flags,
            protected_ns=protected_ns,
            interfaces=interfaces,
            init_method_idx=init_method_idx,
            traits=traits,
        )


@dataclass
class Class:
    init_method_idx: int
    traits: list[Trait]

    @classmethod
    def unpack(cls, stream):
        init_method_idx = stream.read_var_uint30()

        count = stream.read_var_uint30()
        traits = [Trait.unpack(stream) for _ in range(count)]

        return cls(
            init_method_idx=init_method_idx,
            traits=traits,
        )


@dataclass
class Script:
    init_method_idx: int
    traits: list[Trait]

    @classmethod
    def unpack(cls, stream):
        init_method_idx = stream.read_var_uint30()

        count = stream.read_var_uint30()
        traits = [Trait.unpack(stream) for _ in range(count)]

        return cls(
            init_method_idx=init_method_idx,
            traits=traits,
        )


@dataclass
class AESException:
    from_idx: int
    to_idx: int
    target_idx: int
    exc_type_idx: int
    var_name_idx: int

    @classmethod
    def unpack(cls, stream):
        from_idx = stream.read_var_uint30()
        to_idx = stream.read_var_uint30()
        target_idx = stream.read_var_uint30()
        exc_type_idx = stream.read_var_uint30()
        var_name_idx = stream.read_var_uint30()

        return cls(
            from_idx=from_idx,
            to_idx=to_idx,
            target_idx=target_idx,
            exc_type_idx=exc_type_idx,
            var_name_idx=var_name_idx,
        )


@dataclass
class MethodBody:
    method_idx: int
    max_stack: int
    local_count: int
    init_scope_depth: int
    max_scope_depth: int
    code: bytes
    exceptions: list[AESException]
    traits: list[Trait]

    @classmethod
    def unpack(cls, stream):
        method_idx = stream.read_var_uint30()
        max_stack = stream.read_var_uint30()
        local_count = stream.read_var_uint30()
        init_scope_depth = stream.read_var_uint30()
        max_scope_depth = stream.read_var_uint30()

        count = stream.read_var_uint30()
        code = stream.read_bytes(count, to_int=False)

        count = stream.read_var_uint30()
        exceptions = [AESException.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        traits = [Trait.unpack(stream) for _ in range(count)]

        return cls(
            method_idx=method_idx,
            max_stack=max_stack,
            local_count=local_count,
            init_scope_depth=init_scope_depth,
            max_scope_depth=max_scope_depth,
            code=code,
            exceptions=exceptions,
            traits=traits,
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
        instances = [Instance.unpack(stream) for _ in range(count)]
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


