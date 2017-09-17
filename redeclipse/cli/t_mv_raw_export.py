#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel import to_magicavoxel

from redeclipse.vector import CoarseVector, FineVector, AbsoluteVector
from redeclipse.vector.orientations import rotate_yaw, SELF, \
    SOUTH, NORTH, WEST, EAST, ABOVE, \
    ABOVE_FINE, NORTHWEST, \
    NORTHEAST, SOUTHWEST, SOUTHEAST, TILE_CENTER, HALF_HEIGHT
# from redeclipse.skybox import MinecraftSky
from redeclipse.vector import CoarseVector, FineVector
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False, re_out=False):
    mymap = parse(mpz_in.name)
    upm = UnusedPositionManager(size, mirror=True, noclip=True)
    v = VoxelWorld(size=size)
    Room = p.noway

    kwargs = {}
    e = Room(pos=CoarseVector(1, 1, 1), orientation=EAST, **kwargs)

    e.render(v, mymap)
    print(v.xmax, v.xmin)
    print(v.ymax, v.ymin)
    print(v.zmax, v.zmin)

    p.TEXMAN.emit_conf(mpz_out)
    p.TEXMAN.copy_data()
    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    parser.add_argument('--re_out', action='store_true', help="Redeclipse output instead of magica voxel")
    args = parser.parse_args()
    main(**vars(args))
