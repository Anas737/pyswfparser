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
        nbits = stream.read_uint_from_bits(5)
        x_min = stream.read_uint_from_bits(nbits)
        x_max = stream.read_uint_from_bits(nbits)
        y_min = stream.read_uint_from_bits(nbits)
        y_max = stream.read_uint_from_bits(nbits)

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
    mult_terms: tuple[int, int, int]
    add_terms: tuple[int, int, int]

    @classmethod
    def unpack(cls, stream):
        has_add_terms = stream.read_bit_bool()
        has_mult_terms = stream.read_bit_bool()
        nbits = stream.read_ubits(4)

        mult_terms = (None, None, None)
        if has_mult_terms:
            mult_terms = (
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
            )

        add_terms = (None, None, None)
        if has_add_terms:
            add_terms = (
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
                stream.read_sbits(nbits),
            )

        return cls(
            mult_terms=mult_terms,
            add_terms=add_terms,
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
