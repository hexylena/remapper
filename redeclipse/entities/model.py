from redeclipse.entities import Entity
from redeclipse.vector.re import ivec3
from redeclipse.enums import EntType


class MapModel(Entity):

    def __init__(self, xyz, type=0, yaw=0, pitch=0, roll=0, blend=0,
                 scale=0, flags=0, colour=0, palette=0, palindex=0, spinyaw=0,
                 spinpitch=0, spinroll=0, links=None, reserved=None):

        self.o = ivec3(*(xyz * 4))
        self.type = EntType.ET_MAPMODEL
        self.attrs = [
            type, yaw, pitch, roll, blend, scale, flags, colour, palette,
            palindex, spinyaw, spinpitch, spinroll
        ]
        self.links = [] if links is None else links
        self.reserved = [0, 0, 0] if reserved is None else reserved
