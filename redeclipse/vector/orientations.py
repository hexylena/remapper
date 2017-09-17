from math import atan2

from redeclipse.vector import CoarseVector, FineVector


#: Reference to own position
SELF = CoarseVector(0, 0, 0)
#: One (coarse) position north of the current location
NORTH = CoarseVector(0, 1, 0)
#: One (coarse) position west of the current location
WEST = NORTH.rotate(90)
#: One (coarse) position south of the current location
SOUTH = NORTH.rotate(180)
#: One (coarse) position east of the current location
EAST = NORTH.rotate(270)
#: All the cardinal directions in something iterable
CARDINALS = [EAST, NORTH, WEST, SOUTH]

#: Northwest of current location
NORTHWEST = NORTH + WEST
#: Northeast of current location
NORTHEAST = NORTH + EAST
#: Southwest of current location
SOUTHWEST = SOUTH + WEST
#: Southeast of current location
SOUTHEAST = SOUTH + EAST

#: Above current location
ABOVE = CoarseVector(0, 0, 1)
#: Below current location
BELOW = CoarseVector(0, 0, -1)

#: x-y Center of the current 8x8x8 cube
TILE_CENTER = FineVector(4, 4, 0)
#: Vertical center of the current 8x8x8 cube. Combine with TILE_CENTER for the actual cube center.
HALF_HEIGHT = FineVector(0, 0, 4)
#: Voxel offset (to the center of the voxel from the bottom left corner of the voxel)
VOXEL_OFFSET = FineVector(0.5, 0.5, 0.5)
TILE_VOX_OFF = VOXEL_OFFSET - TILE_CENTER

NORTH_FINE = FineVector(0, 1, 0)
WEST_FINE = NORTH_FINE.rotate(90)
SOUTH_FINE = NORTH_FINE.rotate(180)
EAST_FINE = NORTH_FINE.rotate(270)
ABOVE_FINE = FineVector(0, 0, 1)
BELOW_FINE = FineVector(0, 0, -1)


def get_vector_rotation(vec):
    """
    Get the rotation from a cardinal direction vector.

    :param vec: A directional vector (must be one of the named constants, N/S/E/W)
    :type vec: redeclipse.vector.CoarseVector

    :returns: A (degree) direction
    :rtype: int
    """
    return atan2(vec.y, vec.x)


def rotate_yaw(angle, orientation):
    if orientation == EAST:
        return angle % 360
    elif orientation == NORTH:
        return (angle + 90) % 360
    elif orientation == WEST:
        return (angle + 180) % 360
    elif orientation == SOUTH:
        return (angle + 270) % 360
    raise Exception("Unexpected orientation")
