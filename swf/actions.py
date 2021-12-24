from dataclasses import dataclass
from typing import Any
from swf.enums import ValueType

from swf.records import Event


__ACTIONS__ = {}


def action(code, length=0):
    def modifier(cls):
        cls.__code__ = code
        cls.__length__ = length

        return cls

    return modifier



@dataclass
class Header:
    code: int
    length: int

    @classmethod
    def unpack(cls, stream):
        code = stream.read_uint8()
        length = 0
        if code >= 0x80:
            length = stream.read_uint16()

        return cls(
            code=code,
            length=length,
        )


@dataclass
class Action:
    header: Header

    @classmethod
    def unpack(cls, header, _stream):
        return cls(
            header=header,
        )


def unpack(stream):
    header = Header.unpack(stream)
    if header.code not in __ACTIONS__:
        # unhandled action
        if header.length != 0:
            stream.move_bytes(header.length)

        return None

    cls = __ACTIONS__[header.code]
    return cls.unpack(header, stream)


@dataclass
@action(code=0x81, length=2)
class GotoFrame(Action):
    frame: int

    @classmethod
    def unpack(cls, header, stream):
        frame = stream.read_uint16()

        return cls(
            header=header,
            frame=frame,
        )


@dataclass
@action(code=0x83)
class GetURL(Action):
    url: str
    target: str

    @classmethod
    def unpack(cls, header, stream):
        url = stream.read_string()
        target = stream.read_string()

        return cls(
            header=header,
            url=url,
            target=target,
        )


@dataclass
@action(code=0x04)
class NextFrame(Action):
    pass


@dataclass
@action(code=0x05)
class PreviousFrame(Action):
    pass


@dataclass
@action(code=0x06)
class Play(Action):
    pass


@dataclass
@action(code=0x07)
class Stop(Action):
    pass


@dataclass
@action(code=0x08)
class ToggleQuality(Action):
    pass


@dataclass
@action(code=0x09)
class StopSounds(Action):
    pass


@dataclass
@action(code=0x8a, length=3)
class WaitForFrame(Action):
    frame: int
    skip_count: int

    @classmethod
    def unpack(cls, header, stream):
        frame = stream.read_uint16()
        skip_count = stream.read_uint8()

        return cls(
            header=header,
            frame=frame,
            skip_count=skip_count,
        )


@dataclass
@action(code=0x8b)
class SetTarget(Action):
    name: str

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_string()

        return cls(
            header=header,
            name=name,
        )


@dataclass
@action(code=0x8c)
class GoToLabel(Action):
    label: str

    @classmethod
    def unpack(cls, header, stream):
        label = stream.read_string()

        return cls(
            header=header,
            label=label,
        )


@dataclass
@action(code=0x96)
class Push(Action):
    values: list[tuple[ValueType, Any]]

    @classmethod
    def unpack(cls, header, stream):
        values = []

        # XXX: to make sure we get the right position
        # maybe we read some bits before ?
        stream.byte_align()
        position = stream.byte_position
        while stream.byte_position < position + header.length:
            type = ValueType(stream.read_uint8())
            value = {
                ValueType.STRING: stream.read_string,
                ValueType.FLOAT: stream.read_float,
                ValueType.REGISTER: stream.read_uint8,
                ValueType.BOOL: stream.read_bool,
                ValueType.DOUBLE: stream.read_double,
                ValueType.INTEGER: stream.read_uint32,
                ValueType.CONSTANT_8: stream.read_uint8,
                ValueType.CONSTANT_16: stream.read_uint16,
            }.get(type, lambda: None)()

            values.append((type, value))

        return cls(
            values=values,
        )


@dataclass
@action(code=0x17)
class Pop(Action):
    pass


@dataclass
@action(code=0x0a)
class Add(Action):
    pass


@dataclass
@action(code=0x0b)
class Substract(Action):
    pass


@dataclass
@action(code=0x0c)
class Multiply(Action):
    pass


@dataclass
@action(code=0x0d)
class Divide(Action):
    pass


@dataclass
@action(code=0x0e)
class Equals(Action):
    pass


@dataclass
@action(code=0x0f)
class Less(Action):
    pass


@dataclass
@action(code=0x10)
class And(Action):
    pass


@dataclass
@action(code=0x11)
class Or(Action):
    pass


@dataclass
@action(code=0x12)
class Not(Action):
    pass


@dataclass
@action(code=0x13)
class StringEquals(Action):
    pass


@dataclass
@action(code=0x14)
class StringLength(Action):
    pass


@dataclass
@action(code=0x21)
class StringAdd(Action):
    pass


@dataclass
@action(code=0x15)
class StringExtract(Action):
    pass


@dataclass
@action(code=0x29)
class StringLess(Action):
    pass

