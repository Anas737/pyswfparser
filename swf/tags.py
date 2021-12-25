from dataclasses import dataclass
from swf.enums import BlendMode

from swf.records import RGB, RGBA, ClipActions, CxformWithAlpha, FilterList, Header, Cxform, Matrix


def tag(tag_type):
    def modifier(cls):
        cls.__tag_type__ = tag_type

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

    @classmethod
    def unpack(cls, header, stream):
        pass

@dataclass
@tag(tag_type=4)
class PlaceObject(Tag):
    character_id: int
    depth: int
    matrix: Matrix
    color_transform: Cxform

    @classmethod
    def unpack(cls, header, stream):
        character_id = stream.read_uint16()
        depth = stream.read_uint16()
        matrix = Matrix.unpack(stream)
        color_transform = Cxform.unpack(stream)

        return cls(
            header=header,
            character_id=character_id,
            depth=depth,
            matrix=matrix,
            color_transform=color_transform,
        )


@dataclass
@tag(tag_type=26)
class PlaceObject2(Tag):
    move: bool
    depth: int
    character_id: int
    matrix: Matrix
    color_transform: CxformWithAlpha
    ratio: int
    name: str
    clip_depth: int
    clip_actions: ClipActions

    @classmethod
    def unpack(cls, header, version, stream):
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
        if has_character:
            character_id = stream.read_uint16()

        matrix = None
        if has_matrix:
            matrix = Matrix.unpack(stream)

        color_transform = None
        if has_color_transform:
            color_transform = CxformWithAlpha.unpack(stream)

        ratio = None
        if has_ratio:
            ratio = stream.read_uint16()

        name = None
        if has_name:
            name = stream.read_cstring()

        clip_depth = None
        if has_clip_depth:
            clip_depth = stream.read_uint16()

        clip_actions = None
        if has_clip_actions:
            clip_actions = ClipActions.unpack(version, stream)

        return cls(
            header=header,
            move=move,
            depth=depth,
            character_id=character_id,
            matrix=matrix,
            color_transform=color_transform,
            ratio=ratio,
            name=name,
            clip_depth=clip_depth,
            clip_actions=clip_actions,
        )


@dataclass
@tag(tag_type=70)
class PlaceObject3(Tag):
    move: bool
    opaque_background: bool
    depth: int
    class_name = str
    character_id: int
    matrix: Matrix
    color_transform: CxformWithAlpha
    ratio: int
    name: str
    clip_depth: int
    surface_filter_list: FilterList
    blend_mode: BlendMode
    bit_map_cache: int
    visible: int
    background_color: RGBA
    clip_actions: ClipActions

    @classmethod
    def unpack(cls, header, version, stream):
        has_clip_actions = stream.read_bit_bool()
        has_clip_depth = stream.read_bit_bool()
        has_name = stream.read_bit_bool()
        has_ratio = stream.read_bit_bool()
        has_color_transform = stream.read_bit_bool()
        has_matrix = stream.read_bit_bool()
        has_character = stream.read_bit_bool()
        move = stream.read_bit_bool()
        opaque_background = stream.read_bit_bool()
        has_visible = stream.read_bit_bool()
        has_image = stream.read_bit_bool()
        has_class_name = stream.read_bit_bool()
        has_cache_as_bitmap = stream.read_bit_bool()
        has_blend_mode = stream.read_bit_bool()
        has_filter_list = stream.read_bit_bool()
        depth = stream.read_uint16()

        class_name = None
        if has_class_name or (has_image and has_character):
            class_name = stream.read_cstring()

        character_id = None
        if has_character:
            character_id = stream.read_uint16()

        matrix = None
        if has_matrix:
            matrix = Matrix.unpack(stream)

        color_transform = None
        if has_color_transform:
            color_transform = CxformWithAlpha.unpack(stream)

        ratio = None
        if has_ratio:
            ratio = stream.read_uint16()

        name = None
        if has_name:
            name = stream.read_cstring()

        clip_depth = None
        if has_clip_depth:
            clip_depth = stream.read_uint16()

        surface_filter_list = None
        if has_filter_list:
            surface_filter_list = FilterList.unpack(stream)

        blend_mode = None
        if has_blend_mode:
            blend_mode = BlendMode(stream.read_uint8())

        bitmap_cache = None
        if has_cache_as_bitmap:
            bitmap_cache = stream.read_uint8()

        visible = None
        background_color = None
        if has_visible:
            visible = stream.read_uint8()
            background_color = RGBA.unpack(stream)

        clip_actions = None
        if has_clip_actions:
            clip_actions = ClipActions.unpack(version, stream)

        return cls(
            header=header,
            move=move,
            opaque_background=opaque_background,
            depth=depth,
            class_name=class_name,
            character_id=character_id,
            matrix=matrix,
            color_transform=color_transform,
            ratio=ratio,
            name=name,
            clip_depth=clip_depth,
            surface_filter_list=surface_filter_list,
            blend_mode=blend_mode,
            bitmap_cache=bitmap_cache,
            visible=visible,
            background_color=background_color,
            clip_actions=clip_actions,
        )


@dataclass
@tag(tag_type=5)
class RemoveObject(Tag):
    character_id: int
    depth: int

    @classmethod
    def unpack(cls, header, stream):
        character_id = stream.read_uint16()
        depth = stream.read_uint16()

        return cls(
            header=header,
            character_id=character_id,
            depth=depth
        )


@dataclass
@tag(tag_type=28)
class RemoveObject2(Tag):
    depth: int

    @classmethod
    def unpack(cls, header, stream):
        depth = stream.read_uint16()

        return cls(
            header=header,
            depth=depth
        )


@dataclass
@tag(tag_type=1)
class ShowFrame(Tag):
    pass


@dataclass
@tag(tag_type=9)
class SetBackgroundColor(Tag):
    background_color: RGB

    @classmethod
    def unpack(cls, header, stream):
        color = RGB.unpack(stream)

        return cls(
            header=header,
            background_color=color,
        )


@dataclass
@tag(tag_type=43)
class FrameLabel(Tag):
    name: str

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()

        return cls(
            header=header,
            name=name,
        )


@dataclass
@tag(tag_type=43)
class FrameLabel(Tag):
    name: str

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()
        named_anchor_flag = 0
        if header.length > len(name):
            named_anchor_flag = stream.read_uint8()

        return cls(
            header=header,
            name=name,
            named_anchor_flag=named_anchor_flag,
        )


@dataclass
@tag(tag_type=24)
class Protect(Tag):
    pass


@dataclass
@tag(tag_type=0)
class End(Tag):
    pass


@dataclass
@tag(tag_type=56)
class ExportAssets(Tag):
    tags: list(tuple[int, str])

    @classmethod
    def unpack(cls, header, stream):
        count = stream.read_uint16()
        tags = [(stream.read_uint16(), stream.read_cstring())
                for _ in range(count)]

        return cls(
            header=header,
            tags=tags,
        )


@dataclass
@tag(tag_type=57)
class ImportAssets(Tag):
    url: str
    tags: list(tuple[int, str])

    @classmethod
    def unpack(cls, header, stream):
        url = stream.read_cstring()
        count = stream.read_uint16()
        tags = [(stream.read_uint16(), stream.read_cstring())
                for _ in range(count)]

        return cls(
            header=header,
            url=url,
            tags=tags,
        )


@dataclass
@tag(tag_type=58)
class EnableDebuger(Tag):
    password: str

    @classmethod
    def unpack(cls, header, stream):
        password = stream.read_cstring()

        return cls(
            header=header,
            password=password,
        )


@dataclass
@tag(tag_type=64)
class EnableDebuger2(Tag):
    #reserved: int
    password: str

    @classmethod
    def unpack(cls, header, stream):
        stream.read_uint16()  # reserved always 0
        password = stream.read_cstring()

        return cls(
            header=header,
            password=password,
        )

