from dataclasses import dataclass
from typing import Any

from swf.enums import ValueType, VarsMethod
from swf.records import Events


__ACTIONS__ = {}


def register_action(code):
    def modifier(cls):
        __ACTIONS__[code] = cls

        cls.__code__ = code
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
class Action:
    header: Header

    @classmethod
    def unpack(cls, header, _stream):
        return cls(
            header=header,
        )

#### SWF 3 Actions ####
@dataclass
@register_action(code=0x81)
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
@register_action(code=0x83)
class GetURL(Action):
    url: str
    target: str

    @classmethod
    def unpack(cls, header, stream):
        url = stream.read_cstring()
        target = stream.read_cstring()

        return cls(
            header=header,
            url=url,
            target=target,
        )


@dataclass
@register_action(code=0x04)
class NextFrame(Action):
    pass


@dataclass
@register_action(code=0x05)
class PreviousFrame(Action):
    pass


@dataclass
@register_action(code=0x06)
class Play(Action):
    pass


@dataclass
@register_action(code=0x07)
class Stop(Action):
    pass


@dataclass
@register_action(code=0x08)
class ToggleQuality(Action):
    pass


@dataclass
@register_action(code=0x09)
class StopSounds(Action):
    pass


@dataclass
@register_action(code=0x8a)
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
@register_action(code=0x8b)
class SetTarget(Action):
    name: str

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()

        return cls(
            header=header,
            name=name,
        )


@dataclass
@register_action(code=0x8c)
class GoToLabel(Action):
    label: str

    @classmethod
    def unpack(cls, header, stream):
        label = stream.read_cstring()

        return cls(
            header=header,
            label=label,
        )



#### SWF 4 Actions ####
@dataclass
@register_action(code=0x96)
class Push(Action):
    values: list[tuple[ValueType, Any]]

    @classmethod
    def unpack(cls, header, stream):
        values = []
        position = stream.byte_position
        while stream.byte_position < position + header.length:
            type = ValueType(stream.read_uint8())
            value = {
                ValueType.STRING: stream.read_cstring,
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
@register_action(code=0x17)
class Pop(Action):
    pass


@dataclass
@register_action(code=0x0a)
class Add(Action):
    pass


@dataclass
@register_action(code=0x0b)
class Substract(Action):
    pass


@dataclass
@register_action(code=0x0c)
class Multiply(Action):
    pass


@dataclass
@register_action(code=0x0d)
class Divide(Action):
    pass


@dataclass
@register_action(code=0x0e)
class Equals(Action):
    pass


@dataclass
@register_action(code=0x0f)
class Less(Action):
    pass


@dataclass
@register_action(code=0x10)
class And(Action):
    pass


@dataclass
@register_action(code=0x11)
class Or(Action):
    pass


@dataclass
@register_action(code=0x12)
class Not(Action):
    pass


@dataclass
@register_action(code=0x13)
class StringEquals(Action):
    pass


@dataclass
@register_action(code=0x14)
class StringLength(Action):
    pass


@dataclass
@register_action(code=0x21)
class StringAdd(Action):
    pass


@dataclass
@register_action(code=0x15)
class StringExtract(Action):
    pass


@dataclass
@register_action(code=0x29)
class StringLess(Action):
    pass


@dataclass
@register_action(code=0x31)
class MBStringLength(Action):
    pass


@dataclass
@register_action(code=0x35)
class MBStringExtract(Action):
    pass


@dataclass
@register_action(code=0x18)
class ToInteger(Action):
    pass


@dataclass
@register_action(code=0x32)
class CharToAscii(Action):
    pass


@dataclass
@register_action(code=0x33)
class AsciiToChart(Action):
    pass


@dataclass
@register_action(code=0x36)
class MBCharToAscii(Action):
    pass


@dataclass
@register_action(code=0x37)
class MBAsciiToChart(Action):
    pass


@dataclass
@register_action(code=0x99)
class Jump(Action):
    offset: int

    @classmethod
    def unpack(cls, header, stream):
        offset = stream.read_sint16()

        return cls(
            header=header,
            offset=offset,
        )


@dataclass
@register_action(code=0x9d)
class If(Action):
    offset: int

    @classmethod
    def unpack(cls, header, stream):
        offset = stream.read_sint16()

        return cls(
            header=header,
            offset=offset,
        )


@dataclass
@register_action(code=0x9e)
class Call(Action):
    pass


@dataclass
@register_action(code=0x1c)
class GetVariable(Action):
    pass


@dataclass
@register_action(code=0x1d)
class SetVariable(Action):
    pass


@dataclass
@register_action(code=0x9a)
class GetURL2(Action):
    send_vars_method: VarsMethod
    load_target: bool
    load_variables: bool

    @classmethod
    def unpack(cls, header, stream):
        send_vars_method = VarsMethod(stream.read_ubits(2))
        stream.read_ubits(4)  # reserved always 0
        load_target = stream.read_bit_bool()
        load_variables = stream.read_bit_bool()

        return cls(
            header=header,
            send_vars_method=send_vars_method,
            load_target=load_target,
            load_variables=load_variables,
        )


@dataclass
@register_action(code=0x9f)
class GotoFrame2(Action):
    play: bool
    scene_bias: int
    
    @classmethod
    def unpack(cls, header, stream):
        stream.read_ubits(6)  # reserved always 0
        is_scene_bias = stream.read_bit_bool()
        play = stream.read_bit_bool()
        scene_bias = 0
        if is_scene_bias:
            scene_bias = stream.read_uint16()

        return cls(
            header=header,
            play=play,
            scene_bias=scene_bias,
        )


@dataclass
@register_action(code=0x20)
class SetTarget2(Action):
    pass


@dataclass
@register_action(code=0x22)
class GetProperty(Action):
    pass


@dataclass
@register_action(code=0x23)
class SetProperty(Action):
    pass


@dataclass
@register_action(code=0x24)
class CloneSprite(Action):
    pass


@dataclass
@register_action(code=0x25)
class RemoveSprite(Action):
    pass


@dataclass
@register_action(code=0x27)
class StartDrag(Action):
    pass


@dataclass
@register_action(code=0x28)
class EndDrag(Action):
    pass


@dataclass
@register_action(code=0x8d)
class WaitForFrame2(Action):
    skip_count: int

    @classmethod
    def unpack(cls, header, stream):
        skip_count = stream.read_uint8()

        return cls(
            header=header,
            skip_count=skip_count,
        )


@dataclass
@register_action(code=0x26)
class Trace(Action):
    pass


@dataclass
@register_action(code=0x34)
class GetTime(Action):
    pass


@dataclass
@register_action(code=0x30)
class RandomNumber(Action):
    pass


#### SWF 5 Actions ####
@dataclass
@register_action(code=0x3d)
class CallFunction(Action):
    pass


@dataclass
@register_action(code=0x52)
class CallMethod(Action):
    pass


@dataclass
@register_action(code=0x88)
class ConstantPool(Action):
    constant_pool: str

    @classmethod
    def unpack(cls, header, stream):
        constant_pool = stream.read_string()

        return cls(
            header=header,
            constant_pool=constant_pool,
        )


@dataclass
@register_action(code=0x9b)
class DefineFunction(Action):
    name: str
    params: list[str]
    code_size: int

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()
        count = stream.read_uint16()
        params = [stream.read_cstring() for _ in range(count)]
    
        return cls(
            header=header,
            name=name,
            params=params,
        )


@dataclass
@register_action(code=0x3c)
class DefineLocal(Action):
    pass


@dataclass
@register_action(code=0x41)
class DefineLocal2(Action):
    pass


@dataclass
@register_action(code=0x3a)
class Delete(Action):
    pass


@dataclass
@register_action(code=0x3b)
class Delete2(Action):
    pass


@dataclass
@register_action(code=0x46)
class Enumerate(Action):
    pass


@dataclass
@register_action(code=0x49)
class Equals2(Action):
    pass


@dataclass
@register_action(code=0x4e)
class GetMember(Action):
    pass


@dataclass
@register_action(code=0x42)
class InitArray(Action):
    pass


@dataclass
@register_action(code=0x43)
class InitObject(Action):
    pass


@dataclass
@register_action(code=0x53)
class NewMethod(Action):
    pass


@dataclass
@register_action(code=0x40)
class NewObject(Action):
    pass


@dataclass
@register_action(code=0x4f)
class SetMember(Action):
    pass


@dataclass
@register_action(code=0x45)
class TargetPath(Action):
    pass


@dataclass
@register_action(code=0x94)
class NewMethod(Action):
    size: int

    @classmethod
    def unpack(cls, header, stream):
        size = stream.read_uint16()

        return cls(
            header=header,
            size=size,
        )


@dataclass
@register_action(code=0x53)
class NewMethod(Action):
    pass


@dataclass
@register_action(code=0x4a)
class ToNumber(Action):
    pass


@dataclass
@register_action(code=0x4b)
class ToString(Action):
    pass


@dataclass
@register_action(code=0x44)
class TypeOf(Action):
    pass


@dataclass
@register_action(code=0x47)
class Add2(Action):
    pass


@dataclass
@register_action(code=0x48)
class Less2(Action):
    pass


@dataclass
@register_action(code=0x3f)
class Modulo(Action):
    pass


@dataclass
@register_action(code=0x60)
class BitAnd(Action):
    pass


@dataclass
@register_action(code=0x63)
class BitLShift(Action):
    pass


@dataclass
@register_action(code=0x61)
class BitOr(Action):
    pass


@dataclass
@register_action(code=0x64)
class BitRShift(Action):
    pass


@dataclass
@register_action(code=0x65)
class BitURShift(Action):
    pass


@dataclass
@register_action(code=0x62)
class BitXor(Action):
    pass


@dataclass
@register_action(code=0x51)
class Decrement(Action):
    pass


@dataclass
@register_action(code=0x50)
class Increment(Action):
    pass


@dataclass
@register_action(code=0x4c)
class Push2(Action):
    pass


@dataclass
@register_action(code=0x3e)
class Return(Action):
    pass


@dataclass
@register_action(code=0x4d)
class StackSwap(Action):
    pass


@dataclass
@register_action(code=0x3e)
class StoreRegister(Action):
    register_number: int

    @classmethod
    def unpack(cls, header, stream):
        register_number = stream.read_uint8()

        return cls(
            header=header,
            register_number=register_number,
        )


#### SWF 6 Actions ####
@dataclass
@register_action(code=0x54)
class InstanceOf(Action):
    pass


@dataclass
@register_action(code=0x55)
class Enumerate2(Action):
    pass


@dataclass
@register_action(code=0x66)
class StrictEquals(Action):
    pass


@dataclass
@register_action(code=0x67)
class Greater(Action):
    pass


@dataclass
@register_action(code=0x68)
class StringGreater(Action):
    pass


#### SWF 7 Actions ####
@dataclass
class RegisterParam:
    register: int
    name: str

    @classmethod
    def unpack(cls, stream):
        register = stream.read_uint8()
        name = stream.read_cstring()

        return cls(
            register=register,
            name=name,
        )


@dataclass
@register_action(code=0x8e)
class DefineFunction2(Action):
    name: str
    register_count: int
    preload_parent: bool
    preload_root: bool
    suppress_super: bool
    preload_super: bool
    suppress_arguments: bool
    preload_arguments: bool
    suppress_this: bool
    preload_this: bool
    # reserved: int
    preload_global: bool
    params: list[RegisterParam]
    code_size: int

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()
        param_count = stream.read_uint16()
        register_count = stream.read_uint8()
        preload_parent = stream.read_bit_bool()
        preload_root = stream.read_bit_bool()
        suppress_super = stream.read_bit_bool()
        preload_super = stream.read_bit_bool()
        suppress_arguments = stream.read_bit_bool()
        preload_arguments = stream.read_bit_bool()
        suppress_this = stream.read_bit_bool()
        preload_this = stream.read_bit_bool()
        stream.read_ubits(7)  # reserved always 0
        preload_global = stream.read_bit_bool()
        params = [RegisterParam.unpack(stream) for _ in range(param_count)]
        code_size = stream.read_uint16()

        return cls(
            header=header,
            name=name,
            register_count=register_count,
            preload_parent=preload_parent,
            preload_root=preload_root,
            suppress_super=suppress_super,
            preload_super=preload_super,
            suppress_arguments=suppress_arguments,
            preload_arguments=preload_arguments,
            suppress_this=suppress_this,
            preload_this=preload_this,
            preload_global=preload_global,
            params=params,
            code_size=code_size,
        )


@dataclass
@register_action(code=0x69)
class Extends(Action):
    pass


@dataclass
@register_action(code=0x2b)
class CastOp(Action):
    pass


@dataclass
@register_action(code=0x2c)
class ImplementsOp(Action):
    pass


@dataclass
@register_action(code=0x8f)
class Try(Action):
    # reserved: int
    catch_in_register: bool
    finally_block: bool
    catch_block: bool
    catch_name: str
    catch_register: str
    try_body: list[int]
    catch_body: list[int]
    finally_body: list[int]

    @classmethod
    def unpack(cls, header, stream):
        stream.read_ubits(5)  # reserved always 0
        catch_in_register = stream.read_bit_bool()
        finally_block = stream.read_bit_bool()
        catch_block = stream.read_bit_bool()
        try_size = stream.read_uint16()
        catch_size = stream.read_uint16()
        finally_size = stream.read_uint16()
        catch_register = -1
        catch_name = ''
        if catch_in_register:
            catch_register = stream.read_uint8()
        else:
            catch_name = stream.read_cstring()
        try_body = [stream.read_uint8() for _ in range(try_size)]
        catch_body = [stream.read_uint8() for _ in range(catch_size)]
        finally_body = [stream.read_uint8() for _ in range(finally_size)]

        return cls(
            header=header,
            catch_in_register=catch_in_register,
            finally_block=finally_block,
            catch_block=catch_block,
            catch_name=catch_name,
            catch_register=catch_register,
            try_body=try_body,
            catch_body=catch_body,
            finally_body=finally_body,
        )



@dataclass
@register_action(code=0x2a)
class Throw(Action):
    pass


@dataclass
class ClipAction:
    events: Events
    key_code: int
    actions: list[Action]

    @classmethod
    def unpack(cls, version, stream):
        events = Events.unpack(version, stream)
        size = stream.read_uint32()
        key_code = None
        if events.is_key_press:
            key_code = stream.read_uint8()
            size = size - 1

        actions = []
        position = stream.byte_position
        while stream.byte_position < position + size:
            actions.append(unpack(stream))

        return cls(
            events=events,
            key_code=key_code,
            actions=actions,
        )


@dataclass
class ClipActions:
    # reserved: int
    events: Events
    clip_actions: list[ClipAction]
    clip_action_end: int

    @classmethod
    def unpack(cls, version, stream):
        stream.read_uint16()  # reserved always 0
        events = Events.unpack(version, stream)
        clip_actions = [ClipAction.unpack(version, stream)
                        for _ in range(len(events))]

        clip_action_end = 0
        if version <= 5:
            clip_action_end = stream.read_uint16()
        elif version >= 6:
            clip_action_end = stream.read_uint32()

        return cls(
            events=events,
            clip_actions=clip_actions,
            clip_action_end=clip_action_end,
        )


#### SWF 9 Actions ####


#### SWF 10 Actions ####
