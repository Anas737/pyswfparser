from dataclasses import dataclass
from typing import Union

from swf import byte_align_unpack
from swf.enums import CapStyleType, FillStyleType, JoinStyleType


@dataclass
class RGB:
    red: int
    green :int
    blue: int

    @classmethod
    def unpack(cls, stream):
        red = stream.read_uint8()
        green = stream.read_uint8()
        blue = stream.read_uint8()

        return cls(
            red=red,
            green=green,
            blue=blue,
        )


@dataclass
class RGBA(RGB):
    alpha: int

    @classmethod
    def unpack(cls, stream):
        rgb = RGB.unpack(stream)
        alpha = stream.read_uint8()

        return cls(
            red=rgb.red,
            green=rgb.green,
            blue=rgb.blue,
            alpha=alpha,
        )


@dataclass
class ARGB(RGB):
    alpha: int

    @classmethod
    def unpack(cls, stream):
        alpha = stream.read_uint8()
        rgb = RGB.unpack(stream)

        return cls(
            alpha=alpha,
            red=rgb.red,
            green=rgb.green,
            blue=rgb.blue,
        )


@dataclass
class Rectangle:
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    @classmethod
    @byte_align_unpack
    def unpack(cls, stream):
        nbits = stream.read_ubits(5)
        x_min = stream.read_sbits(nbits)
        x_max = stream.read_sbits(nbits)
        y_min = stream.read_sbits(nbits)
        y_max = stream.read_sbits(nbits)

        return cls(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
        )


@dataclass
class Matrix:
    has_scale: bool
    scale_x: int
    scale_y: int

    has_rotate: bool
    rotate_skew_0: int
    rotate_skew_1: int

    translate_x: int
    translate_y: int

    @classmethod
    @byte_align_unpack
    def unpack(cls, stream):
        has_scale = stream.read_bit_bool()
        scale_x = 0
        scale_y = 0
        if has_scale:
            nbits = stream.read_ubits(5)
            scale_x = stream.read_fbits(nbits)
            scale_y = stream.read_fbits(nbits)

        has_rotate = stream.read_bit_bool()
        rotate_skew_0 = 0
        rotate_skew_1 = 0
        if has_rotate:
            nbits = stream.read_ubits(5)
            rotate_skew_0 = stream.read_fbits(nbits)
            rotate_skew_1 = stream.read_fbits(nbits)

        nbits = stream.read_ubits(5)
        translate_x = stream.read_sbits(nbits)
        translate_y = stream.read_sbits(nbits)

        return cls(
            has_scale=has_scale,
            scale_x=scale_x,
            scale_y=scale_y,
            has_rotate=has_rotate,
            rotate_skew_0=rotate_skew_0,
            rotate_skew_1=rotate_skew_1,
            translate_x=translate_x,
            translate_y=translate_y,
        )

    def to_3x2(self):
        return [
            [self.scale_x, self.rotate_skew_0],
            [self.rotate_skew_1, self.scale_y],
            [self.translate_x, self.translate_y],
        ]

    def __rmul__(self, coord):
        x, y = coord

        return (
            x * self.scale_x + y * self.rotate_skew_1 + self.translate_x,
            y * self.scale_y + x * self.rotate_skew_0 + self.translate_y,
        )


@dataclass
class Cxform:
    # [red, green, blue]
    has_add_terms: bool
    add_terms: tuple[int, int, int]

    has_mult_terms: bool
    mult_terms: tuple[int, int, int]

    _nbits: int

    @classmethod
    @byte_align_unpack
    def unpack(cls, stream):
        has_add_terms = stream.read_bit_bool()
        has_mult_terms = stream.read_bit_bool()
        nbits = stream.read_ubits(4)

        mult_terms = (1, 1, 1)
        if has_mult_terms:
            mult_terms = (
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
            )

        add_terms = (0, 0, 0)
        if has_add_terms:
            add_terms = (
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
            )

        return cls(
            has_mult_terms=has_mult_terms,
            mult_terms=mult_terms,

            has_add_terms=has_add_terms,
            add_terms=add_terms,

            _nbits=nbits,
        )

    def __mul__(self, color):
        rgb = (color.red, color.green, color.blue)

        result = []
        for idx in range(3):
            result[idx] = rgb[idx] * self.mult_terms[idx] / 256

        return RGB(*result)

    def __add__(self, color):
        rgb = (color.red, color.green, color.blue)

        result = []
        for idx in range(3):
            result[idx] = rgb[idx] + self.add_terms[idx]
            result[idx] = max(0, min(result[idx], 255))

        return RGB(*result)


@dataclass
class CxformWithAlpha(Cxform):
    alpha_add_term: int
    alpha_mult_term: int

    @classmethod
    @byte_align_unpack
    def unpack(cls, stream):
        csform = Cxform.unpack(stream)

        alpha_mult_term = 1
        if csform.has_mult_terms:
            alpha_mult_term = stream.read_sbits(csform._nbits)

        alpha_add_term = 0
        if csform.has_add_terms:
            alpha_add_term = stream.read_sbits(csform._nbits)

        return cls(
            alpha_mult_term=alpha_mult_term,
            has_mult_terms=csform.has_mult_terms,
            mult_terms=csform.mult_terms,

            alpha_add_term=alpha_add_term,
            has_add_terms=csform.has_add_terms,
            add_terms=csform.add_terms,

            _nbits=csform._nbits,
        )

    def __mul__(self, color):
        rgb = super().__mul__(color)
        alpha = color.alpha * self.alpha_mult_term / 256

        return RGBA(
            red=rgb.red,
            green=rgb.green,
            blue=rgb.blue,
            alpha=alpha,
        )

    def __add__(self, color):
        rgb = super().__add__(color)
        alpha =  max(0, min(color.alpha + self.alpha_add_term, 255))

        return RGBA(
            red=rgb.red,
            green=rgb.green,
            blue=rgb.blue,
            alpha=alpha,
        )

@dataclass
class Events:
    is_key_up: bool
    is_key_down: bool
    is_mouse_up: bool
    is_mouse_down: bool
    is_mouse_move: bool
    is_unload: bool
    is_enter_frame: bool
    is_load: bool
    is_drag_over: bool
    is_roll_out: bool
    is_roll_over: bool
    is_release_outside: bool
    is_release: bool
    is_press: bool
    is_initialize: bool
    is_data: bool
    # reserved: int
    is_construct: bool
    is_key_press: bool
    is_drag_out: bool
    # reserved: int

    @classmethod
    def unpack(cls, version, stream):
        is_key_up = stream.read_bit_bool()
        is_key_down = stream.read_bit_bool()
        is_mouse_up = stream.read_bit_bool()
        is_mouse_down = stream.read_bit_bool()
        is_mouse_move = stream.read_bit_bool()
        is_unload = stream.read_bit_bool()
        is_enter_frame = stream.read_bit_bool()
        is_load = stream.read_bit_bool()
        is_drag_over = stream.read_bit_bool()
        is_roll_out = stream.read_bit_bool()
        is_roll_over = stream.read_bit_bool()
        is_release_outside = stream.read_bit_bool()
        is_release = stream.read_bit_bool()
        is_press = stream.read_bit_bool()
        is_initialize = stream.read_bit_bool()
        is_data = stream.read_bit_bool()

        is_construct = False
        is_key_press = False
        is_drag_out = False
        if version >= 6:
            stream.read_ubits(5)  # reserved is always 0
            is_construct = stream.read_bit_bool()
            is_key_press = stream.read_bit_bool()
            is_drag_out = stream.read_bit_bool()
            stream.read_ubits(8)  # reserved is always 0

        return cls(
            is_key_up=is_key_up,
            is_key_down=is_key_down,
            is_mouse_up=is_mouse_up,
            is_mouse_down=is_mouse_down,
            is_mouse_move=is_mouse_move,
            is_unload=is_unload,
            is_enter_frame=is_enter_frame,
            is_load=is_load,
            is_drag_over=is_drag_over,
            is_roll_out=is_roll_out,
            is_roll_over=is_roll_over,
            is_release_outside=is_release_outside,
            is_release=is_release,
            is_press=is_press,
            is_initialize=is_initialize,
            is_data=is_data,
            is_construct=is_construct,
            is_key_press=is_key_press,
            is_drag_out=is_drag_out,
        )


@dataclass
class Grad:
    ratio: int
    color: RGB

    @classmethod
    def unpack(cls, shape_version, stream):
        ratio = stream.read_uint8()
        
        if shape_version <= 2:
            color = RGB.unpack(stream)
        else:
            color = RGBA.unpack(stream)

        return cls(
            ratio=ratio,
            color=color,
        )

@dataclass
class Gradient:
    spread_mode: int
    imterpolation_mode: RGB
    grads: list[Grad]

    @classmethod
    def unpack(cls, shape_version, stream):
        spread_mode = stream.read_ubits(2)
        imterpolation_mode = stream.read_ubits(2)
        count = stream.read_ubits(4)
        grads = [Grad.unpack(shape_version, stream)
                for _ in range(count)]

        return cls(
            spread_mode=spread_mode,
            imterpolation_mode=imterpolation_mode,
            grads=grads,
        )


@dataclass
class FocalGradient:
    spread_mode: int
    imterpolation_mode: RGB
    grads: list[Grad]
    focal_point: float

    @classmethod
    def unpack(cls, shape_version, stream):
        spread_mode = stream.read_ubits(2)
        imterpolation_mode = stream.read_ubits(2)
        count = stream.read_ubits(4)
        grads = [Grad.unpack(shape_version, stream)
                for _ in range(count)]
        focal_point = stream.read_fixed8()

        return cls(
            spread_mode=spread_mode,
            imterpolation_mode=imterpolation_mode,
            grads=grads,
            focal_point=focal_point,
        )


@dataclass
class FillStyle:
    type: int
    color: RGB
    gradient_matrix: Matrix
    gradient: Gradient
    bitmap_id: int
    bitmap_matrix: Matrix

    @classmethod
    def unpack(cls, shape_version, stream):
        type = FillStyleType(stream.read_uint8())
        color = None
        gradient_matrix = None
        gradient = None
        bitmap_id = None
        bitmap_matrix= None
        if type == FillStyleType.SOLID:
            if shape_version <= 2:
                color = RGB.unpack(stream)
            else:
                color = RGBA.unpack(stream)
        elif type in (
                        FillStyleType.LINEAR_GRADIENT,
                        FillStyleType.RADIAL_GRADIENT,
                        FillStyleType.FOCAL_RADIAL_GRADIENT,
                    ):
            gradient_matrix = Matrix.unpack(stream)
            if type == FillStyleType.FOCAL_RADIAL_GRADIENT:
                gradient =  FocalGradient.unpack(stream)
            else:
                gradient =  Gradient.unpack(stream)
        elif type in (
                        FillStyleType.REPEATING_BITMAP,
                        FillStyleType.CLIPPED_BITMAP,
                        FillStyleType.NON_SMOOTHED_REPEATING_BITMAP,
                        FillStyleType.NON_SMOOTHED_CLIPPED_BITMAP,
                    ):
            bitmap_id = stream.read_uint16()
            bitmap_matrix = Matrix.unpack(stream)

        return cls(
            type=type,
            color=color,
            gradient_matrix=gradient_matrix,
            gradient=gradient,
            bitmap_id=bitmap_id,
            bitmap_matrix=bitmap_matrix,
        )


@dataclass
class FillStyleArray:
    fill_styles: list[FillStyle]

    @classmethod
    def unpack(cls, shape_version, stream):
        count = stream.read_uint8()
        if count == 0xff:
            count = stream.read_uint16()
        fill_styles = [FillStyle.unpack(shape_version, stream)
                        for _ in range(count)]
        return cls(
            fill_styles=fill_styles,
        )

@dataclass
class LineStyle:
    width: int
    color: RGB

    @classmethod
    def unpack(cls, shape_version, stream):
        width = stream.read_uint16()

        if shape_version <= 2:
            color = RGB.unpack(stream)
        else:
            color = RGBA.unpack(stream)

        return cls(
            width=width,
            color=color,
        )


class ShapeRecord:
    pass


def unpack_shape(fill_bits, line_bits, shape_version, stream):
    is_edge_record = stream.read_bit_bool()
    if is_edge_record:
        is_straight = stream.read_bit_bool()
        if is_straight:
            return StraightEdge.unpack(stream)
        else:
            return CurvedEdge.unpack(stream)

    flags = stream.tell_bits(5)
    if flags == 0:
        return EndShape.unpack(stream)

    return StyleChange.unpack(fill_bits, line_bits, shape_version, stream)

@dataclass
class StyleChange(ShapeRecord):
    is_edge_record: bool
    move_delta_x: int
    move_delta_y: int
    fill_style_0: int
    fill_style_1: int
    line_style: int
    fill_styles: int
    line_styles: int

    @classmethod
    def unpack(cls, fill_bits, line_bits, shape_version, stream):
        state_new_styles = stream.read_bit_bool()
        state_line_style = stream.read_bit_bool()
        state_fill_style_1 = stream.read_bit_bool()
        state_fill_style_0 = stream.read_bit_bool()
        state_move_to = stream.read_bit_bool()

        move_delta_x = None
        move_delta_y = None
        if state_move_to:
            move_bits = stream.read_ubits(5)
            move_delta_x = stream.read_sbits(move_bits)
            move_delta_y = stream.read_sbits(move_bits)

        fill_style_0 = None
        if state_fill_style_0:
            fill_style_0 = stream.read_ubits(fill_bits)

        fill_style_1 = None
        if state_fill_style_1:
            fill_style_1 = stream.read_ubits(fill_bits)

        line_style = None
        if state_line_style:
            line_style = stream.read_ubits(line_bits)

        fill_styles = None
        line_styles = None
        fill_bits = 0
        line_bits = 0

        if state_new_styles:
            fill_styles = FillStyleArray.unpack(shape_version, stream)
            line_styles = LineStyleArray.unpack(shape_version, stream)
            fill_bits = stream.read_ubits(4)
            line_bits = stream.read_ubits(4)

        return cls(
            is_edge_record=False,
            move_delta_x=move_delta_x,
            move_delta_y=move_delta_y,
            fill_style_0=fill_style_0,
            fill_style_1=fill_style_1,
            line_style=line_style,
            fill_styles=fill_styles,
            line_styles=line_styles,
        )


@dataclass
class StraightEdge(ShapeRecord):
    is_edge_record: bool
    is_straight: bool
    general_line_flag: bool
    delta_x: int
    delta_y: int
    vert_line_flag: bool

    @classmethod
    def unpack(cls, stream):
        bits = stream.read_ubits(4)
        general_line_flag = stream.read_bit_bool()
        delta_x = 0
        delta_y = 0
        vert_line_flag = False
        if not general_line_flag:
            vert_line_flag = stream.read_bit_bool()

        if general_line_flag or not vert_line_flag:
            delta_x = stream.read_sbits(bits + 2)
        if general_line_flag or vert_line_flag:
            delta_y = stream.read_sbits(bits + 2)

        return cls(
            is_edge_record=True,
            is_straight=True,
            general_line_flag=general_line_flag,
            delta_x=delta_x,
            delta_y=delta_y,
            vert_line_flag=vert_line_flag,
        )


@dataclass
class CurvedEdge(ShapeRecord):
    is_edge_record: bool
    is_straight: bool
    control_delta_x: int
    control_delta_y: int
    anchor_delta_x: int
    anchor_delta_y: int

    @classmethod
    def unpack(cls, stream):
        bits = stream.read_ubits(4)
        control_delta_x = stream.read_sbits(bits + 2)
        control_delta_y = stream.read_sbits(bits + 2)
        anchor_delta_x = stream.read_sbits(bits + 2)
        anchor_delta_y = stream.read_sbits(bits + 2)

        return cls(
            is_edge_record=True,
            is_straight=False,
            control_delta_x=control_delta_x,
            control_delta_y=control_delta_y,
            anchor_delta_x=anchor_delta_x,
            anchor_delta_y=anchor_delta_y,
        )


@dataclass
class EndShape(ShapeRecord):
    is_edge_record: bool
    end_of_shape: int

    @classmethod
    def unpack(cls, stream):
        end_of_shape = stream.read_ubits(5)

        return cls(
            is_edge_record=False,
            end_of_shape=end_of_shape,
        )

@dataclass
class Shape:
    fill_bits: int
    line_bits: int
    shape_records: list[ShapeRecord]

    @classmethod
    def unpack(cls, shape_version, stream):
        fill_bits = stream.read_ubits(4)
        line_bits = stream.read_ubits(4)
        shape_records = []
        shape = unpack_shape(fill_bits, line_bits, shape_version, stream)
        while not isinstance(shape, EndShape):
            shape_records.append(shape)
            shape = unpack_shape(fill_bits, line_bits, shape_version, stream)

        return cls(
            fill_bits=fill_bits,
            line_bits=line_bits,
            shape_records=shape_records,
        )


@dataclass
class LineStyleArray:
    line_styles: list[LineStyle]

    @classmethod
    def unpack(cls, shape_version, stream):
        count = stream.read_uint8()
        if count == 0xff:
            count = stream.read_uint16()
        line_styles = [LineStyle.unpack(shape_version, stream)
                        for _ in range(count)]
        
        return cls(
            line_styles=line_styles,
        )


@dataclass
class ShapeWithStyle(Shape):
    fill_styles: FillStyleArray
    line_styles: LineStyleArray

    @classmethod
    def unpack(cls, shape_version, stream):
        fill_styles = FillStyleArray.unpack(shape_version, stream)
        line_styles = LineStyleArray.unpack(shape_version, stream)
        shape = Shape.unpack(shape_version, stream)

        return cls(
            fill_bits=shape.fill_bits,
            line_bits=shape.line_bits,
            shape_records=shape.shape_records,
            fill_styles=fill_styles,
            line_styles=line_styles,
        )


@dataclass
class MorphGradRecord:
    start_ratio: int
    start_color: RGBA
    end_ratio: int
    end_color: RGBA

    @classmethod
    def unpack(cls, stream):
        start_ratio = stream.read_uint8()
        start_color = RGBA.unpack(stream)
        end_ratio = stream.read_uint8()
        end_color = RGBA.unpack(stream)

        return cls(
            start_ratio=start_ratio,
            start_color=start_color,
            end_ratio=end_ratio,
            end_color=end_color,
        )


@dataclass
class MorphGradient:
    morph_grads: list[MorphGradRecord]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_uint8()
        morph_grads = [MorphGradRecord.unpack(stream) 
                        for _ in range(count)]

        return cls(
            morph_grads=morph_grads,
        )

@dataclass
class MorphFillStyle:
    type: int
    start_color: RGBA
    end_color: RGBA
    start_gradient_matrix: Matrix
    end_gradient_matrix: Matrix
    gradient: MorphGradient
    bitmap_id: int
    start_bitmap_matrix: Matrix
    end_bitmap_matrix: Matrix

    @classmethod
    def unpack(cls, stream):
        type = FillStyleType(stream.read_uint8())
        start_color = None
        end_color = None
        start_gradient_matrix = None
        end_gradient_matrix = None
        gradient = None
        bitmap_id = None
        start_bitmap_matrix = None
        end_bitmap_matrix = None
        if type == FillStyleType.SOLID:
            start_color = RGBA.unpack(stream)
            end_color = RGBA.unpack(stream)
        elif type in (
                        FillStyleType.LINEAR_GRADIENT,
                        FillStyleType.RADIAL_GRADIENT,
                    ):
            start_gradient_matrix = Matrix.unpack(stream)
            end_gradient_matrix = Matrix.unpack(stream)
            gradient =  MorphGradient.unpack(stream)
        elif type in (
                        FillStyleType.REPEATING_BITMAP,
                        FillStyleType.CLIPPED_BITMAP,
                        FillStyleType.NON_SMOOTHED_REPEATING_BITMAP,
                        FillStyleType.NON_SMOOTHED_CLIPPED_BITMAP,
                    ):
            bitmap_id = stream.read_uint16()
            start_bitmap_matrix = Matrix.unpack(stream)
            end_bitmap_matrix = Matrix.unpack(stream)

        return cls(
            type=type,
            start_color=start_color,
            end_color=end_color,
            start_gradient_matrix=start_gradient_matrix,
            end_gradient_matrix=end_gradient_matrix,
            gradient=gradient,
            bitmap_id=bitmap_id,
            start_bitmap_matrix=start_bitmap_matrix,
            end_bitmap_matrix=end_bitmap_matrix,
        )


@dataclass
class MorphLineStyle:
    start_width: int
    end_width: int
    start_color: RGBA
    end_color: RGBA


    @classmethod
    def unpack(cls, stream):
        start_width = stream.read_uint16()
        end_width = stream.read_uint16()
        start_color = RGBA.unpack(stream)
        end_color = RGBA.unpack(stream)

        return cls(
            start_width=start_width,
            end_width=end_width,
            start_color=start_color,
            end_color=end_color,
        )


@dataclass
class MorphLineStyle2:
    start_width: int
    end_width: int
    start_cap_style: CapStyleType
    join_style: JoinStyleType
    has_fill: bool
    no_h_scale: bool
    no_v_scale: bool
    pixel_hinting: bool
    #reserved: int
    no_close: bool
    end_cap_style: CapStyleType
    miter_limit_factor: int
    start_color: RGBA
    end_color: RGBA
    fill_type: MorphFillStyle

    @classmethod
    def unpack(cls, stream):
        start_width = stream.read_uint16()
        end_width = stream.read_uint16()
        start_cap_style = CapStyleType(stream.read_ubit(2))
        join_style = JoinStyleType(stream.read_ubit(2))
        has_fill = stream.read_bit_bool()
        no_h_scale = stream.read_bit_bool()
        no_v_scale = stream.read_bit_bool()
        pixel_hinting = stream.read_bit_bool()
        stream.read_ubits(5)  # reserved
        no_close = stream.read_bit_bool()
        end_cap_style = CapStyleType(stream.read_ubit(2))

        miter_limit_factor = None
        if join_style == JoinStyleType.MITER:
            miter_limit_factor = stream.read_uint16()

        start_color = None
        end_color = None
        fill_stype = None
        if has_fill:
            fill_type = MorphFillStyle.unpack(stream)
        else:
            start_color = RGBA.unpack(stream)
            end_color = RGBA.unpack(stream)

        return cls(
            start_width=start_width,
            end_width=end_width,
            start_cap_style=start_cap_style,
            join_style=join_style,
            has_fill=has_fill,
            no_h_scale=no_h_scale,
            no_v_scale=no_v_scale,
            pixel_hinting=pixel_hinting,
            no_close=no_close,
            end_cap_style=end_cap_style,
            miter_limit_factor=miter_limit_factor,
            start_color=start_color,
            end_color=end_color,
            fill_type=fill_type,
        )


@dataclass
class MorphLineStyleArray:
    line_styles: list[Union[MorphLineStyle, MorphLineStyle2]]

    @classmethod
    def unpack(cls, shape_version, stream):
        count = stream.read_uint8()
        if count == 0xff:
            count = stream.read_uint16()
        line_styles = [
            MorphLineStyle.unpack(stream) if shape_version == 1 else \
            MorphLineStyle2.unpack(stream)
            for _ in range(count)
        ]

        return cls(
            line_styles=line_styles,
        )


@dataclass
class MorphFillStyleArray:
    line_styles: list[MorphFillStyle]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_uint8()
        if count == 0xff:
            count = stream.read_uint16()
        line_styles = [
            MorphFillStyle.unpack(stream) for _ in range(count)
        ]

        return cls(
            line_styles=line_styles,
        )

