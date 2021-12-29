from dataclasses import dataclass

@dataclass
class CPool:
    sinteger: list[int]
    uinteger: list[int]
    double: list[float]
    string: list[String]
    namespace: list[Namespace]
    ns_set: list[NSSet]
    multiname: list[Multiname]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_var_uint30()
        sinteger = [stream.read_var_sint32() for _ in range(count)]

        count = stream.read_var_uint30()
        uinteger = [stream.read_var_uint32() for _ in range(count)]

        count = stream.read_var_uint30()
        double = [stream.read_double() for _ in range(count)]

        count = stream.read_var_uint30()
        string = [String.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        namespace = [Namespace.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        ns_set = [NSSet.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        multiname = [Multiname.unpack(stream) for _ in range(count)]

        return cls(
            sinteger=sinteger,
            uinteger=uinteger,
            double=double,
            string=string,
            namespace=namespace,
            ns_set=ns_set,
            multiname=multiname,
        )


@dataclass
class File:
    minor_version: int
    major_version: int
    constant_pool: CPool
    method: list[Method]
    method_body: list[MethodBody]
    instance: list[Instance]
    cls: list[Class]
    metadata: list[Metadata]
    script: list[Script]

    @classmethod
    def unpack(cls, stream):
        minor_version = stream.read_uint16()
        major_version = stream.read_uint16()

        constant_pool = CPool.unpack(stream)

        count = stream.read_var_uint30()
        method = [Method.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        metadata = [Metadata.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        instance = [Class.unpack(stream) for _ in range(count)]
        _cls = [Class.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        script = [Script.unpack(stream) for _ in range(count)]

        count = stream.read_var_uint30()
        method_body = [MethodBody.unpack(stream) for _ in range(count)]

        return cls(
            minor_version=minor_version,
            major_version=major_version,
            constant_pool=constant_pool,
            method=method,
            method_body=method_body,
            instance=instance,
            cls=_cls,
            metadata=metadata,
            script=script,
        )


