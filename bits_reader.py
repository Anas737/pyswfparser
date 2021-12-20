import math

from bitarray import bitarray


__BYTE_BIT_SIZE__ = 8


class BitsExhaustion(Exception):
    pass


class BitsReader:
    def __init__(self, data=None, bitorder='big', byteorder='little'):
        self._buffer = bitarray()
        self._bitorder = bitorder
        self._byteorder = byteorder

        self._buffer.frombytes(
            data if data is not None else bytes()
        )
        self._position = 0

    @property
    def buffer(self):
        return self._buffer[self.position:]

    @property
    def bytes_buffers(self):
        return self.buffer.tobytes()

    @property
    def position(self):
        return self._position

    @property
    def byte_position(self):
        return math.ceil(self.position / 8)

    @property
    def bits_length(self):
        return len(self._buffer)

    @property
    def bytes_length(self):
        return math.ceil(self.bits_length / 8)

    def tell_bits(self, size=1):
        return self._buffer[self.position: min(self.bits_length, size)]

    def tell_bytes(self, size=1):
        return self.tell_bits(size * __BYTE_BIT_SIZE__)

    def seek_bits(self, position):
        self._position = min(position, self.bits_length - 1)

    def seek_bytes(self, position):
        self.seek_bits(position * __BYTE_BIT_SIZE__)

    def read_uint8(self):
        return self.read_uint_from_bytes()

    def read_uint_from_bits(self, size=1):
        bits = self._read_bits(size)

        return int.from_bytes(
            bits_to_bytes(bits),
            byteorder='big',
            signed=False,
        )

    def read_int_from_bits(self, size=2):
        if size <= 1:
            return self.read_uint_from_bits(size)

        bits = self._read_bits(size)
        sign, *bits = bits
        bits = bitarray(bits)

        return int.from_bytes(
            bits_to_bytes(bits, str(sign)),
            byteorder=self._bitorder,
            signed=True,
        )

    def read_uint_from_bytes(self, size=1):
        bits = self._read_bits_from_bytes(size)
        return int.from_bytes(
            bits_to_bytes(bits),
            byteorder=self._byteorder,
            signed=False,
        )

    def read_int_from_bytes(self, size=1):
        bits = self._read_bits_from_bytes(size)
        return int.from_bytes(
            bits_to_bytes(bits),
            byteorder=self._byteorder,
            signed=True,
        )

    def read_int8(self):
        return self.read_int_from_bytes()
    
    def read_uint16(self):
        return self.read_uint_from_bytes(size=2)

    def read_int16(self):
        return self.read_int_from_bytes(size=2)
    
    def read_uint24(self):
        return self.read_uint_from_bytes(size=3)
    
    def read_int24(self):
        return self.read_int_from_bytes(size=3)
    
    def read_uint32(self):
        return self.read_uint_from_bytes(size=4)

    def read_int32(self):
        return self.read_int_from_bytes(size=4)

    def _read_bits(self, size=1):
        if size > self.bits_length - self._position:
            raise BitsExhaustion()

        bits = self._buffer[self._position: self.position + size]

        self.seek_bits(self._position + size)
        return bits

    def _read_bits_from_bytes(self, size=1):
        return self._read_bits(size * __BYTE_BIT_SIZE__)


def bits_to_bytes(bits, bit='0'):
    ceil = math.ceil(len(bits) / 8) * 8

    return (
        (ceil - len(bits)) * bitarray(bit) + bits
    ).tobytes()
