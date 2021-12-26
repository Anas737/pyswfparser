from dataclasses import dataclass

from swf.records import RGBA


__FILTERS__ = {}


def register_filter(id):
    def modifier(cls):
        __FILTERS__[id] = cls

        cls.__id__ = id
        return cls
    
    return modifier 


def unpack(stream):
    id = stream.read_uint8()
    return __FILTERS__[id].unpack(stream)


class Filter:
    pass


@dataclass
@register_filter(id=0)
class DropShadow(Filter):
    color: RGBA
    blur_x: float
    blur_y: float
    angle: float
    distance: float
    strength: float
    inner_shadow: bool
    knockout: bool
    composite_source: bool
    passes: int

    @classmethod
    def unpack(cls, stream):
        color = RGBA.unpack(stream)
        blur_x = stream.read_fixed16()
        blur_y = stream.read_fixed16()
        angle = stream.read_fixed16()
        distance = stream.read_fixed16()
        strength = stream.read_fixed8()
        inner_shadow = stream.read_bit_bool()
        knockout = stream.read_bit_bool()
        composite_source = stream.read_bit_bool()
        passes = stream.read_ubits(5)

        return cls(
            color=color,
            blur_x=blur_x,
            blur_y=blur_y,
            angle=angle,
            distance=distance,
            strength=strength,
            inner_shadow=inner_shadow,
            knockout=knockout,
            composite_source=composite_source,
            passes=passes,
        )


@dataclass
@register_filter(id=1)
class Blur(Filter):
    blur_x: float
    blur_y: float
    passes: int
    #reserved: int

    @classmethod
    def unpack(cls, stream):
        blur_x = stream.read_fixed16()
        blur_y = stream.read_fixed16()
        passes = stream.read_ubits(5)
        stream.read_ubits(3)  # reserved always 0

        return cls(
            blur_x=blur_x,
            blur_y=blur_y,
            passes=passes,
        )

    def get_filter(self, plane):
        funcs = []
        for i in range(self.blur_x):
            for j in range(self.blur_y):
                funcs[i][j] = \
                    lambda x, y: \
                        (
                            plane \
                                [x + i - self.blur_x // 2]
                                [y + j - self.blur_y // 2]
                        ) // (self.blur_x * self.blur_y)

        def filter(x, y):
            result = []

            for i in range(self.blur_x):
                for j in range(self.blur_y):
                    result += funcs[i][j](x, y)

            return result

        return filter


@dataclass
@register_filter(id=2)
class Glow(Filter):
    color: RGBA
    blur_x: float
    blur_y: float
    distance: float
    strength: float
    inner_glow: bool
    knockout: bool
    composite_source: bool
    passes: int

    @classmethod
    def unpack(cls, stream):
        color = RGBA.unpack(stream)
        blur_x = stream.read_fixed16()
        blur_y = stream.read_fixed16()
        distance = stream.read_fixed16()
        strength = stream.read_fixed8()
        inner_glow = stream.read_bit_bool()
        knockout = stream.read_bit_bool()
        composite_source = stream.read_bit_bool()
        passes = stream.read_ubits(5)

        return cls(
            color=color,
            blur_x=blur_x,
            blur_y=blur_y,
            distance=distance,
            strength=strength,
            inner_glow=inner_glow,
            knockout=knockout,
            composite_source=composite_source,
            passes=passes,
        )


@dataclass
@register_filter(id=3)
class Bevel(Filter):
    shadow_color: RGBA
    highlight_color: RGBA
    blur_x: float
    blur_y: float
    angle: float
    distance: float
    strength: float
    inner_shadow: bool
    knockout: bool
    composite_source: bool
    on_top: bool
    passes: int

    @classmethod
    def unpack(cls, stream):
        shadow_color = RGBA.unpack(stream)
        highlight_color = RGBA.unpack(stream)
        blur_x = stream.read_fixed16()
        blur_y = stream.read_fixed16()
        angle = stream.read_fixed16()
        distance = stream.read_fixed16()
        strength = stream.read_fixed8()
        inner_shadow = stream.read_bit_bool()
        knockout = stream.read_bit_bool()
        composite_source = stream.read_bit_bool()
        on_top = stream.read_bit_bool()
        passes = stream.read_ubits(4)

        return cls(
            shadow_color=shadow_color,
            highlight_color=highlight_color,
            blur_x=blur_x,
            blur_y=blur_y,
            angle=angle,
            distance=distance,
            strength=strength,
            inner_shadow=inner_shadow,
            knockout=knockout,
            composite_source=composite_source,
            on_top=on_top,
            passes=passes,
        )



@dataclass
@register_filter(id=4)
class GradientGlow(Filter):
    gradient_colors: list[RGBA]
    gradient_ratio: list[int]
    blur_x: float
    blur_y: float
    angle: float
    distance: float
    strength: float
    inner_shadow: bool
    knockout: bool
    composite_source: bool
    on_top: bool
    passes: int

    @classmethod
    def unpack(cls, stream):
        count = stream.read_uint8()
        gradient_colors = [RGBA.unpack(stream) for _ in range(count)]
        gradient_ratio = [stream.read_uint8() for _ in range(count)]
        blur_x = stream.read_fixed16()
        blur_y = stream.read_fixed16()
        angle = stream.read_fixed16()
        distance = stream.read_fixed16()
        strength = stream.read_fixed8()
        inner_shadow = stream.read_bit_bool()
        knockout = stream.read_bit_bool()
        composite_source = stream.read_bit_bool()
        on_top = stream.read_bit_bool()
        passes = stream.read_ubits(4)

        return cls(
            gradient_colors=gradient_colors,
            gradient_ratio=gradient_ratio,
            blur_x=blur_x,
            blur_y=blur_y,
            angle=angle,
            distance=distance,
            strength=strength,
            inner_shadow=inner_shadow,
            knockout=knockout,
            composite_source=composite_source,
            on_top=on_top,
            passes=passes,
        )


@dataclass
@register_filter(id=5)
class Convolution(Filter):
    divisor: float
    bias: float
    matrix: list[list[float]]
    default_color: RGBA
    #reserved: int
    clamp: int
    preserve_alpha: int

    @classmethod
    def unpack(cls, stream):
        matrix_x = stream.read_uint8()
        matrix_y = stream.read_uint8()
        divisor = stream.read_float()
        bias = stream.read_float()
        matrix = []
        for row in range(matrix_x):
            matrix[row] = [stream.read_float()
                            for _ in range(matrix_y)]
        default_color = RGBA.unpack(stream)
        stream.read_ubits(6)  # reserved always 0
        clamp = stream.read_bit_bool()
        preserve_alpha = stream.read_bit_bool()

        return cls(
            divisor=divisor,
            bias=bias,
            matrix=matrix,
            default_color=default_color,
            clamp=clamp,
            preserve_alpha=preserve_alpha,
        )

    def get_filter(self, plane):
        rows = len(self.matrix)
        cols = len(self.matrix[0]) if rows else 0

        funcs = []
        for i in range(rows):
            for j in range(cols):
                funcs[i][j] = lambda x, y: \
                    ((
                        plane \
                            [x + i - rows // 2]
                            [y + j - cols // 2]
                    ) + self.bias * self.matrix[i][j]) // self.divisor

        def filter(x, y):
            result = []

            for i in range(rows):
                for j in range(cols):
                    result += funcs[i][j](x, y)

            return result

        return filter


@dataclass
@register_filter(id=6)
class ColorMatrix(Filter):
    COLS = 5
    ROWS = 4

    matrix: list[list[float]]

    @classmethod
    def unpack(cls, stream):
        matrix = []
        for row in range(ColorMatrix.ROWS):
            matrix[row] = [stream.read_float()
                            for _ in range(ColorMatrix.COLS)]

        return cls(
            matrix=matrix,
        )

    def __mult__(self, rgba):
        rgba = (rgba.red, rgba.green, rgba.blue, rgba.aplha)

        result = []
        for i in range(0, ColorMatrix.ROWS):
            value = 0
            for j in range(0, ColorMatrix.COLS):
                value = value + self.matrix[i][j] * rgba[j]

            result[i] = value

        return RGBA(*result)


@dataclass
@register_filter(id=7)
class GradientBevel(Filter):
    composite_source: bool
    on_top: bool
    passes: int

    @classmethod
    def unpack(cls, stream):
        composite_source = stream.read_bit_bool()
        on_top = stream.read_bit_bool()
        passes = stream.read_ubits(4)

        return cls(
            composite_source=composite_source,
            on_top=on_top,
            passes=passes,
        )


@dataclass
class FilterList:
    filters: list[Filter]

    @classmethod
    def unpack(cls, stream):
        count = stream.read_uint8()
        filters = [unpack(stream) for _ in range(count)]

        return cls(
            filters=filters,
        )
