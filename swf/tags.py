from dataclasses import dataclass

from swf.records import CxformWithAlpha, Header, Cxform, Matrix


def tag(tag_type):
    def modifier(cls):
        cls.tag_type = tag_type

        return cls

    return modifier


@dataclass
class Header:
    tag_type: int
    length: int

    @classmethod
    def unpack(cls, stream):
        tag_code_and_length = stream.read_uint16()

        # 6: tag type is the first 10 bits
        tag_type = tag_code_and_length >> 6
        # 63: MASK 111111
        length = tag_code_and_length & 63

        if length == 0x3f:
            length = stream.read_uint32()

        return cls(
            tag_type=tag_type,
            length=length,
        )


@dataclass
class Tag:
    header: Header

    @staticmethod
    def unpack(stream):
        header = Header.unpack(stream)

@dataclass
@tag(tag_type=4)
class PlaceObject:
    character_id: int
    depth: int
    matrix: Matrix
    color_transform: Cxform

    @classmethod
    def unpack(cls, stream):
        character_id = stream.read_uint16()
        depth = stream.read_uint16()
        matrix = Matrix.unpack(stream)
        color_transform = Cxform.unpack(stream)

        return cls(
            character_id=character_id,
            depth=depth,
            matrix=matrix,
            color_transform=color_transform,
        )


@dataclass
@tag(tag_type=26)
class PlaceObject2:
    has_clip_actions: bool
    has_clip_depth: bool
    has_name: bool
    has_ratio: bool
    has_color_transform: bool
    has_matrix: bool
    has_character: bool
    move: bool
    depth: int
    character_id: int
    matrix: Matrix
    color_transform: CxformWithAlpha
    ratio: int
    name: str
    clip_depth: int
    clip_actions: int

    @classmethod
    def unpack(cls, stream):
        has_clip_actions = stream.read_bit_bool()
        has_clip_depth = stream.read_bit_bool()
        has_name = stream.read_bit_bool()
        has_ratio = stream.read_bit_bool()
        has_color_transform = stream.read_bit_bool()
        has_matrix = stream.read_bit_bool()
        has_character = stream.read_bit_bool()
        move = stream.read_bit_bool()
        depth = stream.read_uint16()
        character_id = None
        matrix = None
        color_transform = None
        ratio = None
        name = None
        clip_depth = None
        clip_actions = None

        if has_character:
            character_id = stream.read_uint16()
        if has_matrix:
            matrix = Matrix.unpack(stream)
        if has_color_transform:
            color_transform = CxformWithAlpha.unpack(stream)
        if has_ratio:
            ratio = stream.read_uint16()
        if has_name:
            name = stream.read_string()
        if has_clip_depth:
            clip_depth = stream.read_uint16()
        if has_clip_actions:
            