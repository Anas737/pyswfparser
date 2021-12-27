from dataclasses import dataclass

from swf.stream import Stream
from swf.exceptions import UnmatchedFileLength
from swf.tags import End, Tag, unpack as unpack_tag
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


@dataclass
class File:
    header: Header
    tags: list[Tag]

    @classmethod
    def unpack(cls, stream):
        header = Header.unpack(stream)

        position = stream.byte_position
        data = stream.available_bytes

        if header.is_zlib_compressed:
            import zlib
            data = zlib.decompress(data)
        elif header.is_lzma_compressed:
            import pylzma
            data = pylzma.decompress(data)

        if position + len(data) != header.file_length:
            raise UnmatchedFileLength()

        stream = Stream(data)
        # we don't read all the header struct data in the first
        # unpack since the data might be compressed
        header.unpack_rest(stream)

        tags = []
        tag = unpack_tag(header.version, stream)
        while not isinstance(tag, End):
            tags.append(tag)
            tag = unpack_tag(header.version, stream)

        return cls(
            header=header,
            tags=tags,
        )


def parse(path):
    with open(path, 'rb') as file:
        data = file.read()
        stream = Stream(data)

    swf = File.unpack(stream)
    return swf
