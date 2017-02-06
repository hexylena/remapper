from redeclipse.objects import cube
from redeclipse.entities.model import MapModel
from redeclipse.prefabs.construction_kit import wall, column, wall_points, mv, \
    m, low_wall
import random

SIZE = 8


class Floor:

    @classmethod
    def render(cls, world, pos):
        wall(world, '-z', SIZE, pos)

    @classmethod
    def get_doorways(cls, pos):
        pass


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


class _Room:
    room_type = 'platform'

    def get_doorways(self):
        return [
            mv(self.pos, m(-1, 0, 0)),
            mv(self.pos, m(0, -1, 0)),
            mv(self.pos, m(1, 0, 0)),
            mv(self.pos, m(0, 1, 0))
        ]

    def get_positions(self):
        return [self.pos]

    @classmethod
    def get_transition_probs(cls):
        return {
            'platform': 0.6,
            'hallway': 0.4,
        }

class _OrientedRoom(_Room):

    def get_doorways(self):
        print('==================', self.orientation)
        if self.orientation == 'x':
            return [
                mv(self.pos, m(-1, 0, 0)),
                mv(self.pos, m(1, 0, 0)),
            ]
        else:
            return [
                mv(self.pos, m(0, -1, 0)),
                mv(self.pos, m(0, 1, 0))
            ]

    @classmethod
    def get_transition_probs(cls):
        return {
            'hallway': 0.8,
            'platform': 0.2,
        }

class _3X3Room(_Room):

    def get_doorways(self):
        return [
            mv(self.pos, m(-1, 1, 0)),
            mv(self.pos, m(3, 1, 0)),
            mv(self.pos, m(1, -1, 0)),
            mv(self.pos, m(1, 3, 0)),
        ]

    def get_positions(self):
        return [
            mv(self.pos, m(0, 0, 0)),
            mv(self.pos, m(0, 1, 0)),
            mv(self.pos, m(0, 2, 0)),
            mv(self.pos, m(1, 0, 0)),
            mv(self.pos, m(1, 1, 0)),
            mv(self.pos, m(1, 2, 0)),
            mv(self.pos, m(2, 0, 0)),
            mv(self.pos, m(2, 1, 0)),
            mv(self.pos, m(2, 2, 0)),
        ]



class BaseRoom(_Room):

    def __init__(self, world, xmap, pos, tex=2, orientation=None):
        self.pos = pos
        self.tex = tex
        wall(world, '-z', SIZE, pos, tex=tex)
        wall(world, '+z', SIZE, pos, tex=tex)


class Corridor2way(_OrientedRoom):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, orientation='x', roof=False):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        if orientation == 'x':
            wall(world, '+y', SIZE, pos)
            wall(world, '-y', SIZE, pos)
        else:
            wall(world, '+x', SIZE, pos)
            wall(world, '-x', SIZE, pos)


class Corridor2way_A(Corridor2way):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, orientation='x', roof=False):
        self.pos = pos
        self.orientation = orientation

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        if orientation == 'x':
            low_wall(world, '+y', SIZE, pos)
            low_wall(world, '-y', SIZE, pos)
        else:
            low_wall(world, '+x', SIZE, pos)
            low_wall(world, '-x', SIZE, pos)


class Corridor4way(_Room):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, roof=False, orientation=None):
        self.pos = pos
        self.roof = roof

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        column(world, 'z', 8, mv(pos, (0, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (SIZE - 1, SIZE - 1, 0)), tex=4)

class Corridor4way_A(Corridor4way):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, roof=None, orientation=None):
        self.pos = pos

        wall(world, '-z', SIZE, pos)

        column(world, 'z', 2, mv(pos, (0, 0, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (SIZE - 1, SIZE - 1, 0)), tex=4)


class AltarRoom(_3X3Room):
    room_type = 'platform_setpiece'

    def __init__(self, world, xmap, pos, roof=False, orientation=None):
        # Push the position
        self.pos = mv(pos, m(1, 0, 0))
        # For bigger rooms, we have to shift them such that the previous_posision matches a doorway.

        size = 24
        wall(world, '-z', size, self.pos)
        if roof:
            wall(world, '+z', size, self.pos)

        column(world, 'z', 8, mv(self.pos, (0, 0, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (0, size - 1, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (size - 1, 0, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (size - 1, size - 1, 0)), tex=4)

        wall(world, '-z', size - 8, mv(self.pos, (4, 4, 1)), tex=5)
        wall(world, '-z', size - 12, mv(self.pos, (6, 6, 2)), tex=6)

        Ring.render(world, mv(self.pos, (4, 4, 6)), size=size - 8, tex=7, thickness=2)

        tree = MapModel(
            x=8 * (self.pos[0] + 12),
            y=8 * (self.pos[1] + 12),
            z=8 * (self.pos[2] + 3),
            type=124
            # type=random.randint(115, 129), # Tree
        )
        xmap.ents.append(tree)


class Stair:
    room_type = 'vertical'

    @classmethod
    def render(cls, world, xmap, pos, orientation='x', roof=False):
        wall(world, '-z', SIZE, pos)

        if orientation == 'x':
            wall(world, '+y', SIZE, pos)
            wall(world, '-y', SIZE, pos)
        else:
            wall(world, '+x', SIZE, pos)
            wall(world, '-x', SIZE, pos)

