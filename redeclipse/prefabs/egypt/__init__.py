import os
# from redeclipse.prefabs import TEXMAN
from redeclipse.prefabs.magica import MagicaRoom
# from redeclipse.entities import Pusher
# from redeclipse.entities import PlayerSpawn
# from redeclipse.entities.weapon import Grenade, Shotgun
# from redeclipse.vector import FineVector
from redeclipse.vector.orientations import EAST, SOUTH, ABOVE, WEST, NORTH
# from redeclipse.vector.orientations import NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST
# from redeclipse.vector.orientations import TILE_CENTER, ABOVE_FINE
# from redeclipse.vector.orientations import rotate_yaw
# from redeclipse.entities import TeamFlag
# from redeclipse.vector.orientations import rotate_yaw
# from redeclipse.prefabs import LIGHTMAN


class stair(MagicaRoom):
    name = 'stair'
    room_type = 'stair'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'stair.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + ABOVE},
    ]


class stair_toplatform(MagicaRoom):
    name = 'stair_toplatform'
    room_type = 'stair'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'stair_toplatform.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST + EAST + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + ABOVE},
        {'orientation': SOUTH, 'offset': EAST + SOUTH + ABOVE},
    ]


class statue(MagicaRoom):
    name = 'statue'
    room_type = 'platform_setpiece'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'statue.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]


class statue_cat(MagicaRoom):
    name = 'statue_cat'
    room_type = 'platform_setpiece'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'statue_cat.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': WEST, 'offset': WEST + NORTH},
        {'orientation': WEST, 'offset': WEST + NORTH + NORTH},

        {'orientation': SOUTH, 'offset': SOUTH},
        {'orientation': SOUTH, 'offset': SOUTH + EAST},
        {'orientation': SOUTH, 'offset': SOUTH + EAST + EAST},
        {'orientation': SOUTH, 'offset': SOUTH + EAST + EAST + EAST},

        {'orientation': NORTH, 'offset': NORTH + NORTH + NORTH},
        {'orientation': NORTH, 'offset': NORTH + NORTH + NORTH + EAST},
        {'orientation': NORTH, 'offset': NORTH + NORTH + NORTH + EAST + EAST},
        {'orientation': NORTH, 'offset': NORTH + NORTH + NORTH + EAST + EAST + EAST},

        {'orientation': EAST, 'offset': EAST + EAST + EAST + EAST},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + EAST + NORTH},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + EAST + NORTH + NORTH},
    ]


class house_2x2(MagicaRoom):
    name = 'house_2x2'
    room_type = 'platform'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'house_2x2.vox')

    doors = [
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH},
    ]


class house_2x2x3(MagicaRoom):
    name = 'house_2x2x3'
    room_type = 'platform'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'house_2x2x3.vox')

    doors = [
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH},
    ]


class gate(MagicaRoom):
    name = 'gate'
    room_type = 'platform'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'gate.vox')

    doors = [
        {'orientation': NORTH, 'offset': EAST + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]
