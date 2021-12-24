from dataclasses import dataclass

from swf.records import Event


__ACTIONS__ = {}


def action(code):
    def modifier(cls):
        cls.code = code

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


class Action:
    @staticmethod
    def unpack(stream):
        header = Header.unpack(stream)
        if header.code not in __ACTIONS__:
            # unhandled action
            if header.length != 0:
                stream.move_bytes(header.length)

            return None

        cls = __ACTIONS__[header.code]
        return cls.unpack(stream)


