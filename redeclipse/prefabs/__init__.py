from redeclipse.entities import Light, PlayerSpawn, Pusher
from redeclipse.entities.model import MapModel
from redeclipse.entities.weapon import Grenade
from redeclipse.prefabs.construction_kit import wall, column, mv, \
    m, low_wall, cube_s, rectangular_prism, ring, multi_wall, rotate, rotate_a, faded_wall
import random # noqa
import noise
import copy
import colorsys
random.seed(22)
SIZE = 8
_BUILTIN_SIZE = 2 ** 7
_REAL_SIZE = 2 ** 8
SIZE_OFFSET = _BUILTIN_SIZE / _REAL_SIZE


def posColor(pos):
    nums = list(map(
        lambda x: x * (2 ** -8.4),
        pos
    ))

    # convert a tuple of three nums (x,y,z) + offset into a
    # 0-255 integer.
    def kleur(nums, base):
        return int(abs(noise.pnoise3(*nums, base=base)) * 255)

    # Now we generate our colour:
    r = kleur(nums, 10)
    g = kleur(nums, 0)
    b = kleur(nums, 43)

    # RGB isn't great, because it means low values of RGB are
    # low luminance. So we convert to HSV to get pure hue
    (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
    # We then peg S and V to high and only retain hue
    (r, g, b) = colorsys.hsv_to_rgb(h, 1, 255)
    # This should give us a bright colour on a continuous range
    return (int(r), int(g), int(b))

def positionColour(pos, size):
    (r, g, b) = posColor(pos)

    return Light(
        # Center the light in the unit, x&y
        xyz=m(
            SIZE_OFFSET * (pos[0] + size / 2),
            SIZE_OFFSET * (pos[1] + size / 2),
            # Light above player head height
            SIZE_OFFSET * (pos[2] + 4),
        ),
        # Colours
        red=r,
        green=g,
        blue=b,
        # Make it a relatively small light, nice intimate feel without
        # washing out.
        radius=SIZE_OFFSET * 64,
    )


class _Room:
    """Base 'room' class which all other room types inherit from
    """
    room_type = 'platform'

    @classmethod
    def get_transition_probs(cls):
        """Probabilities of transitioning to other named room types"""
        # Platform
        return {
            'platform': 0.1,
            'platform_setpiece': 0,
            'vertical': 0.3,
            'hallway': 0.8,
            'hallway_jump': 0.4,
        }

    def _get_doorways(self):
        """
        Return the set of possible doorways as offsets to self.pos. DO NOT include self.pos
        """
        return [
            m(-1, 0, 0),
            m(0, -1, 0),
            m(1, 0, 0),
            m(0, 1, 0)
        ]

    def get_offset(self):
        """get_offset is used to obtain the shift required with non 1x1 units
        """
        # This should be inverse of FIRST get_doorways entry.
        return self._get_doorways()[0]
        # return mi(self._get_doorways()[0])

    def get_doorways(self):
        """The get_doorways function that most things actually use, which applies the offset.

        This mostly means that you only need to override _get_doorways with
        your doorways. Everyone will call this and have access to shifted
        values.
        """
        return [
            mv(self.pos, q) for q in self._get_doorways()
        ]

    def get_positions(self):
        """Positions occupied by this unit"""
        return [self.pos]

    @classmethod
    def randOpts(cls, prev):
        # Get the number of "flags" we can flip on a given room.
        if hasattr(cls, '_randflags'):
            number_of_options = len(cls._randflags)
        else:
            return {}

        # If the same class, only permit mutating ONE attribute.
        if cls == prev.__class__:
            mutatedOpts = copy.deepcopy(prev._randflags)
            mutateIdx = random.randint(0, len(mutatedOpts) - 1)
            # Toggle that value.
            mutatedOpts[mutateIdx] = not mutatedOpts[mutateIdx]
            return {'randflags': mutatedOpts}
        else:
            # From this, now generate a random set of T/F variables
            opts = []
            for i in range(number_of_options):
                opts.append(random.uniform(0, 1) > 0.5)

            return {'randflags': opts}

    def light(self, xmap):
        """Function which applies light entities to the unit."""
        # If there is self.size, use that. Otherwise use default of 8.
        if hasattr(self, 'size'):
            size = self.size
        else:
            size = SIZE

        light = positionColour(self.pos, size)
        # Map (x, y, z) to 0-1 scale
        xmap.ents.append(light)


class _OrientedRoom(_Room):
    """A special case of base _Room, a class which has different behaviour
    based on its orientation.
    """

    @classmethod
    def get_transition_probs(cls):
        # oriented platform / hallway
        return {
            'hallway': 2.3,
            'hallway_jump': 0.8,
            'platform_setpiece': 0.2,
            'platform': 0.6,
            'vertical': 0.3,
        }

    def _get_doorways(self):
        """Doorways out of two axes"""
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


class _3X3Room(_Room):
    """Another special case of room, though this probably does not need to be.
    AltarRoom is currently the only user."""
    room_type = 'platform_setpiece'

    @classmethod
    def get_transition_probs(cls):
        """Probabilities of transitioning to other named room types"""
        # Platform
        return {
            'platform': 0.1,
            'platform_setpiece': 0,
            'vertical': 0.3,
            'hallway': 1.8,
            'hallway_jump': 0.4,
        }

    def __init__(self, pos, tex=2, orientation=None, randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = pos
        self.tex = tex
        self.orientation = orientation

    def _get_doorways(self):
        return [
            m(-2, 0, 0),
            m(2, 0, 0),
            m(0, -2, 0),
            m(0, 2, 0),
        ]

    def get_positions(self):
        return [
            mv(self.pos, m(-1, -1, 0)),
            mv(self.pos, m(-1, 0, 0)),
            mv(self.pos, m(-1, 1, 0)),
            mv(self.pos, m(0, -1, 0)),
            mv(self.pos, m(0, 0, 0)),
            mv(self.pos, m(0, 1, 0)),
            mv(self.pos, m(1, -1, 0)),
            mv(self.pos, m(1, 0, 0)),
            mv(self.pos, m(1, 1, 0)),

            # Do not place things above us
            mv(self.pos, m(-1, -1, 1)),
            mv(self.pos, m(-1, 0, 1)),
            mv(self.pos, m(-1, 1, 1)),
            mv(self.pos, m(0, -1, 1)),
            mv(self.pos, m(0, 0, 1)),
            mv(self.pos, m(0, 1, 1)),
            mv(self.pos, m(1, -1, 1)),
            mv(self.pos, m(1, 0, 1)),
            mv(self.pos, m(1, 1, 1)),
        ]


class BaseRoom(_Room):
    """First real 'room' class."""

    def __init__(self, pos, tex=2, orientation=None, randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = pos
        self.tex = tex
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))
        wall(world, '+z', SIZE, self.pos, tex=self.tex)

        # Add default spawn in base room  (so camera dosen't spawn in
        # miles above where we want to be)
        spawn = PlayerSpawn(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + SIZE / 2),
                SIZE_OFFSET * (self.pos[1] + SIZE / 2),
                SIZE_OFFSET * (self.pos[2] + 1),
            )
        )
        xmap.ents.append(spawn)
        self.light(xmap)


class TestRoom(_Room):
    def __init__(self, pos, tex=2, orientation=None, randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = pos
        self.tex = tex
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        g = Grenade(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + SIZE / 2),
                SIZE_OFFSET * (self.pos[1] + SIZE / 2),
                SIZE_OFFSET * (self.pos[2] + 1),
            )
        )
        xmap.ents.append(g)


class NLongCorridor(_OrientedRoom):
    room_type = 'hallway'
    _randflags = (
        True, # roof
        True, # A
        True, # B; length=a<<1 | b
    )

    def __init__(self, pos, orientation='+x', tex=7, randflags=None):
        self.orientation = orientation
        self.pos = pos
        self.tex = tex
        # self.pos = mv(pos, self.get_offset())
        # print(pos, '+', self.get_offset(), '(' , self.orientation,') =>', self.pos, '==', self.get_positions(), self.get_doorways())
        if randflags:
            self._randflags = randflags

        la = 1 if self._randflags[1] else 0
        lb = 1 if self._randflags[1] else 0
        self.length = 1 + (la << 1 | lb)

    def render(self, world, xmap):
        # First tile
        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))

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
    _randflags = (
        True, # roof
        True, # no wall / low wall
    )

    def __init__(self, pos, orientation='+x', tex=2, randflags=None):
        self.pos = pos
        self.orientation = orientation
        self.tex = tex
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.light(xmap)

        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))
        if self._randflags[0]:
            wall(world, '+z', SIZE, self.pos, tex=self.tex)

        if self._randflags[1]:
            if self.orientation in ('+x', '-x'):
                wall(world, '+y', 2, self.pos, tex=self.tex)
                wall(world, '-y', 2, self.pos, tex=self.tex)
            else:
                wall(world, '+x', 2, self.pos, tex=self.tex)
                wall(world, '-x', 2, self.pos, tex=self.tex)


class JumpCorridor3(_OrientedRoom):
    room_type = 'hallway_jump'

    @classmethod
    def get_transition_probs(cls):
        return {
            'hallway_jump': 0,
            'platform': 0.6,
            'platform_setpiece': 0.1,
            'hallway': 0.6,
            'vertical': 0.2,
        }

    def __init__(self, pos, orientation='+x', tex=2, randflags=None):
        self.pos = pos
        self.orientation = orientation
        self.tex = tex
        if randflags:
            self._randflags = randflags

    def light(self, xmap):
        if hasattr(self, 'size'):
            size = self.size
        else:
            size = SIZE

        poss = self.get_positions()
        xmap.ents.append(positionColour(poss[0], size))
        xmap.ents.append(positionColour(poss[2], size))

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))
        pusher_a = None
        pusher_b = None
        self.light(xmap)

        (a, b, c) = self.pos
        if self.orientation == '-x':
            wall(world, '-z', SIZE, mv(self.pos, m(2, 0, 0)), tex=self.tex)
            rectangular_prism(world, 2, 4, 1, (a + 6, b + 2, c), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 7),
                    SIZE_OFFSET * (self.pos[1] + 4),
                    SIZE_OFFSET * (self.pos[2] + 1),
                ),
                maxrad=15 * SIZE_OFFSET,
                yaw=270,
                force=175 * SIZE_OFFSET,
            )
        elif self.orientation == '+x':
            wall(world, '-z', SIZE, mv(self.pos, m(-2, 0, 0)), tex=self.tex)
            rectangular_prism(world, 2, 4, 1, (a, b + 2, c), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 1),
                    SIZE_OFFSET * (self.pos[1] + 4),
                    SIZE_OFFSET * (self.pos[2] + 1),
                ),
                maxrad=15 * SIZE_OFFSET,
                yaw=90,
                force=175 * SIZE_OFFSET,
            )
        elif self.orientation == '-y':
            wall(world, '-z', SIZE, mv(self.pos, m(0, 2, 0)), tex=self.tex)
            rectangular_prism(world, 4, 2, 1, (a + 2, b + 6, c), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 4),
                    SIZE_OFFSET * (self.pos[1] + 7),
                    SIZE_OFFSET * (self.pos[2] + 1),
                ),
                maxrad=15 * SIZE_OFFSET,
                yaw=0,
                force=175 * SIZE_OFFSET,
            )
        elif self.orientation == '+y':
            wall(world, '-z', SIZE, mv(self.pos, m(0, -2, 0)), tex=self.tex)
            rectangular_prism(world, 4, 2, 1, (a + 2, b, c), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 4),
                    SIZE_OFFSET * (self.pos[1] + 1),
                    SIZE_OFFSET * (self.pos[2] + 1),
                ),
                maxrad=15 * SIZE_OFFSET,
                yaw=180,
                force=175 * SIZE_OFFSET,
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
                    xyz=m(
                        SIZE_OFFSET * (a + 1),
                        SIZE_OFFSET * (b + 4),
                        SIZE_OFFSET * (c + 1),
                    ),
                    maxrad=15 * SIZE_OFFSET,
                    yaw=90,
                    force=175 * SIZE_OFFSET,
                )
            else:
                low_wall(world, '+y', SIZE, mv(self.pos, m(-2, 0, 0)))
                low_wall(world, '-y', SIZE, mv(self.pos, m(-2, 0, 0)))
                (a, b, c) = mv(self.pos, m(-2, 0, 0))
                rectangular_prism(world, 2, 4, 1, (a + 6, b + 2, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    xyz=m(
                        SIZE_OFFSET * (a + 7),
                        SIZE_OFFSET * (b + 4),
                        SIZE_OFFSET * (c + 1),
                    ),
                    maxrad=15 * SIZE_OFFSET,
                    yaw=270,
                    force=175 * SIZE_OFFSET,
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
                    xyz=m(
                        SIZE_OFFSET * (a + 4),
                        SIZE_OFFSET * (b + 1),
                        SIZE_OFFSET * (c + 1),
                    ),
                    maxrad=15 * SIZE_OFFSET,
                    yaw=180,
                    force=175 * SIZE_OFFSET,
                )
            else:
                low_wall(world, '+x', SIZE, mv(self.pos, m(0, -2, 0)))
                low_wall(world, '-x', SIZE, mv(self.pos, m(0, -2, 0)))
                (a, b, c) = mv(self.pos, m(0, -2, 0))
                rectangular_prism(world, 4, 2, 1, (a + 2, b + 6, c), tex=self.tex + 1)
                pusher_b = Pusher(
                    xyz=m(
                        SIZE_OFFSET * (a + 4),
                        SIZE_OFFSET * (b + 7),
                        SIZE_OFFSET * (c + 1),
                    ),
                    maxrad=15 * SIZE_OFFSET,
                    yaw=0,
                    force=175 * SIZE_OFFSET,
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


class JumpCorridorVertical(_OrientedRoom):
    room_type = 'vertical'
    _randflags = (
        True, # extra section
    )

    @classmethod
    def get_transition_probs(cls):
        return {
            'hallway_jump': 0.2,
            'platform': 0.3,
            'platform_setpiece': 0.1,
            'hallway': 0.9,
            'vertical': 0.1,
        }

    def _get_doorways(self):
        if self.orientation == '-x':
            return [
                m(1, 0, 0),
                m(-1, 0, 2),
            ]
        elif self.orientation == '+x':
            return [
                m(-1, 0, 0),
                m(1, 0, 2),
            ]
        if self.orientation == '-y':
            return [
                m(0, 1, 0),
                m(0, -1, 2),
            ]
        if self.orientation == '+y':
            return [
                m(0, -1, 0),
                m(0, 1, 2),
            ]

    def __init__(self, pos, orientation='+x', roof=False, tex=2, randflags=None):
        self.pos = pos
        self.orientation = orientation
        self.roof = roof
        self.tex = tex
        if randflags:
            self._randflags = randflags

    def light(self, xmap):
        xmap.ents.append(positionColour(
            mv(self.pos, m(0, 0, 1)), SIZE))

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))
        wall(world, '+z', SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
        self.light(xmap)

        (a, b, c) = self.pos
        if self.orientation == '-x':
            #Walls
            multi_wall(world, ('+x', '+y', '-y'), SIZE, self.pos, tex=self.tex)
            multi_wall(world, ('-x', '+x', '+y', '-y'), SIZE, mv(self.pos, m(0, 0, 1)), tex=self.tex)
            multi_wall(world, ('+x', '+y', '-y'), SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
            column(world, 'y', 8, mv(self.pos, m(0, 0, 2)), tex=4)
            # Red markers
            rectangular_prism(world, 2, 4, 1, (a + 4, b + 2, c), tex=self.tex + 1)
            rectangular_prism(world, 1, 4, 2, (a + 7, b + 2, c + 12), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(a + 5, b + 4, c + 1, size=SIZE * SIZE_OFFSET),
                pitch=74,
                yaw=270,
                force=400 * SIZE_OFFSET,
            )

            pusher_b = Pusher(
                xyz=m(a + 6, b + 4, c + 15 + (2 if SIZE_OFFSET == 0.5 else 0), size=SIZE * SIZE_OFFSET),
                pitch=40,
                yaw=90,
                force=200 * SIZE_OFFSET,
            )
        elif self.orientation == '+x':
            #Walls
            multi_wall(world, ('-x', '+y', '-y'), SIZE, self.pos, tex=self.tex)
            multi_wall(world, ('-x', '+x', '+y', '-y'), SIZE, mv(self.pos, m(0, 0, 1)), tex=self.tex)
            multi_wall(world, ('-x', '+y', '-y'), SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
            column(world, 'y', 8, mv(self.pos, m(7/8, 0, 2)), tex=4)
            # Red markers
            rectangular_prism(world, 2, 4, 1, (a + 2, b + 2, c), tex=self.tex + 1)
            rectangular_prism(world, 1, 4, 2, (a, b + 2, c + 12), tex=self.tex + 1)

            pusher_a = Pusher(
                xyz=m(a + 3, b + 4, c + 1, size=SIZE * SIZE_OFFSET),
                pitch=74,
                yaw=90,
                force=400 * SIZE_OFFSET,
            )

            pusher_b = Pusher(
                xyz=m(a + 2, b + 4, c + 15 + (2 if SIZE_OFFSET == 0.5 else 0), size=SIZE * SIZE_OFFSET),
                pitch=40,
                yaw=270,
                force=200 * SIZE_OFFSET,
            )
        elif self.orientation == '-y':
            #Walls
            multi_wall(world, ('+y', '+x', '-x'), SIZE, self.pos, tex=self.tex)
            multi_wall(world, ('-y', '+y', '+x', '-x'), SIZE, mv(self.pos, m(0, 0, 1)), tex=self.tex)
            multi_wall(world, ('+y', '+x', '-x'), SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
            column(world, 'x', 8, mv(self.pos, m(0, 0, 2)), tex=4)
            # Red markers
            rectangular_prism(world, 4, 2, 1, (a + 2, b + 4, c), tex=self.tex + 1)
            rectangular_prism(world, 4, 1, 2, (a + 2, b + 7, c + 12), tex=self.tex + 1)
            pusher_a = Pusher(
                xyz=m(a + 4, b + 5, c + 1, size=SIZE * SIZE_OFFSET),
                pitch=74,
                yaw=0,
                force=400 * SIZE_OFFSET,
            )

            pusher_b = Pusher(
                xyz=m(a + 4, b + 6, c + 15 + (2 if SIZE_OFFSET == 0.5 else 0), size=SIZE * SIZE_OFFSET),
                pitch=40,
                yaw=180,
                force=200 * SIZE_OFFSET,
            )
        elif self.orientation == '+y':
            #Walls
            multi_wall(world, ('-y', '+x', '-x'), SIZE, self.pos, tex=self.tex)
            multi_wall(world, ('-y', '+y', '+x', '-x'), SIZE, mv(self.pos, m(0, 0, 1)), tex=self.tex)
            multi_wall(world, ('-y', '+x', '-x'), SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
            column(world, 'x', 8, mv(self.pos, m(7/8, 0, 2)), tex=4)
            # Red markers
            rectangular_prism(world, 4, 2, 1, (a + 2, b + 2, c), tex=self.tex + 1)
            rectangular_prism(world, 4, 1, 2, (a + 2, b, c + 12), tex=self.tex + 1)

            pusher_a = Pusher(
                xyz=m(a + 4, b + 3, c + 1, size=SIZE * SIZE_OFFSET),
                pitch=74,
                yaw=180,
                force=400 * SIZE_OFFSET,
            )

            pusher_b = Pusher(
                xyz=m(a + 4, b + 2, c + 15 + (2 if SIZE_OFFSET == 0.5 else 0), size=SIZE * SIZE_OFFSET),
                pitch=40,
                yaw=0,
                force=200 * SIZE_OFFSET,
            )

        xmap.ents.append(pusher_a)
        xmap.ents.append(pusher_b)

    def get_positions(self):
        return [
            self.pos,
            mv(self.pos, m(0, 0, 1)),
            mv(self.pos, m(0, 0, 2)),
        ]


class JumpCorridorVerticalCenter(JumpCorridorVertical):
    def _get_doorways(self):
        return [
            m(1, 0, 0),
            m(-1, 0, 0),
            m(0, 1, 0),
            m(0, -1, 0),

            m(1, 0, 2),
            m(-1, 0, 2),
            m(0, 1, 2),
            m(0, -1, 2),
        ]

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=random.randint(92, 115))
        wall(world, '+z', SIZE, mv(self.pos, m(0, 0, 2)), tex=self.tex)
        self.light(xmap)

        (a, b, c) = self.pos
        #Walls
        multi_wall(world, ('-x', '+x', '+y', '-y'), SIZE, mv(self.pos, m(0, 0, 1)), tex=self.tex)
        # Red markers
        rectangular_prism(world, 4, 4, 1, (a + 2, b + 2, c), tex=self.tex + 1)
        pusher_a = Pusher(
            xyz=m(a + 4, b + 4, c + 1, size=SIZE * SIZE_OFFSET),
            pitch=90,
            yaw=0,
            force=460 * SIZE_OFFSET,
            maxrad=5
        )
        xmap.ents.append(pusher_a)

    def get_positions(self):
        return [
            self.pos,
            mv(self.pos, m(0, 0, 1)),
            mv(self.pos, m(0, 0, 2)),
        ]


class Corridor4way(_Room):
    room_type = 'platform'
    _randflags = (
        True, # roof
        True, # Wall: A (A + B; !A!B: no walls, B!A: half, A!B: full, AB: columns)
        True, # Wall: B
    )

    def __init__(self, pos, orientation=None, tex=2, randflags=None):
        self.pos = pos
        self.tex = tex
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, random.randint(92, 115))
        if self._randflags[0]:
            wall(world, '+z', SIZE, self.pos)

        if not self._randflags[1] and not self._randflags[2]:
            pass
        elif self._randflags[1] and not self._randflags[2]:
            column(world, 'z', 8, mv(self.pos, (0, 0, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (0, SIZE - 1, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (SIZE - 1, 0, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (SIZE - 1, SIZE - 1, 0)), tex=4)
        elif not self._randflags[1] and self._randflags[2]:
            column(world, 'z', 2, mv(self.pos, (0, 0, 0)), tex=4)
            column(world, 'z', 2, mv(self.pos, (0, SIZE - 1, 0)), tex=4)
            column(world, 'z', 2, mv(self.pos, (SIZE - 1, 0, 0)), tex=4)
            column(world, 'z', 2, mv(self.pos, (SIZE - 1, SIZE - 1, 0)), tex=4)
        else:
            pass
            # TODO

        self.light(xmap)

class SpawnRoom(_OrientedRoom):
    room_type = 'platform_setpiece'
    _randflags = (
        True, # Two sides open
    )

    def __init__(self, pos, roof=None, orientation='+x', randflags=None):
        self.pos = pos
        self.orientation = orientation
        self.tex = 9
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        wall(world, '-z', SIZE, self.pos, tex=self.tex)
        wall(world, '+z', SIZE, self.pos, tex=self.tex)

        if self.orientation == '+x':
            if not self._randflags[0]:
                wall(world, '-x', SIZE, self.pos)
            wall(world, '+y', SIZE, self.pos)
            wall(world, '-y', SIZE, self.pos)
        elif self.orientation == '-x':
            if not self._randflags[0]:
                wall(world, '+x', SIZE, self.pos)
            wall(world, '+y', SIZE, self.pos)
            wall(world, '-y', SIZE, self.pos)
        elif self.orientation == '+y':
            if not self._randflags[0]:
                wall(world, '-y', SIZE, self.pos)
            wall(world, '+x', SIZE, self.pos)
            wall(world, '-x', SIZE, self.pos)
        elif self.orientation == '-y':
            if not self._randflags[0]:
                wall(world, '+y', SIZE, self.pos)
            wall(world, '+x', SIZE, self.pos)
            wall(world, '-x', SIZE, self.pos)
        else:
            raise Exception("Unknown orientation %s" % self.orientation)

        spawn = PlayerSpawn(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + SIZE / 2),
                SIZE_OFFSET * (self.pos[1] + SIZE / 2),
                SIZE_OFFSET * (self.pos[2] + 1),
            )
        )
        xmap.ents.append(spawn)
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + SIZE / 2),
                SIZE_OFFSET * (self.pos[1] + SIZE / 2),
                SIZE_OFFSET * (self.pos[2] + 6),
            )
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

class _LargeRoom(_3X3Room):
    _height = 1

    def __init__(self, pos, roof=False, orientation=None, randflags=None):
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
        if randflags:
            self._randflags = randflags

    def get_positions(self):
        positions = []
        for z in range(self._height):
            positions += [
                mv(self.pos , m(-1 , -1 , z)),
                mv(self.pos , m(-1 , 0  , z)),
                mv(self.pos , m(-1 , 1  , z)),
                mv(self.pos , m(0  , -1 , z)),
                mv(self.pos , m(0  , 0  , z)),
                mv(self.pos , m(0  , 1  , z)),
                mv(self.pos , m(1  , -1 , z)),
                mv(self.pos , m(1  , 0  , z)),
                mv(self.pos , m(1  , 1  , z)),
            ]
        return positions


class PoleRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True, # Floating
        True, # Tall
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        self.light(xmap)
        # size = 24
        wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, 0)))
        if self._randflags[1]:
            wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, self._height)))

        for i in range(-8, 15):
            for j in range(-8, 15):
                if random.random() < 0.05:
                    if False and self._randflags[0]:
                        column(
                            world, 'z',
                            random.randint(0, 8 * self._height),
                            mv(self.pos, (i, j, 0)),
                            tex=random.randint(712, 715)
                        )
                    else:
                        offset = random.randint(1, 8 * self._height / 2)
                        column(
                            world, 'z',
                            (8 * self._height) - (2 * offset),
                            mv(self.pos, (i, j, offset)),
                            tex=random.randint(161, 179)
                        )

    def light(self, xmap):
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 3),
                SIZE_OFFSET * (self.pos[1] + 4),
                SIZE_OFFSET * (self.pos[2] + 7),
            ),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)


class ImposingBlockRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True, # Roof
        True, # Tall
        True, # Vary Cube Sizes
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        self.light(xmap)
        # size = 24
        wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, 0)))
        if self._randflags[0]:
            wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, self._height)))

        # tex = random.randint(161, 169)
        tex = random.randint(712, 715)
        if self._randflags[2]:
            cube_s(world, random.randint(4,7), mv(self.pos, (7, 7, 0)), tex=tex)
            cube_s(world, random.randint(4,7), mv(self.pos, (-5, 7, 0)), tex=tex)
            cube_s(world, random.randint(4,7), mv(self.pos, (7, -5, 0)), tex=tex)
            cube_s(world, random.randint(4,7), mv(self.pos, (-5, -5, 0)), tex=tex)
        else:
            cube_s(world, 6, mv(self.pos, (7, 7, 0)), tex=tex)
            cube_s(world, 6, mv(self.pos, (-5, 7, 0)), tex=tex)
            cube_s(world, 6, mv(self.pos, (7, -5, 0)), tex=tex)
            cube_s(world, 6, mv(self.pos, (-5, -5, 0)), tex=tex)

    def light(self, xmap):
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 3),
                SIZE_OFFSET * (self.pos[1] + 4),
                SIZE_OFFSET * (self.pos[2] + 7),
            ),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)


class ImposingRingRoom(_LargeRoom):
    _randflags = (
        True, # Roof
        True, # Tall
        True, # Offset inner rings
        True, # Center Pillar
        True, # Inner Rings
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        self.light(xmap)

        # size = 24
        wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, 0)), tex=random.randint(92, 115))
        if self._randflags[0]:
            wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, self._height)))

        column(world, 'z', 8 * self._height, mv(self.pos, (15, 15, 0)), tex=100)
        column(world, 'z', 8 * self._height, mv(self.pos, (-8, 15, 0)), tex=100)
        column(world, 'z', 8 * self._height, mv(self.pos, (15, -8, 0)), tex=100)
        column(world, 'z', 8 * self._height, mv(self.pos, (-8, -8, 0)), tex=100)

        if self._randflags[3]:
            column(world, 'z', 8 * self._height, mv(self.pos, (2, 3, 0)), tex=100)
            column(world, 'z', 8 * self._height, mv(self.pos, (4, 2, 0)), tex=100)
            column(world, 'z', 8 * self._height, mv(self.pos, (3, 5, 0)), tex=100)
            column(world, 'z', 8 * self._height, mv(self.pos, (5, 4, 0)), tex=100)

        for i in range(1, self._height * 8, 2):
            ring(world, mv(self.pos, (-4, -4, i)), size=16, tex=123, thickness=1)
            if not self._randflags[2] and self._randflags[4]:
                ring(world, mv(self.pos, (-2, -2, i)), size=12, tex=123, thickness=1)

        if self._randflags[2] and self._randflags[4]:
            for i in range(2, self._height * 8, 2):
                ring(world, mv(self.pos, (-2, -2, i)), size=12, tex=123, thickness=1)

        column(world, 'z', 8 * self._height - 1, mv(self.pos, (-4, 4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (-4, 3, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (-2, 4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (-2, 3, 1)), subtract=True)

        column(world, 'z', 8 * self._height - 1, mv(self.pos, (11, 4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (11, 3, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (9, 4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (9, 3, 1)), subtract=True)

        column(world, 'z', 8 * self._height - 1, mv(self.pos, (4, -4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (3, -4, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (4, -2, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (3, -2, 1)), subtract=True)

        column(world, 'z', 8 * self._height - 1, mv(self.pos, (4, 11, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (3, 11, 1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (4, 9,  1)), subtract=True)
        column(world, 'z', 8 * self._height - 1, mv(self.pos, (3, 9,  1)), subtract=True)

    def light(self, xmap):
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 4),
                SIZE_OFFSET * (self.pos[1] + 4),
                SIZE_OFFSET * (self.pos[2] + 4),
            ),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 128,
        )
        xmap.ents.append(light)


class AltarRoom(_3X3Room):
    _randflags = (
        True, # Tree
        True, # Rings
        True, # Columns
    )

    def __init__(self, pos, roof=False, orientation=None, randflags=None):
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
        if randflags:
            self._randflags = randflags

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

        if self._randflags[2]:
            column(world, 'z', 8, mv(self.pos, (15, 15, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (-8, 15, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (15, -8, 0)), tex=4)
            column(world, 'z', 8, mv(self.pos, (-8, -8, 0)), tex=4)

        wall(world, '-z', 16, mv(self.pos, (-4, -4, 1)), tex=5)
        wall(world, '-z', 12, mv(self.pos, (-2, -2, 2)), tex=6)

        if self._randflags[1]:
            ring(world, mv(self.pos, (-4, -4, 7)), size=16, tex=7, thickness=2)

        if self._randflags[0]:
            tree = MapModel(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 4),
                    SIZE_OFFSET * (self.pos[1] + 4),
                    SIZE_OFFSET * (self.pos[2] + 3),
                ),
                yaw=rotate_a(270, self.orientation),
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
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 12),
                SIZE_OFFSET * (self.pos[1] + 12),
                SIZE_OFFSET * (self.pos[2] + 7),
            ),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 196,
        )
        xmap.ents.append(light)


class Stair(_OrientedRoom):
    room_type = 'vertical'

    @classmethod
    def get_transition_probs(cls):
        # stair
        return {
            'platform': 0.2,
            'platform_setpiece': 0.1,
            'hallway': 0.6,
            'vertical': 0.6,
            'hallway_jump': 0.2,
        }

    def __init__(self, pos, orientation='+x', randflags=None):
        self.pos = pos
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.light(xmap)
        wall(world, '-z', SIZE, self.pos)

        pusher_kw = {}
        if self.orientation == '+x':
            wall(world, '-x', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (0, 2, 0)), tex=3)
            pusher_kw = {
                'xyz': m(
                    (self.pos[0] + 5),
                    (self.pos[1] + 4),
                    (self.pos[2] + 2),
                    size=SIZE * SIZE_OFFSET
                ),
                'yaw': 90,
            }
        elif self.orientation == '-x':
            wall(world, '+x', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (SIZE / 2, 2, 0)), tex=3)
            pusher_kw = {
                'xyz': m(
                    (self.pos[0] + 3),
                    (self.pos[1] + 4),
                    (self.pos[2] + 2),
                    size=SIZE * SIZE_OFFSET
                ),
                'yaw': 270,
            }
        elif self.orientation == '+y':
            wall(world, '-y', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (2, 0, 0)), tex=3)
            pusher_kw = {
                'xyz': m(
                    (self.pos[0] + 4),
                    (self.pos[1] + 5),
                    (self.pos[2] + 2),
                    size=SIZE * SIZE_OFFSET
                ),
                'yaw': 180,
            }
        elif self.orientation == '-y':
            wall(world, '+y', SIZE, self.pos)
            cube_s(world, 4, mv(self.pos, (2, SIZE / 2, 0)), tex=3)
            pusher_kw = {
                'xyz': m(
                    (self.pos[0] + 4),
                    (self.pos[1] + 3),
                    (self.pos[2] + 2),
                    size=SIZE * SIZE_OFFSET
                ),
                'yaw': 0,
            }
        else:
            raise Exception("Unknown orientation %s" % self.orientation)

        pusher = Pusher(
            maxrad=15 * SIZE_OFFSET,
            force=250 * SIZE_OFFSET,
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


class CrossingWalkways(_LargeRoom):
    _height = 2
    _randflags = (
        True, # 2 or 3 units tall
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[0]:
            self._height = 3

    def render(self, world, xmap):
        self.light(xmap)
        # Corners are up 1
        tex2 = random.randint(92, 115)

        wall(world, '-z', SIZE, mv(self.pos, m(-1, 0, 0)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m( 0, 0, 0)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m( 1, 0, 0)), tex=tex2)

        wall(world, '-z', SIZE, mv(self.pos, m(0, -1, 1)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m(0,  0, 1)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m(0,  1, 1)), tex=tex2)

        if self._randflags[0]:
            wall(world, '-z', SIZE, mv(self.pos, m(-1, 0, 2)), tex=tex2)
            wall(world, '-z', SIZE, mv(self.pos, m( 0, 0, 2)), tex=tex2)
            wall(world, '-z', SIZE, mv(self.pos, m( 1, 0, 2)), tex=tex2)

    def _get_doorways(self):
        doors = [
            m(-2, 0, 0),
            m(2, 0, 0),
            m(0, -2, 1),
            m(0, 2, 1),
        ]

        if self._randflags[0]:
            doors += [
                m(-2, 0, 2),
                m(2, 0, 2),
            ]
        return doors

    def light(self, xmap):
        (r, g, b) = posColor(self.pos)

        for i in range(6, self._height * 8, 8):
            light = Light(
                xyz=m(
                    SIZE_OFFSET * (self.pos[0] + 4),
                    SIZE_OFFSET * (self.pos[1] + 4),
                    SIZE_OFFSET * (self.pos[2] + i),
                ),
                red=r,
                green=g,
                blue=b,
                radius=SIZE_OFFSET * 256,
            )
            xmap.ents.append(light)


class PlusPlatform(_LargeRoom):
    _height = 2
    room_type = 'platform'

    def render(self, world, xmap):
        self.light(xmap)

        # Corners are up 1
        tex1 = random.randint(92, 115)

        wall(world, '-z', SIZE, mv(self.pos, m(0, 0, 0)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(1, 0, 0)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(-1, 0, 0)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(0, 1, 0)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(0, -1, 0)), tex=tex1)

    def _get_doorways(self):
        return [
            m(-2, 0, 0),
            m(2, 0, 0),
            m(0, -2, 0),
            m(0, 2, 0),
        ]


class MultiPlatform(_LargeRoom):
    _height = 3

    def render(self, world, xmap):
        self.light(xmap)

        # size = 24
        wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, 0)), tex=random.randint(92, 115))

        # Corners are up 1
        tex1 = random.randint(92, 115)
        tex2 = random.randint(92, 115)

        wall(world, '-z', SIZE, mv(self.pos, m(1, 1, 0.50)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(-1, -1, 0.50)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(1, -1, 1)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m(-1, 1, 1)), tex=tex2)

        wall(world, '-z', SIZE, mv(self.pos, m(1, 0, 1.5)), tex=tex1)
        wall(world, '-z', SIZE, mv(self.pos, m(-1, 0, 1.50)), tex=tex1)

        wall(world, '-z', SIZE, mv(self.pos, m(0, 1, 2)), tex=tex2)
        wall(world, '-z', SIZE, mv(self.pos, m(0, -1, 2)), tex=tex2)

    def _get_doorways(self):
        return [
            m(-2, 0, 0),
            m(2, 0, 0),
            m(0, -2, 0),
            m(0, 2, 0),

            m(2, -1, 1),
            m(1, -2, 1),

            m(-1, 2, 1),
            m(-2, 1, 1),

            m(0, -2, 2),
            m(0, 2, 2),
        ]

    def light(self, xmap):
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 4),
                SIZE_OFFSET * (self.pos[1] + 4),
                SIZE_OFFSET * (self.pos[2] + 16),
            ),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)


class DigitalRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True, # Roof
        True, # Tall
        True, # Density Low / High
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        self.light(xmap)
        prob = 0.3
        if self._randflags[2]:
            prob = 0.7

        # size = 24
        faded_wall(world, '-z', SIZE * 3, mv(self.pos, m(-1, -1, 0)), tex=random.randint(92, 115), prob=0.9)
        if self._randflags[1]:
            faded_wall(world, '+z', SIZE * 3, mv(self.pos, m(-1, -1, -1)), tex=random.randint(92, 115), prob=prob)
        else:
            faded_wall(world, '+z', SIZE * 3, mv(self.pos, m(-1, -1, -2)), tex=random.randint(92, 115), prob=prob)

        wall_tex = random.randint(92, 115)
        #wall_tex = 644
        faded_wall(world, '-x', SIZE, mv(self.pos, m(-1, -1, 0)), tex=wall_tex, prob=prob)
        faded_wall(world, '-x', SIZE, mv(self.pos, m(-1, 1, 0)), tex=wall_tex, prob=prob)
        if self._randflags[1]:
            faded_wall(world, '-x', SIZE, mv(self.pos, m(-1, -1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '-x', SIZE, mv(self.pos, m(-1, 0, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '-x', SIZE, mv(self.pos, m(-1, 1, 1)), tex=wall_tex, prob=prob)

        faded_wall(world, '+x', SIZE, mv(self.pos, m(1, -1, 0)), tex=wall_tex, prob=prob)
        faded_wall(world, '+x', SIZE, mv(self.pos, m(1, 1, 0)), tex=wall_tex, prob=prob)
        if self._randflags[1]:
            faded_wall(world, '+x', SIZE, mv(self.pos, m(1, -1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '+x', SIZE, mv(self.pos, m(1, 0, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '+x', SIZE, mv(self.pos, m(1, 1, 1)), tex=wall_tex, prob=prob)

        faded_wall(world, '-y', SIZE, mv(self.pos, m(-1, -1, 0)), tex=wall_tex, prob=prob)
        faded_wall(world, '-y', SIZE, mv(self.pos, m(1, -1, 0)), tex=wall_tex, prob=prob)
        if self._randflags[1]:
            faded_wall(world, '-y', SIZE, mv(self.pos, m(-1, -1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '-y', SIZE, mv(self.pos, m(0, -1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '-y', SIZE, mv(self.pos, m(1, -1, 1)), tex=wall_tex, prob=prob)

        faded_wall(world, '+y', SIZE, mv(self.pos, m(-1, 1, 0)), tex=wall_tex, prob=prob)
        faded_wall(world, '+y', SIZE, mv(self.pos, m(1, 1, 0)), tex=wall_tex, prob=prob)
        if self._randflags[1]:
            faded_wall(world, '+y', SIZE, mv(self.pos, m(-1, 1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '+y', SIZE, mv(self.pos, m(0, 1, 1)), tex=wall_tex, prob=prob)
            faded_wall(world, '+y', SIZE, mv(self.pos, m(1, 1, 1)), tex=wall_tex, prob=prob)

    def light(self, xmap):
        (r, g, b) = posColor(self.pos)
        h = 6
        if self._height > 1:
            h = 14
        light = Light(
            xyz=m(
                SIZE_OFFSET * (self.pos[0] + 4),
                SIZE_OFFSET * (self.pos[1] + 4),
                SIZE_OFFSET * (self.pos[2] + h),
            ),
            red=r,
            green=g,
            blue=b,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)
