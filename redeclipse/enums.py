from enum import Enum

class EntType(Enum):
    ET_EMPTY = 0
    ET_LIGHT = 1
    ET_MAPMODEL = 2
    ET_PLAYERSTART = 3
    ET_ENVMAP = 4
    ET_PARTICLES = 5
    ET_SOUND = 6
    ET_LIGHTFX = 7
    ET_SUNLIGHT = 8
    ET_WEAPON = 9
    ET_TELEPORT = 10
    ET_ACTOR = 11
    ET_TRIGGER = 12
    ET_PUSHER = 13
    ET_AFFINITY = 14
    ET_CHECKPOINT = 15
    ET_ROUTE = 16
    ET_UNUSEDENT = 17


class Faces(Enum):
    F_EMPTY = 0
    F_SOLID = 0x80808080


class VTYPE(Enum):
    VSLOT_SHPARAM = 0
    VSLOT_SCALE = 1
    VSLOT_ROTATION = 2
    VSLOT_OFFSET = 3
    VSLOT_SCROLL = 4
    VSLOT_LAYER = 5
    VSLOT_ALPHA = 6
    VSLOT_COLOR = 7
    VSLOT_PALETTE = 8
    VSLOT_COAST = 9
    VSLOT_NUM = 10


class OCT(Enum):
    OCTSAV_CHILDREN = 0
    OCTSAV_EMPTY = 1
    OCTSAV_SOLID = 2
    OCTSAV_NORMAL = 3
    OCTSAV_LODCUBE = 4


class OctLayers(Enum):
    LAYER_TOP = (1<<5)
    LAYER_BOTTOM = (1<<6)
    LAYER_DUP = (1<<7)
    LAYER_BLEND = LAYER_TOP | LAYER_BOTTOM
    MAXFACEVERTS = 15


class TextNum(Enum):
    DEFAULT_SKY = 0
    DEFAULT_GEOM = 1

class WeaponType(Enum):
    SWORD = 2
    SHOTGUN = 3
    SMG = 4
    FLAMER = 5
    PLASMA = 6
    ZAPPER = 7
    RIFLE = 8
    GRENADE = 9
    MINE = 10
    ROCKET = 11
