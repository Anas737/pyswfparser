from dataclasses import dataclass
from typing import List

from swf.stream import Stream
from swf.header import Header
from swf.exceptions import UnmatchedFileLength

@dataclass
class File:
    header: Header
    tags: List[object]

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



def parse(path):
    with open(path, 'rb') as file:
        data = file.read()
        stream = Stream(data)

    swf = File.unpack(stream)
    return swf
