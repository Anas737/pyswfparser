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
            nbits = stream.read_uint_from_bits(5)
            scale_x = stream.read_uint_from_bits(nbits)
            scale_y = stream.read_uint_from_bits(nbits)

        has_rotate = stream.read_bit_bool()
        rotate_skew_0 = 0
        rotate_skew_1 = 0
        if has_rotate:
            nbits = stream.read_uint_from_bits(5)
            rotate_skew_0 = stream.read_uint_from_bits(nbits)
            rotate_skew_1 = stream.read_uint_from_bits(nbits)

        nbits = stream.read_uint_from_bits(5)
        translate_x = stream.read_uint_from_bits(nbits)
        translate_y = stream.read_uint_from_bits(nbits)

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
