import os
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST, ABOVE
from redeclipse.prefabs import MagicaRoom


class castle_gate(MagicaRoom):
    vox_file = os.path.abspath(__file__).replace('.py', '.vox')
    name = 'castle_gate'
    room_type = 'oriented'
    doors = [
        WEST + ABOVE,
        EAST + EAST + EAST + ABOVE,
        EAST + NORTH,
        EAST + SOUTH
    ]
