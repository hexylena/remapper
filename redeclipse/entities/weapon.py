from redeclipse.entities import Entity
from redeclipse.vec import ivec3
from redeclipse.enums import EntType, WeaponType


class Weapon(Entity):

    def __init__(self, x=0, y=0, z=0, type=0, flags=0, modes=0, muts=0, id=0,
                 links=None, reserved=None):

        self.o = ivec3(x, y, z)
        self.type = EntType.ET_WEAPON
        self.attr_annotations = [
            'type', 'flags', 'modes', 'muts', 'id'
        ]
        self.attrs = [
            type, flags, modes, muts, id
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved
