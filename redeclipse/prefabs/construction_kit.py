from redeclipse.objects import cube
import random
from redeclipse.prefabs.orientations import SELF, SOUTH, NORTH, WEST, EAST, ABOVE, BELOW
from redeclipse.prefabs.vector import FineVector

ROOM_SIZE = 8


def mv(a, b):
    return (
        a[0] + b[0],
        a[1] + b[1],
        a[2] + b[2],
    )


def mi(*args):
    if len(args) == 1:
        p0 = args[0][0]
        p1 = args[0][1]
        p2 = args[0][2]
    else:
        p0 = args[0]
        p1 = args[1]
        p2 = args[2]

    return (
        p0 * -1,
        p1 * -1,
        p2 * -1,
    )


def column_points(size, direction):
    for i in range(size):
        if direction in ('-x', '+x', 'x'):
            yield (i, 0, 0)
        elif direction in ('-y', '+y', 'y'):
            yield (0, i, 0)
        elif direction in ('-z', '+z', 'z'):
            yield (0, 0, i)


def wall_points(size, direction, limit_j=100, limit_i=100):
    for i in range(size):
        # Allow partial_j walls
        if i > limit_i:
            continue

        for j in range(size):
            # Allow partial_j walls
            if j > limit_j:
                continue

            if direction == '-z':
                yield FineVector(i, j, 0)
            elif direction == '+z':
                yield FineVector(i, j, size - 1)
            elif direction == '-y':
                yield FineVector(i, 0, j)
            elif direction == '+y':
                yield FineVector(i, size - 1, j)
            elif direction == '-x':
                yield FineVector(0, i, j)
            elif direction == '+x':
                yield FineVector(size - 1, i, j)


def multi_wall(world, directions, size, pos, tex=2):
    for direction in directions:
        wall(world, direction, size, pos, tex=tex)


def wall(world, direction, size, pos, tex=2):
    for point in wall_points(size, direction):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )

class ConstructionKitMixin(object):

    def x_column(self, world, offset, direction, length, tex=2):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        # Then get the orientation, rotated, and converted to ±xyz
        orient = VEC_ORIENT_MAP_INV[direction.rotate(self.orientation)]
        for point in column_points(length, orient):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_ceiling(self, world, offset, tex=2, size=ROOM_SIZE):
        # First, rotate the offset
        offset = offset.rotate(self.orientation)
        # And then re-add it to self.pos
        local_position = self.pos + offset

        for point in wall_points(size, '+z'):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_floor(self, world, offset, tex=2, size=ROOM_SIZE):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset

        for point in wall_points(size, '-z'):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_wall(self, world, offset, face, tex=2):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)
        # print('face %s => orientation %s => real_face %s' % (face, self.orientation, real_face))

        for point in wall_points(ROOM_SIZE, real_face):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_rectangular_prism(world, offset, x, y, z, tex=2):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset

        for point in cube_points(x, y, z):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_low_wall(self, world, offset, face, tex=2):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)

        for point in wall_points(ROOM_SIZE, real_face, limit_j=height):
            world.set_pointv(
                point + local_position,
                cube.newtexcube(tex=tex)
            )

    def x_get_face(self, face):
        if self.orientation == '+x':
            if face == NORTH:
                return '-x'
            elif face == SOUTH:
                return '+x'
            elif face == EAST:
                return '+y'
            elif face == WEST:
                return '-y'
        elif self.orientation == '-x':
            if face == NORTH:
                return '+x'
            elif face == SOUTH:
                return '-x'
            elif face == EAST:
                return '-y'
            elif face == WEST:
                return '+y'
        elif self.orientation == '+y':
            if face == NORTH:
                return '-y'
            elif face == SOUTH:
                return '+y'
            elif face == EAST:
                return '+x'
            elif face == WEST:
                return '-x'
        elif self.orientation == '-y':
            if face == NORTH:
                return '+y'
            elif face == SOUTH:
                return '-y'
            elif face == EAST:
                return '-x'
            elif face == WEST:
                return '+x'
        else:
            raise Exception()

def faded_wall(world, direction, size, pos, tex=2, prob=0.7):
    for point in wall_points(size, direction):
        if random.random() < prob:
            world.set_point(
                *mv(point, pos),
                cube.newtexcube(tex=tex)
            )


def low_wall(world, direction, size, pos, height=2, tex=2):
    for point in wall_points(size, direction, limit_j=height):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def column(world, direction, size, pos, tex=2, subtract=False):
    for point in column_points(size, direction):
        if subtract:
            world.del_point(
                *mv(point, pos)
            )
        else:
            world.set_point(
                *mv(point, pos),
                cube.newtexcube(tex=tex)
            )


def cube_points(*args):
    """
    call with a single number for a cube, or x, y, z for a rectangular prism
    """
    if len(args) == 1:
        x = args[0]
        y = args[0]
        z = args[0]
    else:
        (x, y, z) = args

    for i in range(x):
        for j in range(y):
            for k in range(z):
                yield (i, j, k)


def cube_s(world, size, pos, tex=2):
    for point in cube_points(size):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def rectangular_prism(world, x, y, z, pos, tex=2):
    for point in cube_points(x, y, z):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def slope(world, pos, corners_down=None, tex=2):
    # Broken
    c = cube.newtexcube(tex=tex)

    if 0 in corners_down:
        c.edges[4] = 136
    if 1 in corners_down:
        c.edges[5] = 136
    if 2 in corners_down:
        c.edges[7] = 136
    if 3 in corners_down:
        c.edges[10] = 136

    world.set_point(*pos, c)


def ring(world, pos, size=8, tex=2, thickness=1):
    for point in wall_points(size, '-z'):
        if point[0] < thickness or point[0] >= size - thickness or \
                point[1] < thickness or point[1] >= size - thickness:
            world.set_point(
                *mv(point, pos),
                cube.newtexcube(tex=tex)
            )

def rotate(position, orientation):
    (x, y, z) = position
    if orientation == '-x':
        return (x, y, z)
    elif orientation == '+x':
        return (-x, y, z)
    elif orientation == '-y':
        return (y, x, z)
    elif orientation == '+y':
        return (y, -x, z)
    else:
        raise Exception("Unknown Orientation")


def rotate_a(direction, orientation):
    if orientation == '-x':
        return direction + 0 % 360
    elif orientation == '+x':
        return direction + 180 % 360
    elif orientation == '-y':
        return direction + 90 % 360
    elif orientation == '+y':
        return direction + 270 % 360
    else:
        raise Exception("Unknown Orientation")
