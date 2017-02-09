from redeclipse.objects import cube
from redeclipse.entities import Light, PlayerSpawn
from redeclipse.entities.model import MapModel
from redeclipse.prefabs.construction_kit import wall, column, wall_points, mv, \
    m, low_wall, cube_s
import random # noqa
import noise
import colorsys
random.seed(42)
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
            'platform': 0.1,
            'hallway': 0.8,
            'vertical': 0.8,
        }


    def light(self):
        # 70% chance of a light below
        # if random.random() < 0.7:
        if True:
            if hasattr(self, 'size'):
                size = self.size
            else:
                size = SIZE

            # Map to 0-1 scale
            nums = list(map(
                lambda x: x * (2 ** -7),
                self.pos
            ))

            # convert a tuple of three nums + offset into a
            # 0-255 integer.
            def kleur(nums, base):
                return int(abs(noise.pnoise3(*nums, base=base)) * 255)

            # Now we generate our colour:
            r = kleur(nums, 10)
            g = kleur(nums, 0)
            b = kleur(nums, 43)

            # RGB isn't great, because it means low values of RGB are
            # low luminance. So we convert to HSV to get hue
            (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
            # We then peg S and V to high values and only retain huge
            (r, g, b) = colorsys.hsv_to_rgb(h, 1, 255)
            # This should give us a bright colour on a continuous form

            light = Light(
                x=8 * (self.pos[0] + size / 2),
                y=8 * (self.pos[1] + size / 2),
                # Light above head
                z=8 * (self.pos[2] + 4),
                red=int(r),
                green=int(g),
                blue=int(b),
                radius=64,
            )
            self.xmap.ents.append(light)

class _OrientedRoom(_Room):

    def get_doorways(self):
        print('==================', self.orientation)
        if self.orientation in ('+x', '-x'):
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
            'hallway': 0.9,
            'platform': 0.2,
            'vertical': 0.9,
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
        self.xmap = xmap

        wall(world, '-z', SIZE, pos, tex=tex)
        wall(world, '+z', SIZE, pos, tex=tex)

        # Add default spawn in base room  (so camera dosen't spawn in
        # miles above where we want to be)
        spawn = PlayerSpawn(
            x=8 * (self.pos[0] + SIZE / 2),
            y=8 * (self.pos[1] + SIZE / 2),
            z=8 * (self.pos[2] + 1),
        )
        xmap.ents.append(spawn)

        self.light()


class Corridor2way(_OrientedRoom):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, orientation='+x', roof=False):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof
        self.xmap = xmap

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        if orientation in ('+x', '-x'):
            wall(world, '+y', SIZE, pos)
            wall(world, '-y', SIZE, pos)
        else:
            wall(world, '+x', SIZE, pos)
            wall(world, '-x', SIZE, pos)

        self.light()


class Corridor2way_A(Corridor2way):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, orientation='+x', roof=False):
        self.pos = pos
        self.orientation = orientation
        self.xmap = xmap

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        if orientation in ('+x', '-x'):
            low_wall(world, '+y', SIZE, pos)
            low_wall(world, '-y', SIZE, pos)
        else:
            low_wall(world, '+x', SIZE, pos)
            low_wall(world, '-x', SIZE, pos)

        self.light()


class Corridor4way(_Room):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, roof=False, orientation=None):
        self.pos = pos
        self.roof = roof
        self.xmap = xmap

        wall(world, '-z', SIZE, pos)
        if roof:
            wall(world, '+z', SIZE, pos)

        column(world, 'z', 8, mv(pos, (0, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 8, mv(pos, (SIZE - 1, SIZE - 1, 0)), tex=4)

        self.light()


class Corridor4way_A(Corridor4way):
    room_type = 'hallway'

    def __init__(self, world, xmap, pos, roof=None, orientation=None):
        self.pos = pos
        self.xmap = xmap
        self.light()

        wall(world, '-z', SIZE, pos)

        column(world, 'z', 2, mv(pos, (0, 0, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 2, mv(pos, (SIZE - 1, SIZE - 1, 0)), tex=4)


class SpawnRoom(_OrientedRoom):
    room_type = 'platform_setpiece'

    def __init__(self, world, xmap, pos, roof=None, orientation=None):
        self.pos = pos
        self.orientation = orientation
        self.xmap = xmap
        self.light()
        tex = 9

        wall(world, '-z', SIZE, pos, tex=tex)
        wall(world, '+z', SIZE, pos, tex=tex)

        if orientation == '+x':
            wall(world, '-x', SIZE, pos)
            wall(world, '+y', SIZE, pos)
            wall(world, '-y', SIZE, pos)
        elif orientation == '-x':
            wall(world, '+x', SIZE, pos)
            wall(world, '+y', SIZE, pos)
            wall(world, '-y', SIZE, pos)
        elif orientation == '+y':
            wall(world, '-y', SIZE, pos)
            wall(world, '+x', SIZE, pos)
            wall(world, '-x', SIZE, pos)
        elif orientation == '-y':
            wall(world, '+y', SIZE, pos)
            wall(world, '+x', SIZE, pos)
            wall(world, '-x', SIZE, pos)
        else:
            raise Exception("Unknown orientation %s" % orientation)

        spawn = PlayerSpawn(
            x=8 * (self.pos[0] + SIZE / 2),
            y=8 * (self.pos[1] + SIZE / 2),
            z=8 * (self.pos[2] + 1),
        )
        xmap.ents.append(spawn)
        light = Light(
            x=8 * (self.pos[0] + SIZE / 2),
            y=8 * (self.pos[1] + SIZE / 2),
            z=8 * (self.pos[2] + 6),
        )
        xmap.ents.append(light)


class AltarRoom(_3X3Room):
    room_type = 'platform_setpiece'

    def __init__(self, world, xmap, pos, roof=False, orientation=None):
        # Push the position
        self.pos = mv(pos, m(1, 0, 0))
        self.xmap = xmap
        self.light()
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


class Stair(_OrientedRoom):
    room_type = 'vertical'

    def __init__(self, world, xmap, pos, orientation='+x'):
        self.pos = pos
        self.orientation = orientation
        self.xmap = xmap
        self.light()

        wall(world, '-z', SIZE, pos)

        if orientation == '+x':
            wall(world, '-x', SIZE, pos)
            cube_s(world, 4, mv(pos, (0, 2, 0)), tex=3)
        elif orientation == '-x':
            wall(world, '+x', SIZE, pos)
            cube_s(world, 4, mv(pos, (SIZE / 2, 2, 0)), tex=3)
        elif orientation == '+y':
            wall(world, '-y', SIZE, pos)
            cube_s(world, 4, mv(pos, (2, 0, 0)), tex=3)
        elif orientation == '-y':
            wall(world, '+y', SIZE, pos)
            cube_s(world, 4, mv(pos, (2, SIZE / 2, 0)), tex=3)
        else:
            raise Exception("Unknown orientation %s" % orientation)

    def get_doorways(self):
        if self.orientation == '+x':
            return [
                mv(self.pos, m(1, 0, 0)),
                mv(self.pos, m(-1, 0, 1))
            ]
        elif self.orientation == '-x':
            return [
                mv(self.pos, m(1, 0, 1)),
                mv(self.pos, m(-1, 0, 0))
            ]
        elif self.orientation == '+y':
            return [
                mv(self.pos, m(0, 1, 0)),
                mv(self.pos, m(0, -1, 1))
            ]
        elif self.orientation == '-y':
            return [
                mv(self.pos, m(0, 1, 1)),
                mv(self.pos, m(0, -1, 0))
            ]
        return []

    def get_positions(self):
        return [
            self.pos, # Self
            mv(self.pos, m(0, 0, 1)) # Above self
        ]

    @classmethod
    def get_transition_probs(cls):
        return {
            'platform': 0.1,
            'hallway': 0.4,
            'vertical': 10.7,
        }
