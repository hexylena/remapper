import os

from redeclipse.entities.weapon import Grenade
from redeclipse.prefabs import Room, TEXMAN, LIGHTMAN
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.voxel import VoxelWorld
from redeclipse.vector import FineVector, CoarseVector
from redeclipse.vector.orientations import SELF, EAST, SOUTH, ABOVE, WEST, NORTH, n


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

        # Occupied positions are automatically calculated
        self.__positions = []

        x_dims = (
            self.vox.xmax - self.vox.xmin +
            self.boundary_additions.get('EAST', 0) +
            self.boundary_additions.get('WEST', 0)
        ) // 8
        y_dims = (
            self.vox.ymax - self.vox.ymin +
            self.boundary_additions.get('NORTH', 0) +
            self.boundary_additions.get('SOUTH', 0)
        ) // 8
        z_dims = (self.vox.zmax - self.vox.zmin) // 8

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
    room_type = 'oriented'

    # boundary_additions = {
        # 'NORTH': 5,
        # 'SOUTH': 5,
    # }

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        # self.light(xmap)
        LIGHTMAN.light(xmap, self.pos + EAST)
        # LIGHTMAN.light(xmap, position.rotate(self.orientation))

class castle_wall_section(MagicaRoom):
    name = 'castle_wall_section'
    room_type = 'platform'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_section.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
    ]


class castle_wall_corner(MagicaRoom):
    name = 'castle_wall_corner'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_corner.vox')
    room_type = 'platform'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]


class castle_wall_entry(MagicaRoom):
    name = 'castle_wall_entry'
    room_type = 'stair'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_entry.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + ABOVE},
    ]


class castle_wall_tower(MagicaRoom):
    name = 'castle_wall_tower'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_wall_tower.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE},
        {'orientation': NORTH, 'offset': NORTH + ABOVE},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE},
    ]


class castle_small_deis(MagicaRoom):
    name = 'castle_small_deis'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_small_deis.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
        {'orientation': NORTH, 'offset': NORTH},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]


class castle_large(MagicaRoom):
    name = 'castle_large'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_large.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + (NORTH * 2) + ABOVE},
        {'orientation': EAST, 'offset': (EAST * 5) + (NORTH * 2)},
        {'orientation': NORTH, 'offset': (NORTH * 5) + ABOVE + (EAST * 2)},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE + (EAST * 2)},
    ]


class castle_gate_simple(MagicaRoom):
    name = 'castle_gate_simple'
    vox_file = os.path.abspath(__file__).replace('magica.py', 'castle_gate_simple.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        # self.light(xmap)
        LIGHTMAN.light(xmap, self.pos + EAST)
        # LIGHTMAN.light(xmap, position.rotate(self.orientation))
