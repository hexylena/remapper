from redeclipse.vec import ivec3
from redeclipse.enums import EntType, WeaponType

class Entity:

    def __init__(self, xyz, type, attrs, links, reserved):
        self.o = ivec3(x[0], y[0], z[0])
        self.type = type
        self.attrs = attrs
        if self.type == EntType.ET_WEAPON:
            self.attrs[0] = WeaponType(self.attrs[0])
            self.attr_annotations = [
                'type', 'flags', 'modes', 'muts', 'id'
            ]
        elif self.type == EntType.ET_PLAYERSTART:
            self.attrs[0] = WeaponType(self.attrs[0])
            self.attr_annotations = [
                'team', 'yaw', 'pitch', 'modes', 'muts', 'id'
            ]
        elif self.type == EntType.ET_MAPMODEL:
            self.attr_annotations = [
                'type', 'yaw', 'pitch', 'roll', 'blend', 'scale', 'flags',
                'colour', 'palette', 'palindex', 'spinyaw', 'spinpitch',
                'spinroll'
            ]
        elif self.type == EntType.ET_SUNLIGHT:
            self.attr_annotations = [
                'yaw', 'pitch', 'red', 'green', 'blue', 'offset',
                'flare', 'flarescale',
            ]
        elif self.type == EntType.ET_PUSHER:
            self.attr_annotations = [
                'yaw', 'pitch', 'force', 'maxrad', 'minrad', 'type'
            ]
        else:
            raise Exception("Cannot serialize, please specify attrs")

        # Must have right # of attrs.
        assert len(self.attrs) == len(self.attr_annotations)

        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved

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

        data['attr']['_order'] = self.attr_annotations

        return data

    @classmethod
    def from_dict(cls, d):
        attrs = [d['attr'][x] if isinstance(d['attr'][x], int) else WeaponType[d['attr'][x]] for x in d['attr']['_order']]
        e = Entity(
            x=d['position'][0],
            y=d['position'][1],
            z=d['position'][2],
            type=EntType[d['type']],
            attrs=attrs,
            links=d['links'],
            reserved=d['reserved']
        )
        return e


class PlayerSpawn(Entity):

    def __init__(self, xyz=(0, 0, 0), team=0, yaw=0, pitch=0, modes=0, muts=0, id=0, links=None, reserved=None):
        self.o = ivec3(*xyz)
        self.type = EntType.ET_PLAYERSTART
        self.attr_annotations = [
            'team', 'yaw', 'pitch', 'modes', 'muts', 'id'
        ]
        self.attrs = [
            team, yaw, pitch, modes, muts, id
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved


class Sunlight(Entity):

    def __init__(self, xyz=(0, 0, 0), yaw=0, pitch=0, red=255, green=255, blue=255, offset=45, flare=0, flarescale=0, links=None, reserved=None):
        self.o = ivec3(*xyz)
        self.type = EntType.ET_SUNLIGHT
        self.attr_annotations = [
            'yaw', 'pitch', 'red', 'green', 'blue', 'offset', 'flare', 'flarescale',
        ]
        self.attrs = [
            yaw, pitch, red, green, blue, offset, flare, flarescale
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved


class Light(Entity):

    def __init__(self, xyz, radius=64, red=255, green=255, blue=255, flare=0, flarescale=0, links=None, reserved=None):
        self.o = ivec3(*xyz)
        self.type = EntType.ET_LIGHT
        self.attr_annotations = [
            'radius', 'red', 'green', 'blue', 'flare', 'flarescale',
        ]
        self.attrs = [
            radius, red, green, blue, flare, flarescale
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved


class Pusher(Entity):

    def __init__(self, xyz, yaw=0, pitch=45, force=150, maxrad=0, minrad=0, type=0, links=None, reserved=None):
        self.o = ivec3(*xyz)
        self.type = EntType.ET_PUSHER
        self.attr_annotations = [
            'yaw', 'pitch', 'force', 'maxrad', 'minrad', 'type'
        ]
        self.attrs = [
            yaw, pitch, force, maxrad, minrad, type
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved
