def tag(tag_type):
    def modifier(cls):
        cls.tag_type = tag_type

        return cls

    return modifier


class Tag:
    pass


