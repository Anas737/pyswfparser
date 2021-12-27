from swf.file import parse
from swf.tags import DoABC


swf = parse('./RawDataMessage_0.swf')


for tag in swf.tags:
    if isinstance(tag, DoABC):
        print(tag.name)
