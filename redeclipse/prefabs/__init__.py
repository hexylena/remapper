from redeclipse.entities import Light, PlayerSpawn, Pusher
from redeclipse.entities.model import MapModel
from redeclipse.entities.weapon import Grenade
from redeclipse.textures import PrimaryThemedTextureManager
# MinecraftThemedTextureManager, DefaultThemedTextureManager, PaperThemedTextureManager
from redeclipse.lighting import PositionBasedLightManager
from redeclipse.prefabs.distributions import UniformDistributionManager
# TowerDistributionManager, PlatformDistributionManager
from redeclipse.prefabs.construction_kit import ConstructionKitMixin
from redeclipse.vector import CoarseVector, FineVector, rotate_yaw, AbsoluteVector
from redeclipse.vector.orientations import SELF, \
    SOUTH, NORTH, WEST, EAST, ABOVE, \
    ABOVE_FINE, NORTHWEST, \
    NORTHEAST, SOUTHWEST, SOUTHEAST, TILE_CENTER, HALF_HEIGHT

import random # noqa
# import math
import copy
random.seed(22)

SIZE = 8
_BUILTIN_SIZE = 2 ** 7
_REAL_SIZE = 2 ** 8
SIZE_OFFSET = _BUILTIN_SIZE / _REAL_SIZE

# TEXMAN = MinecraftThemedTextureManager()
# TEXMAN = DefaultThemedTextureManager()
# TEXMAN = PaperThemedTextureManager()
TEXMAN = PrimaryThemedTextureManager()
LIGHTMAN = PositionBasedLightManager(brightness=1.0, saturation=0.6)
# LIGHTMAN = None
# DISTMAN = TowerDistributionManager()
# DISTMAN = PlatformDistributionManager()
DISTMAN = UniformDistributionManager()
STARTING_POSITION = CoarseVector(4, 4, 3)


# Room is an object, but is also inherits from CKM which inherits from object,
# so we just inherit from CKM
class Room(ConstructionKitMixin):
    """Base 'room' class which all other room types inherit from
    """
    room_type = 'oriented'
    tex = TEXMAN.get_c('generic')
    _tp = None

    def __init__(self, pos, orientation='+x', randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def get_transition_probs(self):
        """Probabilities of transitioning to other named room types"""
        if not self._tp:
            self._tp = DISTMAN.for_class(self)
        return self._tp

    def _get_doorways(self):
        """
        Return the set of possible doorways as offsets to self.pos. DO NOT include self.pos
        """
        return [
            NORTH,
            SOUTH,
            EAST,
            WEST
        ]

    def get_doorways(self):
        """The get_doorways function that most things actually use, which applies the offset.

        This mostly means that you only need to override _get_doorways with
        your doorways. Everyone will call this and have access to shifted
        values.
        """
        # log.debug('doors', self.orientation, self._get_doorways(), [
            # self.pos + q.rotate(self.orientation) for q in self._get_doorways()
        # ])
        return [
            self.pos + q.rotate(self.orientation) for q in self._get_doorways()
        ]

    def _get_positions(self):
        return [SELF]

    def get_positions(self):
        """Positions occupied by this unit"""
        # print('pos', self.orientation, self._get_positions(), [
            # p.rotate(self.orientation) + self.pos for p in self._get_positions()
        # ])
        return [
            self.pos + p.rotate(self.orientation) for p in self._get_positions()
        ]

    @classmethod
    def randOpts(cls, prev):
        # Get the number of "flags" we can flip on a given room.
        if hasattr(cls, '_randflags'):
            number_of_options = len(cls._randflags)
        else:
            return {}

        # If the same class, only permit mutating ONE attribute.
        if cls == prev.__class__:
            mutatedOpts = list(copy.deepcopy(prev._randflags))
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
        LIGHTMAN.light(xmap, self.pos)

    def render(self, world, xmap):
        self.light(xmap)
        tex = TEXMAN.get_c('floor')

        self.x_floor(world, SELF, tex=tex)
        self.x_ceiling(world, SELF, tex=tex)


class _3X3Room(Room):
    """Another special case of room, though this probably does not need to be.
    AltarRoom is currently the only user."""
    room_type = 'platform_setpiece'

    def __init__(self, pos, orientation='+x', randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = CoarseVector(*pos)
        self.tex = TEXMAN.get_c('floor')
        self.orientation = orientation

    def _get_doorways(self):
        return [
            NORTH * 2,
            SOUTH * 2,
            EAST * 2,
            WEST * 2,
        ]

    def _get_positions(self):
        return [
            NORTHWEST,
            NORTH,
            NORTHEAST,
            WEST,
            SELF,
            EAST,
            SOUTHWEST,
            SOUTH,
            SOUTHEAST,

            # Do not place things above us
            ABOVE + NORTHWEST,
            ABOVE + NORTH,
            ABOVE + NORTHEAST,
            ABOVE + WEST,
            ABOVE + SELF,
            ABOVE + EAST,
            ABOVE + SOUTHWEST,
            ABOVE + SOUTH,
            ABOVE + SOUTHEAST,
        ]


class TestRoom(Room):
    def __init__(self, pos, orientation='+x', randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.x_floor(world, SELF, tex=TEXMAN.get_c('accent'))

        g = Grenade(
            xyz=self.pos + TILE_CENTER + ABOVE_FINE
        )
        xmap.ents.append(g)


class NLongCorridor(Room):
    room_type = 'hallway'
    _randflags = (
        True,  # A
        True,  # B; length=a<<1 | b
        True,  # CoverA
        True,  # CoverB
    )

    def __init__(self, pos, orientation='+x', randflags=None):
        self.orientation = orientation
        self.pos = CoarseVector(*pos)
        if randflags:
            self._randflags = randflags

        la = 1 if self._randflags[0] else 0
        lb = 1 if self._randflags[1] else 0
        self.length = 1 + (la << 1 | lb)

    def render(self, world, xmap):
        # First tile
        floor_tex = TEXMAN.get_c('floor')
        self.x_floor(world, SELF, tex=floor_tex)

        for i in range(1, self.length):
            # Add a floor south of us.
            self.x_floor(world, NORTH * i, tex=floor_tex)

        # for i in range(0, SIZE * self.length):
            # real_lt = self.pos + FineVector(i, 0, 1).rotate(self.orientation)
            # real_rt = self.pos + FineVector(i, 7, 1).rotate(self.orientation)

            # if 'x' in self.orientation:
                # real_idx = 0
            # else:
                # real_idx = 1

            # if self._randflags[3]:
                # y_lt = int(3 + 3 * math.sin(real_lt[real_idx]/4))
                # y_rt = int(3 + 3 * math.sin(real_rt[real_idx]/4))
                # if self._randflags[2]:
                    # column(world, 'z', y_lt, real_lt, tex=floor_tex)
                    # column(world, 'z', y_rt, real_rt, tex=floor_tex)
                # else:
                    # column(world, 'z', 1, (real_lt[0], real_lt[1], real_lt[2] + y_lt - 1), tex=floor_tex)
                    # column(world, 'z', 1, (real_rt[0], real_rt[1], real_rt[2] + y_rt - 1), tex=floor_tex)

        self.light(xmap)

    def _get_positions(self):
        positions = [SELF]

        # Same logic as init
        for i in range(1, self.length):
            positions.append(NORTH * i)

        return positions

    def _get_doorways(self):
        return [
            SOUTH,
            NORTH * self.length
        ]


class Corridor2way(Room):
    room_type = 'hallway'
    _randflags = (
        True,  # roof
        True,  # no wall / low wall
    )

    def __init__(self, pos, orientation='+x', randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.light(xmap)
        floor_tex = TEXMAN.get_c('floor')

        self.x_floor(world, SELF, tex=floor_tex)
        if self._randflags[0]:
            self.x_ceiling(world, SELF, tex=floor_tex)

        if self._randflags[1]:
            # TODO: low wall (2 high)
            self.x_low_wall(world, SELF + ABOVE_FINE, EAST)
            self.x_low_wall(world, SELF + ABOVE_FINE, WEST)

    def _get_doorways(self):
        return [
            SOUTH,
            NORTH + NORTH
        ]


class JumpCorridor3(Room):
    room_type = 'hallway_jump'

    def __init__(self, pos, orientation='+x', randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def light(self, xmap):
        all_positions = self.get_positions()
        # Light the first and last positions
        LIGHTMAN.light(xmap, all_positions[0])
        LIGHTMAN.light(xmap, all_positions[-1])

    def render(self, world, xmap):
        pusher_a = None
        pusher_b = None
        self.light(xmap)
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        (a, b, c) = self.pos

        pusher_a = Pusher(
            xyz=self.pos + FineVector(7, 4, 1).rotate(self.orientation) + self.x_get_adjustment(),
            maxrad=15 * SIZE_OFFSET,
            yaw=rotate_yaw(270, self.orientation),
            force=175 * SIZE_OFFSET,
        )

        pusher_b = Pusher(
            xyz=self.pos + (NORTH + NORTH + FineVector(1, 4, 1)).rotate(self.orientation) + self.x_get_adjustment(),
            maxrad=15 * SIZE_OFFSET,
            yaw=rotate_yaw(90, self.orientation),
            force=175 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_a)
        xmap.ents.append(pusher_b)

        self.x_floor(world, SELF, tex=floor_tex)
        self.x_floor(world, SELF + NORTH + NORTH, tex=floor_tex)

        self.x_low_wall(world, SELF + ABOVE_FINE, EAST, tex=wall_tex)
        # self.x_low_wall(world, SELF + ABOVE_FINE, WEST, tex=wall_tex)
        self.x_low_wall(world, SELF + NORTH + NORTH + ABOVE_FINE, EAST, tex=wall_tex)
        # self.x_low_wall(world, SELF + NORTH + NORTH + ABOVE_FINE, WEST, tex=wall_tex)

        self.x_rectangular_prism(world, FineVector(6, 2, 0), AbsoluteVector(2, 4, 1), tex=accent_tex)
        self.x_rectangular_prism(world, NORTH + NORTH + FineVector(0, 2, 0), AbsoluteVector(2, 4, 1), tex=accent_tex)

    def _get_positions(self):
        positions = []
        for i in range(3):
            positions.append(NORTH * i)
        return positions

    def _get_doorways(self):
        return [
            SOUTH,
            NORTH * 3
        ]


class JumpCorridorVertical(Room):
    room_type = 'vertical'
    _randflags = (
        True,  # extra section
    )

    def __init__(self, pos, orientation='+x', roof=False, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        self.roof = roof
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        self.x_floor(world, SELF, tex=floor_tex)
        self.x_ceiling(world, SELF + ABOVE + ABOVE, tex=floor_tex)
        self.light(xmap)

        pusher_a = Pusher(
            xyz=self.pos + FineVector(5, 4, 1).rotate(self.orientation) + self.x_get_adjustment(),
            pitch=74,
            yaw=rotate_yaw(270, self.orientation),
            force=400 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_a)

        pusher_b = Pusher(
            xyz=self.pos + FineVector(6, 4, 17).rotate(self.orientation) + self.x_get_adjustment(),
            pitch=40,
            yaw=rotate_yaw(90, self.orientation),
            force=200 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_b)

        (a, b, c) = self.pos

        self.x_wall(world, SELF, face=SOUTH, tex=wall_tex)
        self.x_wall(world, SELF, face=EAST, tex=wall_tex)
        self.x_wall(world, SELF, face=WEST, tex=wall_tex)

        self.x_wall(world, SELF + ABOVE, face=NORTH, tex=wall_tex)
        self.x_wall(world, SELF + ABOVE, face=SOUTH, tex=wall_tex)
        self.x_wall(world, SELF + ABOVE, face=EAST, tex=wall_tex)
        self.x_wall(world, SELF + ABOVE, face=WEST, tex=wall_tex)

        self.x_wall(world, SELF + ABOVE + ABOVE, face=SOUTH, tex=wall_tex)
        self.x_wall(world, SELF + ABOVE + ABOVE, face=EAST, tex=wall_tex)
        self.x_wall(world, SELF + ABOVE + ABOVE, face=WEST, tex=wall_tex)

        self.x_rectangular_prism(world, FineVector(4, 2, 0), AbsoluteVector(2, 4, 1), tex=accent_tex)
        self.x_rectangular_prism(world, FineVector(7, 2, 12), AbsoluteVector(1, 4, 2), tex=accent_tex)
        self.x_rectangular_prism(world, FineVector(0, 1, 0) + ABOVE + ABOVE, AbsoluteVector(1, 6, 1), tex=accent_tex)

    def _get_positions(self):
        return [
            SELF,
            SELF + ABOVE,
            SELF + ABOVE + ABOVE,
        ]

    def _get_doorways(self):
        return [
            SOUTH,
            SOUTH + ABOVE + ABOVE
        ]


class JumpCorridorVerticalCenter(JumpCorridorVertical):
    length = 1
    _randflags = (
        True,  # Tall
    )

    def __init__(self, pos, orientation='+x', roof=False, tex=506, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        self.roof = roof
        self.tex = tex
        if randflags:
            self._randflags = randflags
        if self._randflags[0]:
            self.length = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        self.x_floor(world, SELF, tex=floor_tex)
        self.light(xmap)

        (a, b, c) = self.pos
        # Walls
        for i in range(1, self.length + 1):
            self.x_wall(world, SELF + (ABOVE * i), face=NORTH, tex=wall_tex)
            self.x_wall(world, SELF + (ABOVE * i), face=SOUTH, tex=wall_tex)
            self.x_wall(world, SELF + (ABOVE * i), face=EAST, tex=wall_tex)
            self.x_wall(world, SELF + (ABOVE * i), face=WEST, tex=wall_tex)

        # Red markers
        self.x_rectangular_prism(world, FineVector(2, 2, 0), AbsoluteVector(4, 4, 1), tex=accent_tex)

        force = 460 * SIZE_OFFSET
        if self.length == 2:
            force = 700 * SIZE_OFFSET

        pusher_a = Pusher(
            xyz=self.pos + FineVector(4, 4, 1).rotate(self.orientation) + self.x_get_adjustment(),
            pitch=90,
            maxrad=5,
            yaw=rotate_yaw(0, self.orientation),
            force=force,
        )
        xmap.ents.append(pusher_a)

    def _get_positions(self):
        positions = []
        for i in range(self.length + 2):
            positions.append(ABOVE * i)
        return positions

    def _get_doorways(self):
        return [
            NORTH,
            SOUTH,
            EAST,
            WEST,

            NORTH + ABOVE * (self.length + 1),
            SOUTH + ABOVE * (self.length + 1),
            EAST + ABOVE * (self.length + 1),
            WEST + ABOVE * (self.length + 1),
        ]


class Corridor4way(Room):
    room_type = 'platform'
    _randflags = (
        True,  # roof
        True,  # Wall: A (A + B; !A!B: no walls, B!A: half, A!B: full, AB: columns)
        True,  # Wall: B
    )

    def __init__(self, pos, orientation='+x', randflags=None):
        self.orientation = orientation
        self.pos = CoarseVector(*pos)
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        column_tex = TEXMAN.get_c('column')

        self.x_floor(world, SELF, tex=floor_tex)
        if self._randflags[0]:
            self.x_ceiling(world, SELF, tex=floor_tex)

        if not self._randflags[1] and not self._randflags[2]:
            pass
        elif self._randflags[1] and not self._randflags[2]:
            self.x_rectangular_prism(world, FineVector(0, 0, 0), AbsoluteVector(1, 1, 8), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(0, 7, 0), AbsoluteVector(1, 1, 8), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(7, 0, 0), AbsoluteVector(1, 1, 8), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(7, 7, 0), AbsoluteVector(1, 1, 8), tex=column_tex)
        elif not self._randflags[1] and self._randflags[2]:
            self.x_rectangular_prism(world, FineVector(0, 0, 0), AbsoluteVector(1, 1, 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(0, 7, 0), AbsoluteVector(1, 1, 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(7, 0, 0), AbsoluteVector(1, 1, 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(7, 7, 0), AbsoluteVector(1, 1, 2), tex=column_tex)
        else:
            pass

        self.light(xmap)


class SpawnRoom(Room):
    room_type = 'platform_setpiece'
    _randflags = (
        True,  # Two sides open
    )

    def __init__(self, pos, roof=None, orientation='+x', randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        # Floor and ceiling
        self.x_floor(world, SELF, tex=floor_tex)
        self.x_ceiling(world, SELF, tex=floor_tex)

        # Sometimes we add a 'back' to it
        if not self._randflags[0]:
            self.x_wall(world, SELF, face=SELF, tex=accent_tex)

        # Always add at least two walls for cover
        self.x_wall(world, SELF, face=EAST, tex=wall_tex)
        self.x_wall(world, SELF, face=WEST, tex=wall_tex)

        xmap.ents.append(PlayerSpawn(
            xyz=self.pos + TILE_CENTER + FineVector(0, 0, 1)
        ))

        self.light(xmap)

    def _get_doorways(self):
        doors = [NORTH]
        if self._randflags[0]:
            doors += [SOUTH]
        return doors


class _LargeRoom(_3X3Room):
    _height = 1

    def __init__(self, pos, roof=False, orientation='+x', randflags=None):
        # Push the position
        self.orientation = orientation
        # We (arbitrarily) define pos as the middle of one side.
        self.pos = CoarseVector(*pos)
        # We move it once, in orientation in order to re-center the room?
        if self.orientation == '+x':
            self.pos = self.pos + SOUTH
        elif self.orientation == '-x':
            self.pos = self.pos + NORTH
        elif self.orientation == '+y':
            self.pos = self.pos + WEST
        elif self.orientation == '-y':
            self.pos = self.pos + EAST
        # For bigger rooms, we have to shift them such that the previous_posision matches a doorway.
        if randflags:
            self._randflags = randflags

    def _get_positions(self):
        positions = []
        for z in range(self._height):
            positions += [
                (ABOVE * z) + NORTHWEST,
                (ABOVE * z) + NORTH,
                (ABOVE * z) + NORTHEAST,
                (ABOVE * z) + WEST,
                (ABOVE * z) + SELF,
                (ABOVE * z) + EAST,
                (ABOVE * z) + SOUTHWEST,
                (ABOVE * z) + SOUTH,
                (ABOVE * z) + SOUTHEAST,
            ]
        return positions

    def light(self, xmap):
        h = 6
        if self._height > 1:
            h = 12
        position = self.pos + NORTH + TILE_CENTER + FineVector(0, 0, h)
        LIGHTMAN.light(xmap, position.rotate(self.orientation))


class PoleRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True,  # Floating
        True,  # Tall
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)
        # size = 24
        self.x_floor(world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[1]:
            self.x_ceiling(world, SOUTHWEST + ABOVE, tex=floor_tex, size=24)

        for i in range(-8, 15):
            for j in range(-8, 15):
                if random.random() < 0.05:
                    if 2 <= i <= 4 and 3 <= j <= 5:
                        # Do not occupy same space as light.
                        continue

                    if False and self._randflags[0]:
                        self.x_rectangular_prism(world, FineVector(i, j, 0) + ABOVE_FINE,
                                                 AbsoluteVector(1, 1, 8 * self._height),
                                                 tex=TEXMAN.get_c('column'))
                    else:
                        offset = random.randint(1, 8 * self._height / 2)
                        self.x_rectangular_prism(world, FineVector(i, j, 0) + (ABOVE_FINE * offset),
                                                 AbsoluteVector(1, 1, (8 * self._height) - (2 * offset)),
                                                 tex=TEXMAN.get_c('column'))

    def light(self, xmap):
        light = Light(
            xyz=self.pos + FineVector(3, 4, 10),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)


class ImposingBlockRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True,  # Roof
        True,  # Tall
        True,  # Vary Cube Sizes
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)
        # size = 24
        self.x_floor(world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[0]:
            self.x_ceiling(world, SOUTHWEST + (ABOVE * (self._height - 1)), tex=floor_tex, size=24)

        if self._randflags[2]:
            def q():
                return random.randint(4, 7)
            self.x_rectangular_prism(world, FineVector(7, 7, 0), AbsoluteVector(q(), q(), q()), tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(-5, 7, 0), AbsoluteVector(q(), q(), q()), tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(7, -5, 0), AbsoluteVector(q(), q(), q()), tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(-5, -5, 0), AbsoluteVector(q(), q(), q()), tex=TEXMAN.get_c('generic'))
        else:
            v = AbsoluteVector(6, 6, 6)
            self.x_rectangular_prism(world, FineVector(7, 7, 0), v, tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(-5, 7, 0), v, tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(7, -5, 0), v, tex=TEXMAN.get_c('generic'))
            self.x_rectangular_prism(world, FineVector(-5, -5, 0), v, tex=TEXMAN.get_c('generic'))

    def light(self, xmap):
        light = Light(
            xyz=self.pos + FineVector(3, 4, 7),
            red=255,
            green=255,
            blue=255,
            radius=SIZE_OFFSET * 256,
        )
        xmap.ents.append(light)


class ImposingRingRoom(_LargeRoom):
    _randflags = (
        True,  # Roof
        True,  # Tall
        True,  # Offset inner rings
        True,  # Center Pillar
        True,  # Inner Rings
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        accent_tex = TEXMAN.get_c('accent')
        column_tex = TEXMAN.get_c('column')

        self.light(xmap)

        # size = 24
        self.x_floor(world, SOUTHWEST, tex=floor_tex, size=24)
        if self._randflags[0]:
            self.x_ceiling(world, SOUTHWEST + (ABOVE * (self._height - 1)), tex=floor_tex, size=24)

        self.x_rectangular_prism(world, FineVector(15, 15, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x_rectangular_prism(world, FineVector(-8, 15, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x_rectangular_prism(world, FineVector(15, -8, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x_rectangular_prism(world, FineVector(-8, -8, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)

        if self._randflags[3]:
            self.x_rectangular_prism(world, FineVector(2, 3, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(4, 2, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(3, 5, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(5, 4, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)

        for i in range(1, self._height * 8 - 1, 2):
            self.x_ring(world, FineVector(-4, -4, i), 16, tex=accent_tex)
            if not self._randflags[2] and self._randflags[4]:
                self.x_ring(world, FineVector(-2, -2, i), 12, tex=accent_tex)

        if self._randflags[2] and self._randflags[4]:
            for i in range(2, self._height * 8 - 1, 2):
                self.x_ring(world, FineVector(-2, -2, i), 12, tex=accent_tex)

        self.x_rectangular_prism(world, FineVector(-4, 2, 1), AbsoluteVector(3, 4, 8 * self._height - 2), subtract=True)
        self.x_rectangular_prism(world, FineVector(2, -4, 1), AbsoluteVector(4, 3, 8 * self._height - 2), subtract=True)
        self.x_rectangular_prism(world, FineVector(10, 2, 1), AbsoluteVector(3, 4, 8 * self._height - 2), subtract=True)
        self.x_rectangular_prism(world, FineVector(2, 10, 1), AbsoluteVector(4, 3, 8 * self._height - 2), subtract=True)

    def light(self, xmap):
        LIGHTMAN.light(xmap, self.pos + NORTH + HALF_HEIGHT + TILE_CENTER)


class AltarRoom(_3X3Room):
    _randflags = (
        True,  # Tree
        True,  # Rings
        True,  # Columns
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[1]:
            self._height = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        accent_tex = TEXMAN.get_c('accent')
        column_tex = TEXMAN.get_c('column')

        self.light(xmap)
        # size = 24
        self.x_floor(world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[2]:
            self.x_rectangular_prism(world, FineVector(15, 15, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(-8, 15, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(15, -8, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x_rectangular_prism(world, FineVector(-8, -8, 1), AbsoluteVector(1, 1, (8 * self._height) - 2), tex=column_tex)

        self.x_floor(world, SOUTHWEST + FineVector(4, 4, 1), tex=accent_tex, size=16)
        self.x_floor(world, SOUTHWEST + FineVector(5, 5, 2), tex=floor_tex, size=14)

        if self._randflags[1]:
            self.x_ring(world, FineVector(-4, -4, 7), 16, tex=accent_tex)
            self.x_ring(world, FineVector(-6, -6, 7), 20, tex=accent_tex)

        if self._randflags[0]:
            tree = MapModel(
                xyz=self.pos + FineVector(4, 4, 3).rotate(self.orientation),
                yaw=rotate_yaw(270, self.orientation),
                type=124
            )
            xmap.ents.append(tree)

    def _get_positions(self):
        return [
            ABOVE + NORTHWEST,
            ABOVE + NORTH,
            ABOVE + NORTHEAST,
            ABOVE + WEST,
            ABOVE + SELF,
            ABOVE + EAST,
            ABOVE + SOUTHWEST,
            ABOVE + SOUTH,
            ABOVE + SOUTHEAST,

            ABOVE + ABOVE + NORTHWEST,
            ABOVE + ABOVE + NORTH,
            ABOVE + ABOVE + NORTHEAST,
            ABOVE + ABOVE + WEST,
            ABOVE + ABOVE + SELF,
            ABOVE + ABOVE + EAST,
            ABOVE + ABOVE + SOUTHWEST,
            ABOVE + ABOVE + SOUTH,
            ABOVE + ABOVE + SOUTHEAST,
        ]


class Stair(Room):
    room_type = 'stair'

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)

        self.x_rectangular_prism(world, FineVector(0, 0, 0), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(1, 0, 1), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(2, 0, 2), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(3, 0, 3), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(4, 0, 4), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(5, 0, 5), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(6, 0, 6), AbsoluteVector(1, 8, 1), tex=floor_tex)
        self.x_rectangular_prism(world, FineVector(7, 0, 7), AbsoluteVector(1, 8, 1), tex=floor_tex)

    def _get_doorways(self):
        return [SOUTH, NORTH + ABOVE]

    def _get_positions(self):
        return [SELF, ABOVE]


class CrossingWalkways(_LargeRoom):
    _height = 2
    _randflags = (
        True,  # 2 or 3 units tall
    )

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        if self._randflags[0]:
            self._height = 3

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)
        # Corners are up 1

        self.x_floor(world, NORTH, tex=floor_tex)
        self.x_floor(world, SELF, tex=floor_tex)
        self.x_floor(world, SOUTH, tex=floor_tex)

        self.x_floor(world, EAST + ABOVE, tex=floor_tex)
        self.x_floor(world, SELF + ABOVE, tex=floor_tex)
        self.x_floor(world, WEST + ABOVE, tex=floor_tex)

        if self._randflags[0]:
            self.x_floor(world, NORTH + ABOVE + ABOVE, tex=floor_tex)
            self.x_floor(world, SELF + ABOVE + ABOVE, tex=floor_tex)
            self.x_floor(world, SOUTH + ABOVE + ABOVE, tex=floor_tex)

    def _get_doorways(self):
        doors = [
            SOUTH + SOUTH,
            NORTH + NORTH,
            EAST + EAST + ABOVE,
            WEST + WEST + ABOVE,
        ]

        if self._randflags[0]:
            doors += [
                SOUTH + SOUTH + ABOVE + ABOVE,
                NORTH + NORTH + ABOVE + ABOVE,
            ]
        return doors

    def light(self, xmap):
        for i in range(self._height):
            LIGHTMAN.light(xmap, SELF + (ABOVE * i))


class PlusPlatform(_LargeRoom):
    _height = 2
    room_type = 'platform_setpiece'

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)

        self.x_floor(world, SELF, tex=floor_tex)
        self.x_floor(world, NORTH, tex=floor_tex)
        self.x_floor(world, SOUTH, tex=floor_tex)
        self.x_floor(world, EAST, tex=floor_tex)
        self.x_floor(world, WEST, tex=floor_tex)

    def _get_doorways(self):
        return [
            NORTH * 2,
            SOUTH * 2,
            EAST * 2,
            WEST * 2
        ]


class MultiPlatform(_LargeRoom):
    _height = 3
    _randflags = (
        True,  # Floor
    )

    def render(self, world, xmap):
        self.light(xmap)
        tex1 = TEXMAN.get_c('floor')
        tex2 = TEXMAN.get_c('floor')

        if self._randflags[0]:
            self.x_floor(world, SOUTHWEST, tex=tex1, size=24)

        # Corners are up 1
        self.x_floor(world, NORTHEAST + HALF_HEIGHT, tex=tex1)
        self.x_floor(world, SOUTHWEST + HALF_HEIGHT, tex=tex1)

        self.x_floor(world, NORTHWEST + ABOVE, tex=tex2)
        self.x_floor(world, SOUTHEAST + ABOVE, tex=tex2)

        self.x_floor(world, NORTH + ABOVE + HALF_HEIGHT, tex=tex1)
        self.x_floor(world, SOUTH + ABOVE + HALF_HEIGHT, tex=tex1)

        self.x_floor(world, WEST + ABOVE + ABOVE, tex=tex2)
        self.x_floor(world, EAST + ABOVE + ABOVE, tex=tex2)

    def _get_doorways(self):
        return [
            # four center sides
            SOUTH + SOUTH,
            NORTH + NORTH,
            EAST + EAST,
            WEST + WEST,

            # First real above, ignoring half height ones.
            NORTHWEST + NORTH + ABOVE,
            NORTHWEST + WEST + ABOVE,
            SOUTHEAST + SOUTH + ABOVE,
            SOUTHEAST + EAST + ABOVE,

            WEST + WEST + ABOVE + ABOVE,
            EAST + EAST + ABOVE + ABOVE,
        ]

    def light(self, xmap):
        position = self.pos + TILE_CENTER + FineVector(0, 0, 16)
        LIGHTMAN.light(xmap, position)


class FlatSpace(_LargeRoom):
    _height = 1

    def render(self, world, xmap):
        self.light(xmap)
        floor_tex = TEXMAN.get_c('floor')
        self.x_floor(world, SOUTHWEST, tex=floor_tex, size=24)


class DigitalRoom(_LargeRoom):
    _height = 1
    _randflags = (
        True,  # Roof
        True,  # Tall
        True,  # Density Low / High
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

        wall_tex = TEXMAN.get_c('wall')
        ceil_tex = TEXMAN.get_c('wall')

        # TODO: fade 0.9
        prob = 1.0
        self.x_floor(world, SOUTHWEST, tex=ceil_tex, size=24, prob=1.9)
        # if self._randflags[1]:
        # self.x_ceiling(world, SOUTHWEST + ABOVE, tex=ceil_tex, size=24, prob=0.9)
        # else:
        # self.x_ceiling(world, SOUTHWEST, tex=ceil_tex, size=24, prob=0.9)

        # wall_tex = 644
        # TODO: Fix this bug.
        # self.x_wall(world, NORTHWEST, face=SOUTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, NORTHEAST, face=SOUTH, tex=wall_tex, prob=prob)

        # self.x_wall(world, SOUTHWEST, face=NORTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTHEAST, face=NORTH, tex=wall_tex, prob=prob)

        self.x_wall(world, NORTHWEST, face=WEST, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTHWEST, face=WEST, tex=wall_tex, prob=prob)

        # self.x_wall(world, SOUTHEAST, face=EAST, tex=wall_tex, prob=prob)
        # self.x_wall(world, NORTHEAST, face=EAST, tex=wall_tex, prob=prob)

        # if self._randflags[1]:
        # self.x_wall(world, NORTHWEST, face=NORTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, NORTH + NORTH, face=NORTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, NORTHEAST, face=NORTH, tex=wall_tex, prob=prob)

        # self.x_wall(world, SOUTHWEST, face=SOUTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTH + SOUTH, face=SOUTH, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTHEAST, face=SOUTH, tex=wall_tex, prob=prob)

        # self.x_wall(world, NORTHEAST, face=EAST, tex=wall_tex, prob=prob)
        # self.x_wall(world, EAST + EAST, face=EAST, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTHEAST, face=EAST, tex=wall_tex, prob=prob)

        # self.x_wall(world, NORTHWEST, face=WEST, tex=wall_tex, prob=prob)
        # self.x_wall(world, WEST + WEST, face=WEST, tex=wall_tex, prob=prob)
        # self.x_wall(world, SOUTHWEST, face=WEST, tex=wall_tex, prob=prob)


class OffsetTest(_LargeRoom):
    _height = 1
    _randflags = ()

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)

    def render(self, world, xmap):
        self.light(xmap)

        ceil_tex = TEXMAN.get_c('wall')

        # TODO: fade 0.9
        self.x('floor', world, SELF, tex=ceil_tex, size=4)
        # self.x('floor', world, SELF + NORTH * 1, tex=ceil_tex, size=4)
        # self.x('floor', world, SELF + NORTH * 2, tex=ceil_tex, size=4)
        # self.x('floor', world, SELF + NORTH * 3, tex=ceil_tex, size=4)
        # self.x('floor', world, SELF + NORTH * 4, tex=ceil_tex, size=4)

        # self.x('low_wall', world, SELF + ABOVE_FINE + (NORTH * 0), EAST)
        # self.x('low_wall', world, SELF + ABOVE_FINE + (NORTH * 1), SOUTH)
        # self.x('low_wall', world, SELF + ABOVE_FINE + (NORTH * 2), WEST)
        # self.x('low_wall', world, SELF + ABOVE_FINE + (NORTH * 3), NORTH)
        # self.x('low_wall', world, SELF + ABOVE_FINE + (NORTH * 4), EAST)
