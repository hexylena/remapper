from redeclipse.objects import cube
from redeclipse.entities.model import MapModel
import random


def mv(a, b):
    return (
        a[0] + b[0],
        a[1] + b[1],
        a[2] + b[2],
    )

def column_points(size, direction):
    for i in range(size):
        if direction in ('-x', '+x', 'x'):
            yield (i, 0, 0)
        elif direction in ('-y', '+y', 'y'):
            yield (0, i, 0)
        elif direction in ('-z', '+z', 'z'):
            yield (0, 0, i)

def wall_points(size, direction):
    for i in range(size):
        for j in range(size):
            if direction == '-z':
                yield (i, j, 0)
            elif direction == '+z':
                yield (i, j, size - 1)
            elif direction == '-y':
                yield (i, 0, j)
            elif direction == '+y':
                yield (i, size - 1, j)
            elif direction == '-x':
                yield (0, i, j)
            elif direction == '+x':
                yield (size - 1, i, j)

def wall(world, direction, size, pos, tex=2):
    for point in wall_points(size, direction):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )

def column(world, direction, size, pos, tex=2):
    for point in column_points(size, direction):
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

class Floor:

    @classmethod
    def render(cls, world, pos, size=8):
        wall(world, '-z', size, pos)

class Ring:

    @classmethod
    def render(cls, world, pos, size=8, tex=2, thickness=1):
        for point in wall_points(size, '-z'):
            if point[0] < thickness or point[0] >= size - thickness or \
                    point[1] < thickness or point[1] >= size - thickness:
                world.set_point(
                    *mv(point, pos),
                    cube.newtexcube(tex=tex)
                )


class BaseRoom:

    @classmethod
    def render(cls, world, xmap, pos, size=8):
        wall(world, '-z', size, pos)
        wall(world, '+z', size, pos)


class Corridor:

    @classmethod
    def render(cls, world, xmap, pos, orientation='x', roof=False):
        size = 8
        wall(world, '-z', size, pos)
        if roof:
            wall(world, '+z', size, pos)

        if orientation == 'x':
            wall(world, '+y', size, pos)
            wall(world, '-y', size, pos)
        else:
            wall(world, '+x', size, pos)
            wall(world, '-x', size, pos)


class AltarRoom:

    @classmethod
    def render(cls, world, xmap, pos, orientation='x', roof=False):
        size = 24
        wall(world, '-z', size, pos)
        if roof:
            wall(world, '+z', size, pos)

        column(world, 'z', 8, mv(pos, (0, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (0, size - 1, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (size - 1, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (size - 1, size - 1, 0)), tex=4)

        wall(world, '-z', size - 8, mv(pos, (4, 4, 1)), tex=5)
        wall(world, '-z', size - 12, mv(pos, (6, 6, 2)), tex=6)

        Ring.render(world, mv(pos, (4, 4, 6)), size - 8, tex=7, thickness=2)

        tree = MapModel(
            x=8 * (pos[0] + 12),
            y=8 * (pos[1] + 12),
            z=8 * (pos[2] + 3),
            type=random.randint(115, 129), # Tree
        )
        xmap.ents.append(tree)


class Stair:

    @classmethod
    def render(cls, world, xmap, pos, orientation='x', roof=False):
        size = 8
        wall(world, '-z', size, pos)

        if orientation == 'x':
            wall(world, '+y', size, pos)
            wall(world, '-y', size, pos)
        else:
            wall(world, '+x', size, pos)
            wall(world, '-x', size, pos)

