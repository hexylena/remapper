import os
from redeclipse.prefabs.magica import MagicaRoom
from redeclipse.vector.orientations import EAST, SOUTH, ABOVE, WEST, NORTH
from redeclipse.prefabs import LIGHTMAN


class dungeon_2x2(MagicaRoom):
    name = 'dungeon_2x2'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'dungeon_2x2.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH},
    ]


class dungeon_junction(MagicaRoom):
    name = 'dungeon_junction'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'dungeon_junction.vox')
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
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'dungeon_stair2.vox')
    room_type = 'stair'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + ABOVE},
    ]


class dungeon_walkway(MagicaRoom):
    name = 'dungeon_walkway'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'dungeon_walkway.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
    ]


class dungeon_walkway3(MagicaRoom):
    name = 'dungeon_walkway3'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'dungeon_walkway3.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + EAST},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST).rotate(self.orientation), size_factor=2)
