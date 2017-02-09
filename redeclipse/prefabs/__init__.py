from redeclipse.objects import cube
from redeclipse.entities import Light, PlayerSpawn, Pusher
from redeclipse.entities.model import MapModel
from redeclipse.prefabs.construction_kit import wall, column, wall_points, mv, \
    m, mi, low_wall, cube_s, rectangular_prism
import random # noqa
import noise
import colorsys
random.seed(22)
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

    def get_offset(self):
        # This should be inverse of FIRST get_doorways entry.
        return m(1, 0, 0)

    def _get_doorways(self):
        return [
            m(-1, 0, 0),
            m(0, -1, 0),
            m(1, 0, 0),
            m(0, 1, 0)
        ]

    def get_offset(self):
        # This should be inverse of FIRST get_doorways entry.
        return self._get_doorways()[0]
        # return mi(self._get_doorways()[0])

    def get_doorways(self):
        return [
            mv(self.pos, q) for q in self._get_doorways()
        ]

    def get_positions(self):
        return [self.pos]

    @classmethod
    def get_transition_probs(cls):
        # Platform
        return {
            'platform': 0.1,
            'platform_setpiece': 0.1,
            'hallway': 0.8,
            'vertical': 0.4,
            'hallway_jump': 0.2,
        }


    def light(self, xmap):
        # 70% chance of a light below
        # if random.random() < 0.7:
        if True:
            if hasattr(self, 'size'):
                size = self.size
            else:
                size = SIZE

            # Map to 0-1 scale
            nums = list(map(
                lambda x: x * (2 ** -7.5),
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
            xmap.ents.append(light)

class _OrientedRoom(_Room):
    def _get_doorways(self):
        if self.orientation in ('+x', '-x'):
            return [
                m(-1, 0, 0),
                m(1, 0, 0),
            ]
        else:
            return [
                m(0, 1, 0),
                m(0, -1, 0)
            ]

    @classmethod
    def get_transition_probs(cls):
        # oriented platform / hallway
        return {
            'hallway': 0.4,
            'platform_setpiece': 0.1,
            'platform': 0.3,
            'vertical': 0.6,
            'hallway_jump': 0.6,
        }

class _3X3Room(_Room):

    def _get_doorways(self):
        return [
            m(-2, 0, 0),
            m(2, 0, 0),
            m(0, -2, 0),
            m(0, 2, 0),
        ]

    def get_positions(self):
        return [
            mv(self.pos , m(-1 , -1 , 0)) ,
            mv(self.pos , m(-1 , 0  , 0)) ,
            mv(self.pos , m(-1 , 1  , 0)) ,
            mv(self.pos , m(0  , -1 , 0)) ,
            mv(self.pos , m(0  , 0  , 0)) ,
            mv(self.pos , m(0  , 1  , 0)) ,
            mv(self.pos , m(1  , -1 , 0)) ,
            mv(self.pos , m(1  , 0  , 0)) ,
            mv(self.pos , m(1  , 1  , 0)) ,
        ]



class BaseRoom(_Room):

    def __init__(self, pos, tex=2, orientation=None):
        self.pos = pos
        self.tex = tex
        self.orientation = orientation

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=self.tex)
        wall(world, '+z', SIZE, self.pos, tex=self.tex)

        # Add default spawn in base room  (so camera dosen't spawn in
        # miles above where we want to be)
        spawn = PlayerSpawn(
            x=8 * (self.pos[0] + SIZE / 2),
            y=8 * (self.pos[1] + SIZE / 2),
            z=8 * (self.pos[2] + 1),
        )
        xmap.ents.append(spawn)
        self.light(xmap)


class NLongCorridor(_OrientedRoom):
    room_type = 'hallway'

    def __init__(self, pos, orientation='+x', roof=False, length=2, tex=7):
        self.orientation = orientation
        self.roof = roof
        self.length = length
        self.pos = pos
        self.tex = tex
        # self.pos = mv(pos, self.get_offset())
        # print(pos, '+', self.get_offset(), '(' , self.orientation,') =>', self.pos, '==', self.get_positions(), self.get_doorways())

        if self.length == 0:
            raise Exception("Must have length")

    def render(self, world, xmap):
        # First tile
        wall(world, '-z', SIZE, self.pos, tex=self.tex)

        for i in range(1, self.length):
            if self.orientation == '-x':
                wall(world, '-z', SIZE, mv(self.pos, m(i, 0, 0)), tex=self.tex)
            elif self.orientation == '+x':
                wall(world, '-z', SIZE, mv(self.pos, m(-i, 0, 0)), tex=self.tex)
            elif self.orientation == '-y':
                wall(world, '-z', SIZE, mv(self.pos, m(0, i, 0)), tex=self.tex)
            elif self.orientation == '+y':
                wall(world, '-z', SIZE, mv(self.pos, m(0, -i, 0)), tex=self.tex)
            else:
                raise Exception("Unknown Orientation")
        self.light(xmap)

    def get_positions(self):
        positions = [self.pos]

        # Same logic as init
        for i in range(1, self.length):
            if self.orientation == '-x':
                positions.append(mv(self.pos, m(i, 0, 0)))
            elif self.orientation == '+x':
                positions.append(mv(self.pos, m(-i, 0, 0)))
            elif self.orientation == '-y':
                positions.append(mv(self.pos, m(0, i, 0)))
            elif self.orientation == '+y':
                positions.append(mv(self.pos, m(0, -i, 0)))
            else:
                raise Exception("Unknown Orientation")
        return positions

    def _get_doorways(self):
        if self.orientation == '+x':
            return [
                m(1, 0, 0),
                m(-self.length, 0, 0),
            ]
        elif self.orientation == '-x':
            return [
                m(-1, 0, 0),
                m(self.length, 0, 0),
            ]
        elif self.orientation == '+y':
            return [
                m(0, 1, 0),
                m(0, -self.length, 0),
            ]
        elif self.orientation == '-y':
            return [
                m(0, -1, 0),
                m(0, self.length, 0),
            ]
        else:
            raise Exception("Unknown Orientation")


class Corridor2way(_OrientedRoom):
    room_type = 'hallway'

    def __init__(self, pos, orientation='+x', roof=False, tex=2):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof
        self.tex = tex

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=self.tex)
        if self.roof:
            wall(world, '+z', SIZE, self.pos, tex=self.tex)

        if self.orientation in ('+x', '-x'):
            wall(world, '+y', SIZE, self.pos, tex=self.tex)
            wall(world, '-y', SIZE, self.pos, tex=self.tex)
        else:
            wall(world, '+x', SIZE, self.pos, tex=self.tex)
            wall(world, '-x', SIZE, self.pos, tex=self.tex)

        self.light(xmap)


class JumpCorridor3(_OrientedRoom):
    room_type = 'hallway_jump'

    @classmethod
    def get_transition_probs(cls):
        return {
            'hallway_jump': 0,
            'platform': 0.3,
            'platform_setpiece': 0.1,
            'hallway': 0.5,
            'vertical': 0.4,
        }

    def __init__(self, pos, orientation='+x', roof=False, tex=2):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof
        self.tex = tex

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=self.tex)
        pusher_a = None
        pusher_b = None

        (a, b, c) = self.pos
        if self.orientation == '-x':
            wall(world, '-z', SIZE, mv(self.pos, m(2, 0, 0)), tex=self.tex)
            rectangular_prism(world, 2, 4, 1, (a + 6, b + 2, c), tex=self.tex + 1)
            pusher_a = Pusher(
                x=8 * (self.pos[0] + 7),
                y=8 * (self.pos[1] + 4),
                z=8 * (self.pos[2] + 1),
                maxrad=15,
                yaw=270,
                force=175,
            )
        elif self.orientation == '+x':
            wall(world, '-z', SIZE, mv(self.pos, m(-2, 0, 0)), tex=self.tex)
            rectangular_prism(world, 2, 4, 1, (a, b + 2, c), tex=self.tex + 1)
            pusher_a = Pusher(
                x=8 * (self.pos[0] + 1),
                y=8 * (self.pos[1] + 4),
                z=8 * (self.pos[2] + 1),
                maxrad=15,
                yaw=90,
                force=175,
            )
        elif self.orientation == '-y':
            wall(world, '-z', SIZE, mv(self.pos, m(0, 2, 0)), tex=self.tex)
            rectangular_prism(world, 4, 2, 1, (a + 2, b + 6, c), tex=self.tex + 1)
            pusher_a = Pusher(
                x=8 * (self.pos[0] + 4),
                y=8 * (self.pos[1] + 7),
                z=8 * (self.pos[2] + 1),
                maxrad=15,
                yaw=0,
                force=175,
            )
        elif self.orientation == '+y':
            wall(world, '-z', SIZE, mv(self.pos, m(0, -2, 0)), tex=self.tex)
            rectangular_prism(world, 4, 2, 1, (a + 2, b, c), tex=self.tex + 1)
            pusher_a = Pusher(
                x=8 * (self.pos[0] + 4),
                y=8 * (self.pos[1] + 1),
                z=8 * (self.pos[2] + 1),
                maxrad=15,
                yaw=180,
                force=175,
            )

        if self.orientation in ('+x', '-x'):
            low_wall(world, '+y', SIZE, self.pos)
            low_wall(world, '-y', SIZE, self.pos)
            if self.orientation == '-x':
                low_wall(world, '+y', SIZE, mv(self.pos, m(2, 0, 0)))
                low_wall(world, '-y', SIZE, mv(self.pos, m(2, 0, 0)))
                (a, b, c) = mv(self.pos, m(2, 0, 0))
                rectangular_prism(world, 2, 4, 1, (a, b + 2, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    x=8 * (a + 1),
                    y=8 * (b + 4),
                    z=8 * (c + 1),
                    maxrad=15,
                    yaw=90,
                    force=175,
                )
            else:
                low_wall(world, '+y', SIZE, mv(self.pos, m(-2, 0, 0)))
                low_wall(world, '-y', SIZE, mv(self.pos, m(-2, 0, 0)))
                (a, b, c) = mv(self.pos, m(-2, 0, 0))
                rectangular_prism(world, 2, 4, 1, (a + 6, b + 2, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    x=8 * (a + 7),
                    y=8 * (b + 4),
                    z=8 * (c + 1),
                    maxrad=15,
                    yaw=270,
                    force=175,
                )
        else:
            low_wall(world, '+x', SIZE, self.pos)
            low_wall(world, '-x', SIZE, self.pos)

            if self.orientation == '-y':
                low_wall(world, '+x', SIZE, mv(self.pos, m(0, 2, 0)))
                low_wall(world, '-x', SIZE, mv(self.pos, m(0, 2, 0)))
                (a, b, c) = mv(self.pos, m(0, 2, 0))
                rectangular_prism(world, 4, 2, 1, (a + 2, b, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    x=8 * (a + 4),
                    y=8 * (b + 1),
                    z=8 * (c + 1),
                    maxrad=15,
                    yaw=180,
                    force=175,
                )
            else:
                low_wall(world, '+x', SIZE, mv(self.pos, m(0, -2, 0)))
                low_wall(world, '-x', SIZE, mv(self.pos, m(0, -2, 0)))
                (a, b, c) = mv(self.pos, m(0, -2, 0))
                rectangular_prism(world, 4, 2, 1, (a + 2, b + 6, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    x=8 * (a + 4),
                    y=8 * (b + 7),
                    z=8 * (c + 1),
                    maxrad=15,
                    yaw=0,
                    force=175,
                )

        xmap.ents.append(pusher_a)
        xmap.ents.append(pusher_b)

    def get_positions(self):
        positions = [self.pos]
        for i in range(1, 3):
            if self.orientation == '-x':
                positions.append(mv(self.pos, m(i, 0, 0)))
            elif self.orientation == '+x':
                positions.append(mv(self.pos, m(-i, 0, 0)))
            elif self.orientation == '-y':
                positions.append(mv(self.pos, m(0, i, 0)))
            elif self.orientation == '+y':
                positions.append(mv(self.pos, m(0, -i, 0)))
            else:
                raise Exception("Unknown Orientation")
        return positions

    def _get_doorways(self):
        if self.orientation == '+x':
            return [
                m(1, 0, 0),
                m(-3, 0, 0),
            ]
        elif self.orientation == '-x':
            return [
                m(-1, 0, 0),
                m(3, 0, 0),
            ]
        elif self.orientation == '+y':
            return [
                m(0, 1, 0),
                m(0, -3, 0),
            ]
        elif self.orientation == '-y':
            return [
                m(0, -1, 0),
                m(0, 3, 0),
            ]
        else:
            raise Exception("Unknown Orientation")


class Corridor2way_A(Corridor2way):
    room_type = 'hallway'

    def __init__(self, pos, orientation='+x', roof=False):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos)
        if self.roof:
            wall(world, '+z', SIZE, self.pos)

        if self.orientation in ('+x', '-x'):
            low_wall(world, '+y', SIZE, self.pos)
            low_wall(world, '-y', SIZE, self.pos)
        else:
            low_wall(world, '+x', SIZE, self.pos)
            low_wall(world, '-x', SIZE, self.pos)
        self.light(xmap)


class Corridor4way(_Room):
    room_type = 'hallway'

    def __init__(self, pos, roof=False, orientation=None, tex=2):
        self.pos = pos
        self.roof = roof
        self.tex = tex

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos)
        if self.roof:
            wall(world, '+z', SIZE, self.pos)

        column(world, 'z', 8, mv(self.pos, (0, 0, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (SIZE - 1, SIZE - 1, 0)), tex=4)

        self.light(xmap)


class Corridor4way_A(Corridor4way):
    room_type = 'hallway'

    def __init__(self, pos, roof=None, orientation=None, tex=2):
        self.pos = pos
        self.roof = roof
        self.tex = tex

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos)

        column(world, 'z', 2, mv(self.pos, (0, 0, 0)), tex=4)
        column(world, 'z', 2, mv(self.pos, (0, SIZE - 1, 0)), tex=4)
        column(world, 'z', 2, mv(self.pos, (SIZE - 1, 0, 0)), tex=4)
        column(world, 'z', 2, mv(self.pos, (SIZE - 1, SIZE - 1, 0)), tex=4)
        self.light(xmap)


class SpawnRoom(_OrientedRoom):
    room_type = 'platform_setpiece'

    def __init__(self, pos, roof=None, orientation='+x'):
        self.pos = pos
        self.orientation = orientation
        self.tex = 9

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=self.tex)
        wall(world, '+z', SIZE, self.pos, tex=self.tex)

        if self.orientation == '+x':
            wall(world, '-x', SIZE, self.pos)
            wall(world, '+y', SIZE, self.pos)
            wall(world, '-y', SIZE, self.pos)
        elif self.orientation == '-x':
            wall(world, '+x', SIZE, self.pos)
            wall(world, '+y', SIZE, self.pos)
            wall(world, '-y', SIZE, self.pos)
        elif self.orientation == '+y':
            wall(world, '-y', SIZE, self.pos)
            wall(world, '+x', SIZE, self.pos)
            wall(world, '-x', SIZE, self.pos)
        elif self.orientation == '-y':
            wall(world, '+y', SIZE, self.pos)
            wall(world, '+x', SIZE, self.pos)
            wall(world, '-x', SIZE, self.pos)
        else:
            raise Exception("Unknown orientation %s" % self.orientation)

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

    def _get_doorways(self):
        if self.orientation == '+x':
            return [m(1, 0, 0)]
        elif self.orientation == '-x':
            return [m(-1, 0, 0)]
        if self.orientation == '+y':
            return [m(0, 1, 0)]
        elif self.orientation == '-y':
            return [m(0, -1, 0)]


class AltarRoom(_3X3Room):
    room_type = 'platform_setpiece'

    def __init__(self, pos, roof=False, orientation=None):
        # Push the position
        self.orientation = orientation
        # We (arbitrarily) define pos as the middle of one side.
        self.pos = pos
        # We move it once, in orientation in order to re-center the room?
        if self.orientation == '+x':
            self.pos = mv(self.pos, m(-1, 0, 0))
        elif self.orientation == '-x':
            self.pos = mv(self.pos, m(1, 0, 0))
        elif self.orientation == '+y':
            self.pos = mv(self.pos, m(0, -1, 0))
        elif self.orientation == '-y':
            self.pos = mv(self.pos, m(0, 1, 0))
        # For bigger rooms, we have to shift them such that the previous_posision matches a doorway.


    def render(self, world, xmap):
        self.light(xmap)
        # size = 24
        wall(world, '-z', SIZE, self.pos)
        # 4 corners
        wall(world, '-z', SIZE, mv(self.pos, m(1, 1, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(1, -1, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(-1, 1, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(-1, -1, 0)))
        # 4 middle pieces
        wall(world, '-z', SIZE, mv(self.pos, m(1, 0, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(-1, 0, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(0, 1, 0)))
        wall(world, '-z', SIZE, mv(self.pos, m(0, -1, 0)))

        column(world, 'z', 8, mv(self.pos, (15, 15, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (-8, 15, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (15, -8, 0)), tex=4)
        column(world, 'z', 8, mv(self.pos, (-8, -8, 0)), tex=4)

        wall(world, '-z', 16, mv(self.pos, (-4, -4, 1)), tex=5)
        wall(world, '-z', 12, mv(self.pos, (-2, -2, 2)), tex=6)

        Ring.render(world, mv(self.pos, (-4, -4, 7)), size=16, tex=7, thickness=2)

        tree = MapModel(
            x=8 * (self.pos[0] + 4),
            y=8 * (self.pos[1] + 4),
            z=8 * (self.pos[2] + 3),
            type=124
        )
        xmap.ents.append(tree)

    def get_positions(self):
        return [
            mv(self.pos , m(-1 , -1 , 0)) ,
            mv(self.pos , m(-1 , 0  , 0)) ,
            mv(self.pos , m(-1 , 1  , 0)) ,
            mv(self.pos , m(0  , -1 , 0)) ,
            mv(self.pos , m(0  , 0  , 0)) ,
            mv(self.pos , m(0  , 1  , 0)) ,
            mv(self.pos , m(1  , -1 , 0)) ,
            mv(self.pos , m(1  , 0  , 0)) ,
            mv(self.pos , m(1  , 1  , 0)) ,
            mv(self.pos , m(-1 , -1 , 1)) ,
            mv(self.pos , m(-1 , 0  , 1)) ,
            mv(self.pos , m(-1 , 1  , 1)) ,
            mv(self.pos , m(0  , -1 , 1)) ,
            mv(self.pos , m(0  , 0  , 1)) ,
            mv(self.pos , m(0  , 1  , 1)) ,
            mv(self.pos , m(1  , -1 , 1)) ,
            mv(self.pos , m(1  , 0  , 1)) ,
            mv(self.pos , m(1  , 1  , 1)) ,
        ]

    def light(self, xmap):
        light = Light(
            x=8 * (self.pos[0] + 8),
            y=8 * (self.pos[1] + 8),
            # Light above head
            z=8 * (self.pos[2] + 7),
            red=255,
            green=255,
            blue=255,
            radius=128,
        )
        xmap.ents.append(light)


class Stair(_OrientedRoom):
    room_type = 'vertical'

    def __init__(self, pos, orientation='+x'):
        self.pos = pos
        self.orientation = orientation

    def render(self, world, xmap):
        self.light(xmap)
        wall(world, '-z', SIZE, self.pos)

        pusher_kw = {}
        if self.orientation == '+x':
            wall(world, '-x', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (0, 2, 0)), tex=3)
            pusher_kw = {
                'x': 8 * (self.pos[0] + 5),
                'y': 8 * (self.pos[1] + 4),
                'z': 8 * (self.pos[2] + 2),
                'yaw': 90,
            }
        elif self.orientation == '-x':
            wall(world, '+x', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (SIZE / 2, 2, 0)), tex=3)
            pusher_kw = {
                'x': 8 * (self.pos[0] + 3),
                'y': 8 * (self.pos[1] + 4),
                'z': 8 * (self.pos[2] + 2),
                'yaw': 270,
            }
        elif self.orientation == '+y':
            wall(world, '-y', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (2, 0, 0)), tex=3)
            pusher_kw = {
                'x': 8 * (self.pos[0] + 4),
                'y': 8 * (self.pos[1] + 5),
                'z': 8 * (self.pos[2] + 2),
                'yaw': 180,
            }
        elif self.orientation == '-y':
            wall(world, '+y', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (2, SIZE / 2, 0)), tex=3)
            pusher_kw = {
                'x': 8 * (self.pos[0] + 4),
                'y': 8 * (self.pos[1] + 3),
                'z': 8 * (self.pos[2] + 2),
                'yaw': 0,
            }
        else:
            raise Exception("Unknown orientation %s" % self.orientation)

        pusher = Pusher(
            maxrad=15,
            force=250,
            pitch=66,
            **pusher_kw
        )
        xmap.ents.append(pusher)

    def _get_doorways(self):
        if self.orientation == '+x':
            return [
                m(1, 0, 0),
                m(-1, 0, 1),
            ]
        elif self.orientation == '-x':
            return [
                m(1, 0, 1),
                m(-1, 0, 0),
            ]
        elif self.orientation == '+y':
            return [
                m(0, 1, 0),
                m(0, -1, 1),
            ]
        elif self.orientation == '-y':
            return [
                m(0, 1, 1),
                m(0, -1, 0),
            ]
        return []

    def get_positions(self):
        return [
            self.pos, # Self
            mv(self.pos, m(0, 0, 1)) # Above self
        ]

    @classmethod
    def get_transition_probs(cls):
        # stair
        return {
            'platform': 0.5,
            'platform_setpiece': 0.2,
            'hallway': 0.4,
            'vertical': 0.6,
            'hallway_jump': 0.2,
        }
