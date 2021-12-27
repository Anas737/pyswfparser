def byte_align_unpack(unpack):
    def _unpack(*args):
        if isinstance(args, tuple):
            *_, stream = args
        else:
            stream = args

        unpack(*args)
        stream.byte_align()

    return _unpack
