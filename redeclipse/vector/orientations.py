from redeclipse.prefabs.vector import CoarseVector, FineVector


SELF = CoarseVector(0, 0, 0)
NORTH = CoarseVector(1, 0, 0)
EAST = NORTH.rotate(90)
SOUTH = NORTH.rotate(180)
WEST = NORTH.rotate(270)

NORTHWEST = NORTH + WEST
NORTHEAST = NORTH + EAST
SOUTHWEST = SOUTH + WEST
SOUTHEAST = SOUTH + EAST

ABOVE = CoarseVector(0, 0, 1)
BELOW = CoarseVector(0, 0, -1)

TILE_CENTER = FineVector(4, 4, 0)
HALF_HEIGHT = FineVector(0, 0, 4)

NORTH_FINE = FineVector(1, 0, 0)
EAST_FINE = NORTH_FINE.rotate(90)
SOUTH_FINE = NORTH_FINE.rotate(180)
WEST_FINE = NORTH_FINE.rotate(270)
ABOVE_FINE = FineVector(0, 0, 1)
BELOW_FINE = FineVector(0, 0, -1)

VEC_ORIENT_MAP = {
    '+x': NORTH,
    '-x': SOUTH,
    '+y': EAST,
    '-y': WEST,
    '+z': ABOVE,
    '-z': BELOW,
}

VEC_ORIENT_MAP_INV = {
    v: k
    for (k, v) in VEC_ORIENT_MAP.items()
}
