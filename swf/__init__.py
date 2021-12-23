from dataclasses import dataclass
from typing import List

from swf.stream import Stream
from swf.exceptions import UnmatchedFileLength
from swf.header import Header
from swf.tags import Tag


@dataclass
class File:
    header: Header
    tags: List[Tag]

    @classmethod
    def unpack(cls, stream):
        header = Header.unpack(stream)

        position = stream.byte_position
        data = stream.bytes_buffers

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

        return cls(
            header=header,
            tags=[],
        )


def tag(tag_code):
    def modifier(cls):
        cls.tag_code = tag_code

        return cls

    return modifier


def parse(path):
    with open(path, 'rb') as file:
        data = file.read()
        stream = Stream(data)

    swf = File.unpack(stream)
    return swf
