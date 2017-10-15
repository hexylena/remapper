import os

from redeclipse.entities import Pusher
from redeclipse.prefabs import Room, TEXMAN, LIGHTMAN
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.voxel import VoxelWorld
from redeclipse.vector import FineVector, CoarseVector
from redeclipse.vector.orientations import SELF, EAST, SOUTH, ABOVE, WEST, NORTH, n, NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST
from redeclipse.vector.orientations import rotate_yaw


class MagicaRoom(Room):
    vox_file = None
    room_type = 'oriented'
    boundary_additions = {}

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
        {'orientation': NORTH, 'offset': NORTH},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]

    def __init__(self, pos, roof=False, orientation=EAST, randflags=None):
        self._off = FineVector(self.boundary_additions.get('WEST', 0), self.boundary_additions.get('SOUTH', 0), 0).rotate(orientation)
        self.orientation = orientation
        self.pos = CoarseVector(*pos)
        if randflags:
            self._randflags = randflags

    def __repr__(self):
        return '<MagicaRoom %s facing:%s>' % (self.name, n(self.orientation))

    def load_model(self):
        self.model = Magicavoxel.from_file(self.vox_file)
        self.vox = VoxelWorld()
        self._colours = {}
        for vox in self.model.model_voxels.voxels:
            self.vox.set_point(vox.x, vox.y, vox.z, vox.c)
            # For every colour in the palette, register it with the current
            # class's colour atlas (non-global colour atlas).
            for idx, colour in enumerate(self.model.palette.colours):
                self._colours[idx] = (colour.r / 255, colour.g / 255, colour.b / 255)

        self.__doors = []
        for door in self.doors:
            self.__doors.append(door)

        # We'll calculate a unique list of coarse vectors which are occupied
        self.__positions = []
        # Sometimes we need to offset our model because it doesn't fully
        # extend. We get the western + southern side additions which should
        # offset every voxel.
        offset = FineVector(self.boundary_additions.get('WEST', 0), self.boundary_additions.get('SOUTH', 0), 0)
        # Now looping over every voxel
        for (vox, value) in self.vox.world.items():
            # We offset it and convert it to a coarse version ( // 8)
            tmp = (FineVector(*vox) + offset).coarse()
            # And ensure that our list is unique
            if tmp not in self.__positions:
                self.__positions.append(tmp)

    def _get_doorways(self):
        if not hasattr(self, 'model'):
            self.load_model()
        return self.__doors

    def _get_positions(self):
        if not hasattr(self, 'model'):
            self.load_model()
        return self.__positions

    def render_extra(self, world, xmap):
        self.light(xmap)

    def render(self, world, xmap):
        """
        Render the magic room to the world.
        """
        if not hasattr(self, 'model'):
            self.load_model()

        for v in self.vox.world:
            (r, g, b) = self._colours[self.vox.world[v]]
            c = TEXMAN.get_colour(r, g, b)
            self.x('cube', world, SELF + FineVector(*v) + self._off, tex=c)

        self.render_extra(world, xmap)


class castle_gate(MagicaRoom):
    name = 'castle_gate'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_gate.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH + ABOVE).rotate(self.orientation))


class castle_gate_simple(MagicaRoom):
    name = 'castle_gate_simple'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_gate_simple.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH + ABOVE).rotate(self.orientation))


class castle_large(MagicaRoom):
    name = 'castle_large'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_large.vox')
    room_type = 'setpiece_large'

    doors = [
        {'orientation': WEST, 'offset': WEST + (NORTH * 2) + ABOVE},
        {'orientation': EAST, 'offset': (EAST * 5) + (NORTH * 2) + ABOVE},
        {'orientation': NORTH, 'offset': (NORTH * 5) + ABOVE + (EAST * 2)},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE + (EAST * 2)},
    ]

    def render_extra(self, world, xmap):
        large_center = EAST + NORTH + EAST + NORTH
        LIGHTMAN.light(xmap, self.pos + (large_center).rotate(self.orientation), size_factor=2)
        LIGHTMAN.light(xmap, self.pos + (large_center + ABOVE).rotate(self.orientation), size_factor=2)
        LIGHTMAN.light(xmap, self.pos + (large_center + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)

        LIGHTMAN.light(xmap, self.pos + (large_center + NORTHWEST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTHWEST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + NORTHEAST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTHEAST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)

        LIGHTMAN.light(xmap, self.pos + (large_center + NORTH + NORTH + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTH + SOUTH + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + EAST + EAST + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + WEST + WEST + ABOVE).rotate(self.orientation), size_factor=1.5)


class castle_small_deis(MagicaRoom):
    name = 'castle_small_deis'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_small_deis.vox')
    room_type = 'setpiece_small'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
        {'orientation': NORTH, 'offset': NORTH},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)


class castle_wall_corner(MagicaRoom):
    name = 'castle_wall_corner'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_corner.vox')
    room_type = 'hallway'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)


class castle_wall_end_cliff(MagicaRoom):
    name = 'castle_wall_end_cliff'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_end_cliff.vox')
    room_type = 'endcap'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class castle_wall_entry(MagicaRoom):
    name = 'castle_wall_entry'
    room_type = 'stair'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_entry.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class castle_wall_section(MagicaRoom):
    name = 'castle_wall_section'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class castle_wall_section_endcap(MagicaRoom):
    name = 'castle_wall_section_endcap'
    room_type = 'endcap'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section_endcap.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_long(MagicaRoom):
    name = 'castle_wall_section_long'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section_long.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_long_damaged(MagicaRoom):
    name = 'castle_wall_section_long_damaged'
    room_type = 'hallway_setpiece'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section_long_damaged.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_tjoint(MagicaRoom):
    name = 'castle_wall_section_tjoint'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section_tjoint.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
        {'orientation': SOUTH, 'offset': EAST + NORTH + NORTH + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_tower(MagicaRoom):
    name = 'castle_wall_tower'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_tower.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE},
        {'orientation': NORTH, 'offset': NORTH + ABOVE},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class wooden_bridge(MagicaRoom):
    name = 'wooden_bridge'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'wooden_bridge.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class dungeon_2x2(MagicaRoom):
    name = 'dungeon_2x2'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'dungeon_2x2.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH},
    ]


class dungeon_junction(MagicaRoom):
    name = 'dungeon_junction'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'dungeon_junction.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + NORTH},
        {'orientation': WEST, 'offset': WEST},

        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH + NORTH},
        {'orientation': EAST, 'offset': EAST + EAST + EAST},

        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST).rotate(self.orientation), size_factor=1)
        LIGHTMAN.light(xmap, self.pos + (NORTH + NORTH).rotate(self.orientation), size_factor=1)
        LIGHTMAN.light(xmap, self.pos + (NORTH + NORTH + EAST + EAST).rotate(self.orientation), size_factor=1)


class dungeon_stair2(MagicaRoom):
    name = 'dungeon_stair2'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'dungeon_stair2.vox')
    room_type = 'stair'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + ABOVE},
    ]


class dungeon_walkway(MagicaRoom):
    name = 'dungeon_walkway'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'dungeon_walkway.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
    ]


class dungeon_walkway3(MagicaRoom):
    name = 'dungeon_walkway3'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'dungeon_walkway3.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + EAST},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST).rotate(self.orientation), size_factor=2)


class station_tube1(MagicaRoom):
    name = 'station_tube1'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_tube1.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
    ]


class station_tube3(MagicaRoom):
    name = 'station_tube3'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_tube3.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + EAST},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (ABOVE + EAST).rotate(self.orientation), size_factor=2)


class station_tube_jumpx(MagicaRoom):
    name = 'station_tube_jumpx'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_tube_jumpx.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},

        {'orientation': WEST, 'offset': WEST + ABOVE + ABOVE + NORTH},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + ABOVE + ABOVE + NORTH},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + ABOVE + ABOVE + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH + ABOVE + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH + ABOVE).rotate(self.orientation), size_factor=2)

        pusher_a = Pusher(
            xyz=self.pos + (EAST + NORTH + FineVector(4, 5, 12)).rotate(self.orientation),
            pitch=90,
            maxrad=1,
            yaw=rotate_yaw(0, self.orientation),
            force=230,
        )
        xmap.ents.append(pusher_a)


class station_tubeX(MagicaRoom):
    name = 'station_tubeX'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_tubeX.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation))


class station_endcap(MagicaRoom):
    name = 'station_endcap'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_endcap.vox')
    room_type = 'endcap'

    doors = [
        {'orientation': WEST, 'offset': WEST},
    ]


class station_right(MagicaRoom):
    name = 'station_right'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_right.vox')
    room_type = 'hallway'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]


class station_ring(MagicaRoom):
    name = 'station_ring'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_ring.vox')
    room_type = 'setpiece_large'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + NORTH},
        {'orientation': EAST, 'offset': (EAST * 5) + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': (EAST * 2) + SOUTH},
        {'orientation': NORTH, 'offset': (EAST * 2) + (NORTH * 5)},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST * 2).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + (NORTH * 2).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + ((EAST * 2) + (NORTH * 4)).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + ((EAST * 4) + (NORTH * 2)).rotate(self.orientation))


class station_ring_vertical(MagicaRoom):
    name = 'station_ring_vertical'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_ring_vertical.vox')
    room_type = 'setpiece_large'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE + ABOVE},
        {'orientation': EAST, 'offset': (EAST * 5) + ABOVE + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ((EAST * 0.5) + (ABOVE * 3)).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + ((EAST * 3.5) + (ABOVE * 3)).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + ((EAST * 2) + (ABOVE * 4)).rotate(self.orientation))


class station_sphere(MagicaRoom):
    name = 'station_sphere'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_sphere.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + ABOVE},
        {'orientation': EAST, 'offset': (EAST * 3) + NORTH + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH + ABOVE},
        {'orientation': SOUTH, 'offset': EAST + SOUTH + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation), size_factor=3)


class station_sphere_slice(MagicaRoom):
    name = 'station_sphere_slice'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_sphere_slice.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH},
        {'orientation': EAST, 'offset': EAST * 3 + NORTH},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation), size_factor=2)


class station_stair2(MagicaRoom):
    name = 'station_stair2'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'station_stair2.vox')
    room_type = 'stair'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST * 2 + ABOVE},
    ]
