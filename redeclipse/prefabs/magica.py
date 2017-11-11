from redeclipse.prefabs import Room, TEXMAN
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.voxel import VoxelWorld
from redeclipse.vector import FineVector, CoarseVector
from redeclipse.vector.orientations import SELF, EAST, SOUTH, WEST, NORTH, n


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
        return '<MagicaRoom %s facing:%s,pos:%s>' % (self.name, n(self.orientation), self.pos)

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

    def colour_to_texture(self, r, g, b):
        """
        :param int c: an index from the texture atlas

        You can override this to exchange the colour replacement behaviour

        :rtype: int
        :returns: another index from the texture atlas.
        """
        c = TEXMAN.get_colour(r, g, b)
        return c

    def initialize_textures(self):
        """Re-builds the textures for this room, randomly picking new
        ones as appropriate.

        This data is then used in ``colour_to_texture``.
        """
        pass

    def render_individual_voxel(self, v, world):
        """
        Render a vector to a world (auto-translating the colour).

        This was abstracted into a separate function to permit effects such as the decaying.
        """
        (r, g, b) = self._colours[self.vox.world[v]]
        c = self.colour_to_texture(r, g, b)
        self.x('cube', world, SELF + FineVector(*v) + self._off, tex=c)

    def render(self, world, xmap):
        """
        Render the magica room to the world.
        """
        if not hasattr(self, 'model'):
            self.load_model()

        # (re)initialize textures for self.
        self.initialize_textures()

        for v in self.vox.world:
            self.render_individual_voxel(v, world)

        self.render_extra(world, xmap)
