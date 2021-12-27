from dataclasses import dataclass
import inspect
from swf.actions import ClipActions

from swf.enums import BlendMode
from swf.filters import FilterList
from swf.records import RGB, RGBA, CxformWithAlpha, \
                        Cxform, Matrix, MorphFillStyleArray, \
                        MorphLineStyleArray, Rectangle, Shape, \
                        ShapeWithStyle


__TAGS__ = {}


def register_tag(code):
    def modifier(cls):
        __TAGS__[code] = cls

        cls.__code__ = code
        return cls

    return modifier


@dataclass
class Header:
    code: int
    length: int

    @classmethod
    def unpack(cls, stream):
        tag_code_and_length = stream.read_uint16()

        # 6: tag type is the first 10 bits
        code = tag_code_and_length >> 6
        # 63: MASK 111111
        length = tag_code_and_length & 0x003f

        if length == 0x3f:
            length = stream.read_uint32()

        return cls(
            code=code,
            length=length,
        )

def unpack(version, stream):
    header = Header.unpack(stream)
    if header.code not in __TAGS__:
        # unkown tag
        print(f"Unkown tag {header.code}, length: {header.length}")
        if header.length != 0:
            stream.move_bytes(header.length)
        return None

    unpack_tag = __TAGS__[header.code].unpack
    args, *_ = inspect.getargspec(unpack_tag)
    if len(args) == 4:
        tag = unpack_tag(header, version, stream)
    else:
        tag = unpack_tag(header, stream)

    return tag


@dataclass
class Tag:
    header: Header

    @classmethod
    def unpack(cls, header, stream):
        return cls(
            header=header,
        )

@dataclass
@register_tag(code=4)
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
@register_tag(code=26)
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
@register_tag(code=70)
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
@register_tag(code=5)
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
@register_tag(code=28)
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
@register_tag(code=1)
class ShowFrame(Tag):
    pass


@dataclass
@register_tag(code=9)
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
@register_tag(code=43)
class FrameLabel(Tag):
    name: str
    named_anchor: bool

    @classmethod
    def unpack(cls, header, stream):
        name = stream.read_cstring()
        named_anchor = False
        if header.length > len(name) + 1:
            named_anchor_flag = stream.read_bool()

        return cls(
            header=header,
            name=name,
            named_anchor=named_anchor,
        )


@dataclass
@register_tag(code=24)
class Protect(Tag):
    pass


@dataclass
@register_tag(code=0)
class End(Tag):
    pass


@dataclass
@register_tag(code=56)
class ExportAssets(Tag):
    tags: list[tuple[int, str]]

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
@register_tag(code=57)
class ImportAssets(Tag):
    url: str
    tags: list[tuple[int, str]]

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
@register_tag(code=58)
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
@register_tag(code=64)
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


@dataclass
@register_tag(code=65)
class ScriptLimits(Tag):
    max_recursion_depth: int
    script_timeout_seconds: int

    @classmethod
    def unpack(cls, header, stream):
        max_recursion_depth = stream.read_uint16()
        script_timeout_seconds = stream.read_uint16()

        return cls(
            header=header,
            max_recursion_depth=max_recursion_depth,
            script_timeout_seconds=script_timeout_seconds,
        )


@dataclass
@register_tag(code=66)
class SetTabIndex(Tag):
    depth: int
    tab_index: int

    @classmethod
    def unpack(cls, header, stream):
        depth = stream.read_uint16()
        tab_index = stream.read_uint16()

        return cls(
            header=header,
            depth=depth,
            tab_index=tab_index,
        )


@dataclass
@register_tag(code=69)
class FileAttributes(Tag):
    #reserved: int
    use_direct_blit: bool
    use_gpu: bool
    has_metadata: bool
    actionscript3: bool
    #reserved: int
    use_network: bool
    #reserved: int

    @classmethod
    def unpack(cls, header, stream):

        stream.read_ubits(1)  # reserved always 0
        use_direct_blit = stream.read_bit_bool()
        use_gpu = stream.read_bit_bool()
        has_metadata = stream.read_bit_bool()
        actionscript3 = stream.read_bit_bool()
        stream.read_ubits(2)  # reserved always 0
        use_network = stream.read_bit_bool()
        stream.read_ubits(24)  # reserved always 0

        return cls(
            header=header,
            use_direct_blit=use_direct_blit,
            use_gpu=use_gpu,
            has_metadata=has_metadata,
            actionscript3=actionscript3,
            use_network=use_network,
        )


@dataclass
@register_tag(code=71)
class ImportAssets2(Tag):
    url: str
    #reserved: int
    #reserved: int
    tags: list[tuple[int, str]]

    @classmethod
    def unpack(cls, header, stream):
        url = stream.read_cstring()
        stream.read_uint8()  # reserved must be 1
        stream.read_uint8()  # reserved must be 0
        count = stream.read_uint16()
        tags = [(stream.read_uint16(), stream.read_cstring())
                for _ in range(count)]

        return cls(
            header=header,
            url=url,
            tags=tags,
        )


@dataclass
@register_tag(code=76)
class SymbolClass(Tag):
    tags: list[tuple[int, str]]

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
@register_tag(code=77)
class Metadata(Tag):
    metadata: str

    @classmethod
    def unpack(cls, header, stream):
        metadata = stream.read_cstring()

        return cls(
            header=header,
            metadata=metadata,
        )


@dataclass
@register_tag(code=78)
class Metadata(Tag):
    character_id: int
    splitter: Rectangle

    @classmethod
    def unpack(cls, header, stream):
        character_id = stream.read_uint16()
        splitter = Rectangle.unpack(stream)

        return cls(
            header=header,
            character_id=character_id,
            splitter=splitter,
        )


@dataclass
@register_tag(code=2)
class DefineShape(Tag):
    shape_id: int
    shape_bounds: Rectangle
    shapes: ShapeWithStyle

    @classmethod
    def unpack(cls, header, stream):
        shape_id = stream.read_uint16()
        shape_bounds = Rectangle.unpack(stream)
        shapes = ShapeWithStyle.unpack(shape_version=1, stream=stream)

        return cls(
            header=header,
            shape_id=shape_id,
            shape_bounds=shape_bounds,
            shapes=shapes,
        )


@dataclass
@register_tag(code=22)
class DefineShape2(Tag):
    shape_id: int
    shape_bounds: Rectangle
    shapes: ShapeWithStyle

    @classmethod
    def unpack(cls, header, stream):
        shape_id = stream.read_uint16()
        shape_bounds = Rectangle.unpack(stream)
        shapes = ShapeWithStyle.unpack(shape_version=2, stream=stream)

        return cls(
            header=header,
            shape_id=shape_id,
            shape_bounds=shape_bounds,
            shapes=shapes,
        )


@dataclass
@register_tag(code=32)
class DefineShape3(Tag):
    shape_id: int
    shape_bounds: Rectangle
    shapes: ShapeWithStyle

    @classmethod
    def unpack(cls, header, stream):
        shape_id = stream.read_uint16()
        shape_bounds = Rectangle.unpack(stream)
        shapes = ShapeWithStyle.unpack(shape_version=3, stream=stream)

        return cls(
            header=header,
            shape_id=shape_id,
            shape_bounds=shape_bounds,
            shapes=shapes,
        )


@dataclass
@register_tag(code=83)
class DefineShape4(Tag):
    shape_id: int
    shape_bounds: Rectangle
    edge_bounds: Rectangle
    #reserved: int
    uses_fill_winding_rule: bool
    uses_non_scaling_strokes: bool
    uses_scaling_strokes: bool
    shapes: ShapeWithStyle

    @classmethod
    def unpack(cls, header, stream):
        shape_id = stream.read_uint16()
        shape_bounds = Rectangle.unpack(stream)
        stream.read_ubits(5)  # reserved
        uses_fill_winding_rule = stream.read_bit_bool()
        uses_non_scaling_strokes = stream.read_bit_bool()
        uses_scaling_strokes = stream.read_bit_bool()
        shapes = ShapeWithStyle.unpack(shape_version=4, stream=stream)

        return cls(
            header=header,
            shape_id=shape_id,
            shape_bounds=shape_bounds,
            uses_fill_winding_rule=uses_fill_winding_rule,
            uses_non_scaling_strokes=uses_non_scaling_strokes,
            uses_scaling_strokes=uses_scaling_strokes,
            shapes=shapes,
        )

@dataclass
@register_tag(code=46)
class DefineMorphShape(Tag):
    character_id: int
    start_bounds: Rectangle
    end_bounds: Rectangle
    offset: int
    morph_fill_styles: MorphFillStyleArray
    morph_line_styles: MorphLineStyleArray
    start_edges: Shape
    end_edge: ShapeWithStyle

    @classmethod
    def unpack(cls, header, stream):
        character_id = stream.read_uint16()
        start_bounds = Rectangle.unpack(stream)
        end_bounds = Rectangle.unpack(stream)
        offset = stream.read_uint32()
        morph_fill_styles = MorphFillStyleArray.unpack(stream)
        # XXX: shape version = 1 ???
        morph_line_styles = MorphLineStyleArray.unpack(shape_version=1, stream=stream)
        start_edges = Shape.unpack(shape_version=1, stream=stream)
        end_edge = ShapeWithStyle.unpack(shape_version=1, stream=stream)

        return cls(
            header=header,
            character_id=character_id,
            start_bounds=start_bounds,
            end_bounds=end_bounds,
            offset=offset,
            morph_fill_styles=morph_fill_styles,
            morph_line_styles=morph_line_styles,
            start_edges=start_edges,
            end_edge=end_edge,
        )


@dataclass
@register_tag(code=39)
class DefineSprite(Tag):
    sprite_id: int
    frame_count: int
    control_tags: list[Tag]

    @classmethod
    def unpack(cls, header, version, stream):
        sprite_id = stream.read_uint16()
        frame_count = stream.read_uint16()

        control_tags = []
        tag = unpack(version, stream)
        while not isinstance(tag, End):
            control_tags.append(tag)
            tag = unpack(version, stream)

        return cls(
            header=header,
            sprite_id=sprite_id,
            frame_count=frame_count,
            control_tags=control_tags,
        )


@dataclass
@register_tag(code=87)
class DefineBinaryData(Tag):
    tag: int
    #reserved: int
    data: bytes

    @classmethod
    def unpack(cls, header, stream):
        position = stream.byte_position

        tag = stream.read_uint16()
        stream.read_uint32()  # reserved

        bytes_read = stream.byte_position - position
        data = stream.read_bytes(header.length - bytes_read, to_int=False)

        return cls(
            header=header,
            tag=tag,
            data=data,
        )


@dataclass
@register_tag(code=82)
class DoABC(Tag):
    flags: int
    name: str
    data: bytes

    @classmethod
    def unpack(cls, header, stream):
        position = stream.byte_position

        flags = stream.read_uint32()
        name = stream.read_cstring()

        bytes_read = stream.byte_position - position
        data = stream.read_bytes(header.length - bytes_read, to_int=False)

        return cls(
            header=header,
            flags=flags,
            name=name,
            data=data,
        )


@dataclass
@register_tag(code=41)
class ProductInfo(Tag):
    id: int
    edition: int
    major_version: int
    minor_version: int
    build_low: int
    build_high: int
    compilation_date_low: int
    compilation_date_high: int

    @classmethod
    def unpack(cls, header, stream):
        id = stream.read_uint32()
        edition = stream.read_uint32()
        major_version = stream.read_uint8()
        minor_version = stream.read_uint8()
        build_low = stream.read_uint32()
        build_high = stream.read_uint32()
        compilation_date_low = stream.read_uint32()
        compilation_date_high = stream.read_uint32()

        return cls(
            header=header,
            id=id,
            edition=edition,
            major_version=major_version,
            minor_version=minor_version,
            build_low=build_low,
            build_high=build_high,
            compilation_date_low=compilation_date_low,
            compilation_date_high=compilation_date_high,
        )
