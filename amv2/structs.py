from dataclasses import dataclass



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


