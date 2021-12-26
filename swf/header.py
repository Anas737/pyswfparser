from dataclasses import dataclass

from swf.records import Rectangle


__F__ = 0x46
__C__ = 0x43
__W__ = 0x57
__S__ = 0x53
__Z__ = 0x5a

__LETTERS_MAPPING__ = {
    __F__: 'F',
    __C__: 'C',
    __W__: 'W',
    __S__: 'S',
    __Z__: 'Z',
}

__SIGNATURE_VALUES__ = ('FWS', 'CWS', 'ZWS')

__COMPRESSION_MAPPING__ = {
    'FWS': None,
    'CWS': 'zlib',
    'ZWS': 'lzma',
}


class InvalidSignature(Exception):
    pass


@dataclass
class Header:
    signature: str
    version: int
    file_length: int
    frame_size: Rectangle
    frame_rate: int
    frame_count: int

    is_zlib_compressed: bool
    is_lzma_compressed: bool

    @classmethod
    def unpack(cls, stream):
        signature = ''.join([
            __LETTERS_MAPPING__.get(stream.read_uint8(), '')
            for _ in range(3)
        ])

        if signature not in __SIGNATURE_VALUES__:
            raise InvalidSignature()

        is_zlib_compressed = __COMPRESSION_MAPPING__.get(signature) == 'zlib'
        is_lzma_compressed = __COMPRESSION_MAPPING__.get(signature) == 'lzma'

        version = stream.read_uint8()
        file_length = stream.read_uint32()

        return cls(
            signature=signature,
            version=version,
            file_length=file_length,
            frame_size=None,
            frame_rate=None,
            frame_count=None,
            is_zlib_compressed=is_zlib_compressed,
            is_lzma_compressed=is_lzma_compressed,
        )

    def unpack_rest(self, stream):
        self.frame_size = Rectangle.unpack(stream)
        self.frame_rate = stream.read_uint16()
        self.frame_count = stream.read_uint16()
