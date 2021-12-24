from dataclasses import dataclass


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
class Event:
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
