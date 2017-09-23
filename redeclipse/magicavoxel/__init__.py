import os
import glob
import yaml
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.vector import FineVector
from redeclipse.vector.orientations import SELF, NORTH, SOUTH, EAST, WEST, ABOVE, BELOW  # NOQA
from redeclipse.textures import AutomatedMagicaTextureManager
from redeclipse.voxel import VoxelWorld
PATH = os.path.abspath(os.path.dirname(__file__))
ROOMS = os.path.join(PATH, 'rooms')


def autodiscover():
    """
    Automatically load yml/vox pairs from the module.
    """
    rooms = []
    for yml in glob.glob(os.path.join(ROOMS, '*.yml')):
        room_class = MagicaRoom(yml, yml.replace('.yml', '.vox'))
        rooms.append(room_class)
    return rooms
