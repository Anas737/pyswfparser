from dataclasses import dataclass

from swf.stream import Stream
from swf.exceptions import UnmatchedFileLength
from swf.header import Header
from swf.tags import End, Tag, unpack as unpack_tag


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
            # print(tag)
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
