from redeclipse.entities import Entity
from redeclipse.vec import ivec3
from redeclipse.enums import EntType


class Weapon(Entity):

    def __init__(self, xyz, type=0, flags=0, modes=0, muts=0, id=0,
                 links=None, reserved=None):

        self.o = ivec3(*(xyz * 4))
        self.type = EntType.ET_WEAPON
        self.attr_annotations = [
            'type', 'flags', 'modes', 'muts', 'id'
        ]
        self.attrs = [
            type, flags, modes, muts, id
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved


class Grenade(Entity):

    def __init__(self, xyz, flags=0, modes=0, muts=0, id=0,
                 links=None, reserved=None):

        self.o = ivec3(*(xyz * 4))
        self.type = EntType.ET_WEAPON
        self.attr_annotations = [
            'type', 'flags', 'modes', 'muts', 'id'
        ]
        self.attrs = [
            9, flags, modes, muts, id
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved
