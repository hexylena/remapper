from redeclipse.entities import Light, PlayerSpawn, Pusher
from redeclipse.entities.model import MapModel
from redeclipse.entities.weapon import Grenade
from redeclipse.textures import PrimaryThemedTextureManager
# MinecraftThemedTextureManager, DefaultThemedTextureManager, PaperThemedTextureManager
from redeclipse.lighting import PositionBasedLightManager
from redeclipse.prefabs.distributions import UniformDistributionManager
# TowerDistributionManager, PlatformDistributionManager
from redeclipse.prefabs.construction_kit import ConstructionKitMixin
from redeclipse.vector import CoarseVector, FineVector
from redeclipse.vector.orientations import rotate_yaw, SELF, \
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

    def __init__(self, pos, orientation=EAST, randflags=None):
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

        self.x('floor', world, SELF, tex=tex)
        self.x('ceiling', world, SELF, tex=tex)


class _3X3Room(Room):
    """Another special case of room, though this probably does not need to be.
    AltarRoom is currently the only user."""
    room_type = 'platform_setpiece'

    def __init__(self, pos, orientation=EAST, randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = CoarseVector(*pos)
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
    def __init__(self, pos, orientation=EAST, randflags=None):
        """Init is kept separate from rendering, because init sets self.pos,
        and we use that when calling self.get_positions(), which is required as
        part of placement, we wouldn't want to place a partial room."""
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.x('rectangular_prism', world, SELF + FineVector(2, 2, 0), FineVector(4, 4, 1), tex=TEXMAN.get_c('accent'))

        g = Grenade(
            xyz=self.pos + TILE_CENTER + ABOVE_FINE
        )
        xmap.ents.append(g)


class TestRoom2(Room):
    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.x('floor', world, SELF, tex=floor_tex)
        self.x('floor', world, SELF + EAST, tex=TEXMAN.get_c('accent'))

        self.x('wall', world, SELF, SOUTH, tex=TEXMAN.get('blue'))
        self.x('wall', world, SELF, NORTH, tex=TEXMAN.get('red'))
        self.x('wall', world, SELF, WEST, tex=TEXMAN.get('yellow'))
        self.x('wall', world, SELF, EAST, tex=TEXMAN.get('black'))

        self.x('rectangular_prism', world, SELF, FineVector(2, 4, 1), tex=TEXMAN.get_c('accent'))
        self.x('ring', world, ABOVE, 8, tex=TEXMAN.get_c('accent'))


class NLongCorridor(Room):
    room_type = 'hallway'
    _randflags = (
        True,  # A
        True,  # B; length=a<<1 | b
        True,  # CoverA
        True,  # CoverB
    )

    def __init__(self, pos, orientation=EAST, randflags=None):
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
        wall_tex = TEXMAN.get_c('wall')

        for i in range(self.length):
            # Add a floor south of us.
            self.x('floor', world, EAST * i, tex=floor_tex)
            self.x('low_wall', world, EAST * i, SOUTH, tex=wall_tex)
            self.x('low_wall', world, EAST * i, NORTH, tex=wall_tex)

        self.x('dotted_column', world, FineVector(0, 0, 3), EAST, 8 * self.length, tex=wall_tex, on=2, off=1)
        self.x('dotted_column', world, FineVector(0, 7, 3), EAST, 8 * self.length, tex=wall_tex, on=2, off=1)

        self.light(xmap)

    def _get_positions(self):
        positions = [SELF]

        # Same logic as init
        for i in range(1, self.length):
            positions.append(EAST * i)

        return positions

    def _get_doorways(self):
        return [
            WEST,
            EAST * self.length
        ]


class Corridor2way(Room):
    room_type = 'hallway'
    _randflags = (
        True,  # roof
        True,  # no wall / low wall
    )

    def __init__(self, pos, orientation=EAST, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        self.light(xmap)
        floor_tex = TEXMAN.get_c('floor')

        self.x('floor', world, SELF, tex=floor_tex)
        if self._randflags[0]:
            self.x('ceiling', world, SELF, tex=floor_tex)

        if self._randflags[1]:
            self.x('low_wall', world, SELF, NORTH)
            self.x('low_wall', world, SELF, SOUTH)

    def _get_doorways(self):
        return [
            WEST,
            EAST
        ]


class JumpCorridor3(Room):
    room_type = 'hallway_jump'

    def __init__(self, pos, orientation=EAST, randflags=None):
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
            xyz=self.pos + FineVector(7, 4, 1).rotate(self.orientation),
            maxrad=15 * SIZE_OFFSET,
            yaw=rotate_yaw(270, self.orientation),
            force=175 * SIZE_OFFSET,
        )

        pusher_b = Pusher(
            xyz=self.pos + (EAST + EAST + FineVector(1, 4, 1)).rotate(self.orientation),
            maxrad=15 * SIZE_OFFSET,
            yaw=rotate_yaw(90, self.orientation),
            force=175 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_a)
        xmap.ents.append(pusher_b)

        self.x('floor', world, SELF, tex=floor_tex)
        self.x('floor', world, SELF + EAST + EAST, tex=floor_tex)

        self.x('low_wall', world, SELF, NORTH, tex=wall_tex)
        self.x('low_wall', world, SELF, SOUTH, tex=wall_tex)
        self.x('low_wall', world, SELF + EAST + EAST, NORTH, tex=wall_tex)
        self.x('low_wall', world, SELF + EAST + EAST, SOUTH, tex=wall_tex)

        self.x('rectangular_prism', world, FineVector(6, 2, 0), FineVector(2, 4, 1), tex=accent_tex)
        self.x('rectangular_prism', world, EAST + EAST + FineVector(0, 2, 0), FineVector(2, 4, 1), tex=accent_tex)

    def _get_positions(self):
        positions = []
        for i in range(3):
            positions.append(EAST * i)
        return positions

    def _get_doorways(self):
        return [
            WEST,
            EAST * 3
        ]


class JumpCorridorVertical(Room):
    room_type = 'vertical'
    _randflags = (
        True,  # extra section
    )

    def __init__(self, pos, orientation=EAST, roof=False, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        self.roof = roof
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        self.x('floor', world, SELF, tex=floor_tex)
        self.x('ceiling', world, SELF + ABOVE + ABOVE, tex=floor_tex)
        self.light(xmap)

        pusher_a = Pusher(
            xyz=self.pos + FineVector(5, 4, 1).rotate(self.orientation),
            pitch=74,
            yaw=rotate_yaw(270, self.orientation),
            force=400 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_a)

        pusher_b = Pusher(
            xyz=self.pos + FineVector(6, 4, 17).rotate(self.orientation),
            pitch=40,
            yaw=rotate_yaw(90, self.orientation),
            force=200 * SIZE_OFFSET,
        )
        xmap.ents.append(pusher_b)

        (a, b, c) = self.pos

        self.x('wall', world, SELF, face=SOUTH, tex=wall_tex)
        self.x('wall', world, SELF, face=NORTH, tex=wall_tex)
        self.x('wall', world, SELF, face=EAST, tex=wall_tex)

        self.x('wall', world, SELF + ABOVE, face=NORTH, tex=wall_tex)
        self.x('wall', world, SELF + ABOVE, face=SOUTH, tex=wall_tex)
        self.x('wall', world, SELF + ABOVE, face=EAST, tex=wall_tex)
        self.x('wall', world, SELF + ABOVE, face=WEST, tex=wall_tex)

        self.x('wall', world, SELF + ABOVE + ABOVE, face=SOUTH, tex=wall_tex)
        self.x('wall', world, SELF + ABOVE + ABOVE, face=NORTH, tex=wall_tex)
        self.x('wall', world, SELF + ABOVE + ABOVE, face=EAST, tex=wall_tex)

        self.x('rectangular_prism', world, FineVector(4, 2, 0), FineVector(2, 4, 1), tex=accent_tex)
        self.x('rectangular_prism', world, FineVector(7, 2, 12), FineVector(1, 4, 2), tex=accent_tex)
        self.x('rectangular_prism', world, FineVector(0, 1, 0) + ABOVE + ABOVE, FineVector(1, 6, 1), tex=accent_tex)

    def _get_positions(self):
        return [
            SELF,
            SELF + ABOVE,
            SELF + ABOVE + ABOVE,
        ]

    def _get_doorways(self):
        return [
            WEST,
            WEST + ABOVE + ABOVE
        ]


class JumpCorridorVerticalCenter(JumpCorridorVertical):
    length = 1
    _randflags = (
        True,  # Tall
    )

    def __init__(self, pos, orientation=EAST, roof=False, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        self.roof = roof
        if randflags:
            self._randflags = randflags
        if self._randflags[0]:
            self.length = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        self.x('floor', world, SELF, tex=floor_tex)
        self.light(xmap)

        (a, b, c) = self.pos
        # Walls
        for i in range(1, self.length + 1):
            self.x('wall', world, SELF + (ABOVE * i), face=NORTH, tex=wall_tex)
            self.x('wall', world, SELF + (ABOVE * i), face=SOUTH, tex=wall_tex)
            self.x('wall', world, SELF + (ABOVE * i), face=EAST, tex=wall_tex)
            self.x('wall', world, SELF + (ABOVE * i), face=WEST, tex=wall_tex)

        self.x('ring', world, SELF + (ABOVE * (i + 1)), 8, tex=accent_tex)

        # Red markers
        self.x('rectangular_prism', world, FineVector(2, 2, 0), FineVector(4, 4, 1), tex=accent_tex)

        force = 460 * SIZE_OFFSET
        if self.length == 2:
            force = 700 * SIZE_OFFSET

        pusher_a = Pusher(
            xyz=self.pos + FineVector(4, 4, 1).rotate(self.orientation),
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

    def __init__(self, pos, orientation=EAST, randflags=None):
        self.orientation = orientation
        self.pos = CoarseVector(*pos)
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        column_tex = TEXMAN.get_c('column')

        self.x('floor', world, SELF, tex=floor_tex)
        if self._randflags[0]:
            self.x('ceiling', world, SELF, tex=floor_tex)

        if not self._randflags[1] and not self._randflags[2]:
            pass
        elif self._randflags[1] and not self._randflags[2]:
            self.x('column', world, FineVector(0, 0, 0), ABOVE, 8, tex=column_tex)
            self.x('column', world, FineVector(0, 7, 0), ABOVE, 8, tex=column_tex)
            self.x('column', world, FineVector(7, 0, 0), ABOVE, 8, tex=column_tex)
            self.x('column', world, FineVector(7, 7, 0), ABOVE, 8, tex=column_tex)
        elif not self._randflags[1] and self._randflags[2]:
            self.x('column', world, FineVector(0, 0, 0), ABOVE, 3, tex=column_tex)
            self.x('column', world, FineVector(0, 7, 0), ABOVE, 3, tex=column_tex)
            self.x('column', world, FineVector(7, 0, 0), ABOVE, 3, tex=column_tex)
            self.x('column', world, FineVector(7, 7, 0), ABOVE, 3, tex=column_tex)

        self.light(xmap)


class SpawnRoom(Room):
    room_type = 'platform_setpiece'
    _randflags = (
        True,  # Two sides open
    )

    def __init__(self, pos, roof=None, orientation=EAST, randflags=None):
        self.pos = CoarseVector(*pos)
        self.orientation = orientation
        if randflags:
            self._randflags = randflags

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        wall_tex = TEXMAN.get_c('wall')
        accent_tex = TEXMAN.get_c('accent')

        # Floor and ceiling
        self.x('floor', world, SELF, tex=floor_tex)
        self.x('ceiling', world, SELF, tex=floor_tex)

        # Sometimes we add a 'back' to it
        if not self._randflags[0]:
            self.x('wall', world, SELF, face=WEST, tex=accent_tex)

        # Always add at least two walls for cover
        self.x('wall', world, SELF, face=NORTH, tex=wall_tex)
        self.x('wall', world, SELF, face=SOUTH, tex=wall_tex)

        xmap.ents.append(PlayerSpawn(
            xyz=self.pos + TILE_CENTER + FineVector(0, 0, 1)
        ))

        self.light(xmap)

    def _get_doorways(self):
        doors = [EAST]
        if self._randflags[0]:
            doors += [WEST]
        return doors


class _LargeRoom(_3X3Room):
    _height = 1

    def __init__(self, pos, roof=False, orientation=EAST, randflags=None):
        # Push the position
        self.orientation = orientation
        # We (arbitrarily) define pos as the middle of one side. We add
        # orientation to ensure we're not in the room center, we're on
        # west corner.
        self.pos = CoarseVector(*pos) + self.orientation
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
        self.x('floor', world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[1]:
            self.x('ceiling', world, SOUTHWEST + ABOVE, tex=floor_tex, size=24)

        for i in range(-8, 16):
            for j in range(-8, 16):
                if random.random() < 0.05:
                    if 2 <= i <= 4 and 3 <= j <= 5:
                        # Do not occupy same space as light.
                        continue

                    if False and self._randflags[0]:
                        length = FineVector(1, 1, 8 * self._height)
                        voff = ABOVE_FINE
                    else:
                        offset = random.randint(1, 8 * self._height / 2)
                        length = FineVector(1, 1, (8 * self._height) - (2 * offset))
                        voff = (ABOVE_FINE * offset)

                    self.x('rectangular_prism', world, FineVector(i, j, 0) + voff, length, tex=TEXMAN.get_c('column'))

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
        self.x('floor', world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[0]:
            self.x('ceiling', world, SOUTHWEST + (ABOVE * (self._height - 1)), tex=floor_tex, size=24)

        def box_size():
            if self._randflags[2]:
                return FineVector(
                    random.randint(4, 7),
                    random.randint(4, 7),
                    random.randint(4, 7)
                )
            else:
                return FineVector(6, 6, 6)

        self.x('rectangular_prism', world, FineVector(7, 7, 0), box_size(), tex=TEXMAN.get_c('accent'))
        self.x('rectangular_prism', world, FineVector(-5, 7, 0), box_size(), tex=TEXMAN.get_c('accent'))
        self.x('rectangular_prism', world, FineVector(7, -5, 0), box_size(), tex=TEXMAN.get_c('accent'))
        self.x('rectangular_prism', world, FineVector(-5, -5, 0), box_size(), tex=TEXMAN.get_c('accent'))

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
        self.x('floor', world, SOUTHWEST, tex=floor_tex, size=24)
        if self._randflags[0]:
            self.x('ceiling', world, SOUTHWEST + (ABOVE * (self._height - 1)), tex=floor_tex, size=24)

        self.x('rectangular_prism', world, FineVector(15, 15, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x('rectangular_prism', world, FineVector(-8, 15, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x('rectangular_prism', world, FineVector(15, -8, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
        self.x('rectangular_prism', world, FineVector(-8, -8, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)

        if self._randflags[3]:
            self.x('rectangular_prism', world, FineVector(2, 3, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(4, 2, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(3, 5, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(5, 4, 1), FineVector(1, 1, (8 * self._height) - 2), tex=column_tex)

        for i in range(1, self._height * 8 - 1, 2):
            self.x('ring', world, FineVector(-4, -4, i), 16, tex=accent_tex)
            if not self._randflags[2] and self._randflags[4]:
                self.x('ring', world, FineVector(-2, -2, i), 12, tex=accent_tex)

        if self._randflags[2] and self._randflags[4]:
            for i in range(2, self._height * 8 - 1, 2):
                self.x('ring', world, FineVector(-2, -2, i), 12, tex=accent_tex)

        self.x('rectangular_prism', world, FineVector(-4, 2, 1), FineVector(3, 4, 8), subtract=True)
        self.x('rectangular_prism', world, FineVector(2, -4, 1), FineVector(4, 3, 8), subtract=True)
        self.x('rectangular_prism', world, FineVector(9, 2, 1), FineVector(3, 4, 8), subtract=True)
        self.x('rectangular_prism', world, FineVector(2, 9, 1), FineVector(4, 3, 8), subtract=True)

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
        self._height = 2

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')
        accent_tex = TEXMAN.get_c('accent')
        column_tex = TEXMAN.get_c('column')

        self.light(xmap)
        # size = 24
        self.x('floor', world, SOUTHWEST, tex=floor_tex, size=24)

        if self._randflags[2]:
            self.x('rectangular_prism', world, FineVector(15, 15, 1), FineVector(1, 1, 8), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(-8, 15, 1), FineVector(1, 1, 8), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(15, -8, 1), FineVector(1, 1, 8), tex=column_tex)
            self.x('rectangular_prism', world, FineVector(-8, -8, 1), FineVector(1, 1, 8), tex=column_tex)

        self.x('floor', world, SOUTHWEST + FineVector(4, 4, 1), tex=accent_tex, size=16)
        self.x('floor', world, SOUTHWEST + FineVector(5, 5, 2), tex=floor_tex, size=14)

        if self._randflags[1]:
            self.x('ring', world, FineVector(-2, -2, 11), 12, tex=accent_tex)
            self.x('ring', world, FineVector(-4, -4, 10), 16, tex=accent_tex)
            self.x('ring', world, FineVector(-6, -6, 9), 20, tex=accent_tex)
            self.x('ring', world, FineVector(-8, -8, 8), 24, tex=accent_tex)

        if self._randflags[0]:
            tree = MapModel(
                xyz=self.pos + FineVector(4, 4, 3).rotate(self.orientation),
                yaw=rotate_yaw(270, self.orientation),
                type=124
            )
            xmap.ents.append(tree)


class Stair(Room):
    room_type = 'stair'

    _randflags = (
        True,  # Hand rail
    )

    def render(self, world, xmap):
        floor_tex = TEXMAN.get_c('floor')

        self.light(xmap)

        self.x('rectangular_prism', world, FineVector(0, 0, 0), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(1, 0, 1), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(2, 0, 2), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(3, 0, 3), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(4, 0, 4), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(5, 0, 5), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(6, 0, 6), FineVector(1, 8, 1), tex=floor_tex)
        self.x('rectangular_prism', world, FineVector(7, 0, 7), FineVector(1, 8, 1), tex=floor_tex)

        # if self._randflags[0]:
            # self.x('interpolate', world, SELF, FineVector(0, 0, 2), FineVector(7, 0, 9), tex=floor_tex)

    def _get_doorways(self):
        return [WEST, EAST + ABOVE]

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

        self.x('floor', world, NORTH, tex=floor_tex)
        self.x('floor', world, SELF, tex=floor_tex)
        self.x('floor', world, SOUTH, tex=floor_tex)

        self.x('floor', world, EAST + ABOVE, tex=floor_tex)
        self.x('floor', world, SELF + ABOVE, tex=floor_tex)
        self.x('floor', world, WEST + ABOVE, tex=floor_tex)

        if self._randflags[0]:
            self.x('floor', world, NORTH + ABOVE + ABOVE, tex=floor_tex)
            self.x('floor', world, SELF + ABOVE + ABOVE, tex=floor_tex)
            self.x('floor', world, SOUTH + ABOVE + ABOVE, tex=floor_tex)

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

        self.x('floor', world, SELF, tex=floor_tex)
        self.x('floor', world, NORTH, tex=floor_tex)
        self.x('floor', world, SOUTH, tex=floor_tex)
        self.x('floor', world, EAST, tex=floor_tex)
        self.x('floor', world, WEST, tex=floor_tex)

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
            self.x('floor', world, SOUTHWEST, tex=tex1, size=24)

        # Corners are up 1
        self.x('floor', world, NORTHEAST + HALF_HEIGHT, tex=tex1)
        self.x('floor', world, SOUTHWEST + HALF_HEIGHT, tex=tex1)

        self.x('floor', world, NORTHWEST + ABOVE, tex=tex2)
        self.x('floor', world, SOUTHEAST + ABOVE, tex=tex2)

        self.x('floor', world, NORTH + ABOVE + HALF_HEIGHT, tex=tex1)
        self.x('floor', world, SOUTH + ABOVE + HALF_HEIGHT, tex=tex1)

        self.x('floor', world, WEST + ABOVE + ABOVE, tex=tex2)
        self.x('floor', world, EAST + ABOVE + ABOVE, tex=tex2)

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
        self.x('floor', world, SOUTHWEST, tex=floor_tex, size=24)


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
        self.x('floor', world, SOUTHWEST, tex=ceil_tex, size=24, prob=0.9)
        if self._randflags[1]:
            self.x('ceiling', world, SOUTHWEST + ABOVE, tex=ceil_tex, size=24, prob=prob)
        else:
            self.x('ceiling', world, SOUTHWEST, tex=ceil_tex, size=24, prob=prob)

        # wall_tex = 644
        # TODO: Fix this bug.
        self.x('wall', world, NORTHWEST, face=NORTH, tex=wall_tex, prob=prob)
        self.x('wall', world, NORTHEAST, face=NORTH, tex=wall_tex, prob=prob)

        self.x('wall', world, SOUTHWEST, face=SOUTH, tex=wall_tex, prob=prob)
        self.x('wall', world, SOUTHEAST, face=SOUTH, tex=wall_tex, prob=prob)

        self.x('wall', world, NORTHWEST, face=WEST, tex=wall_tex, prob=prob)
        self.x('wall', world, SOUTHWEST, face=WEST, tex=wall_tex, prob=prob)

        self.x('wall', world, SOUTHEAST, face=EAST, tex=wall_tex, prob=prob)
        self.x('wall', world, NORTHEAST, face=EAST, tex=wall_tex, prob=prob)

        if self._randflags[1]:
            self.x('wall', world, ABOVE + NORTHWEST, face=NORTH, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + NORTH, face=NORTH, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + NORTHEAST, face=NORTH, tex=wall_tex, prob=prob)

            self.x('wall', world, ABOVE + SOUTHWEST, face=SOUTH, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + SOUTH, face=SOUTH, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + SOUTHEAST, face=SOUTH, tex=wall_tex, prob=prob)

            self.x('wall', world, ABOVE + NORTHWEST, face=WEST, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + WEST, face=WEST, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + SOUTHWEST, face=WEST, tex=wall_tex, prob=prob)

            self.x('wall', world, ABOVE + SOUTHEAST, face=EAST, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + EAST, face=EAST, tex=wall_tex, prob=prob)
            self.x('wall', world, ABOVE + NORTHEAST, face=EAST, tex=wall_tex, prob=prob)

