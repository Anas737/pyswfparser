import math
import struct

from bitarray import bitarray


__BYTE_BITS_SIZE__ = 8
__MAX_UINT8__ = 256
__MAX_UINT16__ = 65536
__MASK_01111111__ = 127

__BYTE_ORDER_MAPPING__ = {
    'big': '>',
    'little': '<',
}


class BitsExhaustion(Exception):
    pass


class Stream:
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
        return self._buffer[self._position:]

    @property
    def bytes_buffers(self):
        return self.buffer.tobytes()

    @property
    def bit_position(self):
        return self._position

    @property
    def byte_position(self):
        return math.ceil(self._position / 8)

    @property
    def bits_length(self):
        return len(self._buffer)

    @property
    def bytes_length(self):
        return math.ceil(self.bits_length / 8)

    def tell_bits(self, size=1):
        return self._buffer[self._position: min(self.bits_length, size)]

    def tell_bytes(self, size=1):
        return self.tell_bits(size * __BYTE_BITS_SIZE__)

    def seek_bits(self, position):
        self._position = min(position, self.bits_length - 1)

    def seek_bytes(self, position):
        self.seek_bits(position * __BYTE_BITS_SIZE__)

    def move_bits(self, steps):
        self.seek_bits(self._position + steps)

    def move_bytes(self, steps):
        self.seek_bytes(self._position + steps)

    def byte_align(self):
        remaining_bits = self.byte_position * __BYTE_BITS_SIZE__ - self._position
        self.seek_bits(self._position + remaining_bits)

    def read_bits(self, size=1, signed=False):
        bits = self._read_bits(size)
        sign, *bits = bits
        bits = bitarray(bits)

        return int.from_bytes(
            bits_to_bytes(bits, str(sign)),
            byteorder=self._bitorder,
            signed=signed,
        )

    def read_bytes(self, size=1, signed=False):
        bits = self._read_byte_aligned_bits(size)
        return int.from_bytes(
            bits_to_bytes(bits),
            byteorder=self._byteorder,
            signed=signed,
        )

    def read_ubits(self, size=1):
        return self.read_bits(size)

    def read_sbits(self, size=1):
        return self.read_bits(size, signed=True)

    def read_fbits(self, size=1):
        return self.read_bits(size, signed=True) / __MAX_UINT16__

    def read_uint(self, size=1):
        return self.read_bytes(size)

    def read_sint(self, size=1):
        return self.read_bytes(size, signed=True)

    def read_uint8(self):
        return self.read_uint()

    def read_sint8(self):
        return self.read_sint()

    def read_uint16(self):
        return self.read_uint(size=2)

    def read_sint16(self):
        return self.read_sint(size=2)

    def read_uint24(self):
        return self.read_uint(size=3)
    
    def read_sint24(self):
        return self.read_sint(size=3)

    def read_uint32(self):
        return self.read_uint(size=4)

    def read_sint32(self):
        return self.read_sint(size=4)

    def read_uint64(self):
        return self.read_uint(size=8)

    def read_sint64(self):
        return self.read_sint(size=8)

    def read_fixed8(self):
        return self.read_sint16() / __MAX_UINT8__

    def read_fixed16(self):
        return self.read_sint32() / __MAX_UINT16__

    def read_float16(self):
        bits = self._read_byte_aligned_bits(size=2)

        sign = str(bits[0])
        # 3: difference between exponent bit numbers for
        # float and float16
        exponent = 3 * bitarray('0') + bits[0:5] 
        # 13: difference between mantissa bit numbers for
        # float and float16
        mantissa = 13 * bitarray(sign) + bits[5:]

        [value] = unpack_bytes(
            fmt='f',
            buffer=bits_to_bytes(exponent + mantissa),
        )

        return value

    def read_float(self):
        bits = self._read_byte_aligned_bits(size=4)

        [value] = unpack_bytes(
            fmt='f',
            buffer=bits_to_bytes(bits),
        )
        return value

    def read_double(self):
        bits = self._read_byte_aligned_bits(size=8)

        [value] = unpack_bytes(
            fmt='d',
            buffer=bits_to_bytes(bits),
        )
        return value

    def read_encoded_uint32(self):
        shift = __BYTE_BITS_SIZE__ -1
        b = self.read_uint8()

        value = b & __MASK_01111111__
        while b >> shift:
            b = self.read_uint8()
            value = (value << shift) | (b & __MASK_01111111__)

        return value

    def read_char(self):
        return self.read_uint8().decode()

    def read_cstring(self):
        string = ''
        char = self.read_char()
        while char != '\0':
            string += char
            char = self.read_char()   

        return string

    def read_string(self, length=None):
        if length is None:
            length = self.read_uint16()
        return ''.join([self.read_char() for _ in range(length)])

    def read_bool(self):
        return bool(self.read_uint8())

    def read_bit_bool(self):
        return bool(self._read_bits(1))

    def _read_bits(self, size=1, byte_aligned=False):
        if size > self.bits_length - self._position:
            raise BitsExhaustion()

        if byte_aligned:
            self.byte_align()

        bits = self._buffer[self._position: self._position + size]

        self.seek_bits(self._position + size)
        return bits

    def _read_byte_aligned_bits(self, size=1):
        return self._read_bits(size * __BYTE_BITS_SIZE__, byte_aligned=True)


def unpack_bytes(fmt, buffer, byte_order='little'):
    fmt = f"{__BYTE_ORDER_MAPPING__[byte_order]}{fmt}"
    return struct.unpack(fmt, buffer)


def bits_to_bytes(bits, sign_bit='0'):
    ceil = math.ceil(len(bits) / 8) * 8

    # NOTE: `bitarray` starts with the most significant bits
    # like `big-endian` *bit order*
    extended_sign = (ceil - len(bits)) * bitarray(sign_bit)
    return (extended_sign + bits).tobytes()


def bytes_to_bits(bytes):
    return bitarray().frombytes(bytes)
