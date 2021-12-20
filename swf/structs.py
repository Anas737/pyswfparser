from dataclasses import dataclass


@dataclass
class Rectangle:
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    @classmethod
    def unpack(cls, reader):
        nbits = reader.read_uint_from_bits(5)
        print(nbits)
        x_min = reader.read_uint_from_bits(nbits)
        print(x_min)
        x_max = reader.read_uint_from_bits(nbits)
        print(x_max)
        y_min = reader.read_uint_from_bits(nbits)
        y_max = reader.read_uint_from_bits(nbits)

        return cls(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
        )
