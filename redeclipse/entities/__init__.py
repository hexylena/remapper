from redeclipse.vec import ivec3
from redeclipse.enums import EntType, WeaponType

class Entity:

    def __init__(self, x, y, z, type, attrs, links, reserved):
        self.o = ivec3(x, y, z)
        self.type = type
        self.attrs = attrs
        if self.type == EntType.ET_WEAPON:
            self.attrs[0] = WeaponType(self.attrs[0])
            self.attr_annotations = [
                'type', 'flags', 'modes', 'muts', 'id'
            ]
            assert len(self.attrs) == len(self.attr_annotations)
        elif self.type == EntType.ET_MAPMODEL:
            self.attr_annotations = [
                'type', 'yaw', 'pitch', 'roll', 'blend', 'scale', 'flags',
                'colour', 'palette', 'palindex', 'spinyaw', 'spinpitch',
                'spinroll'
            ]
            assert len(self.attrs) == len(self.attr_annotations)
        self.links = links
        self.reserved = reserved

    def __str__(self):
        return '[Ent %s %s [Attr: %s] [Links: %s]]' % (
            self.o, self.type.name,
            ','.join(map(str, self.attrs)),
            ','.join(map(str, self.links))
        )

    def serialize(self):
        return [self.o.x, self.o.y, self.o.z, str.encode(chr(self.type.value))] + \
            [str.encode(chr(x)) for x in self.reserved]

    def to_dict(self):
        data = {
            'position': [self.o.x, self.o.y, self.o.z],
            'type': self.type.name,
            'attr': {},
            'links': self.links,
            'reserved': self.reserved,
        }

        for (key, value) in zip(self.attr_annotations, self.attrs):
            data['attr'][key] = value

        if self.type == EntType.ET_WEAPON:
            data['attr']['type'] = data['attr']['type'].name

        return data
