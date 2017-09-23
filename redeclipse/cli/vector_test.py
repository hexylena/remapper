#!/usr/bin/env python
import copy
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel import autodiscover, TEXMAN
from redeclipse.magicavoxel.writer import to_magicavoxel

from redeclipse.vector import CoarseVector, FineVector, AbsoluteVector
from redeclipse.vector.orientations import rotate_yaw, SELF, \
    SOUTH, NORTH, WEST, EAST, ABOVE, \
    ABOVE_FINE, NORTHWEST, \
    NORTHEAST, SOUTHWEST, SOUTHEAST, TILE_CENTER, HALF_HEIGHT
# from redeclipse.skybox import MinecraftSky
from redeclipse.vector import CoarseVector, FineVector
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, redeclipse=None, magica=None):

    for idx, Room in enumerate(autodiscover()):
        mymap = parse(mpz_in.name)
        upm = UnusedPositionManager(2**7, mirror=True, noclip=True)
        v = VoxelWorld(size=2**7)
        print("Processing %s" % Room.name.replace(' ', '_'))

        kwargs = Room.randOpts(None)
        e = Room
        n = copy.copy(e)
        s = copy.copy(e)
        w = copy.copy(e)

        e.re_init(pos=CoarseVector(8 + 3, 8, 0), orientation=EAST, **kwargs)
        kwargs = Room.randOpts(None)
        w.re_init(pos=CoarseVector(8 - 3, 8, 0), orientation=WEST, **kwargs)
        kwargs = Room.randOpts(None)
        n.re_init(pos=CoarseVector(8, 8 + 3, 0), orientation=NORTH, **kwargs)
        kwargs = Room.randOpts(None)
        s.re_init(pos=CoarseVector(8, 8 - 3, 0), orientation=SOUTH, **kwargs)

        upm.register_room(n)
        upm.register_room(s)
        upm.register_room(e)
        upm.register_room(w)

        n.render(v, mymap)
        s.render(v, mymap)
        e.render(v, mymap)
        w.render(v, mymap)

        e.x('column', v, NORTH + EAST + NORTH + (ABOVE * 3), EAST, 8, tex=TEXMAN.get_colour(1, 0, 0))
        e.x('column', v, NORTH + EAST + NORTH + (ABOVE * 3), NORTH, 6, tex=TEXMAN.get_colour(1, 1, 0))
        e.x('column', v, NORTH + EAST + NORTH + (ABOVE * 3), SOUTH, 6, tex=TEXMAN.get_colour(1, 0, 1))
        e.x('column', v, NORTH + EAST + NORTH + (ABOVE * 3), WEST, 4, tex=TEXMAN.get_colour(0, 1, 1))

        from redeclipse.objects import cube
        for i in range(8):
            for j in range(8):
                v.set_pointv(
                    CoarseVector(8, 8, 3) + (EAST * 5) + FineVector(i, j, 0),
                    cube.newtexcube(tex=p.TEXMAN.get_c('accent'))
                )

        for (pos, typ, ori) in upm.unoccupied:
            r = p.TestRoom(pos, orientation=EAST)
            r.render(v, mymap)

        if magica:
            to_magicavoxel(v, magica, TEXMAN)

        if redeclipse:
            TEXMAN.emit_conf(redeclipse)
            TEXMAN.copy_data()
            mymap.world = v.to_octree()
            mymap.world[0].octsav = 0
            mymap.write(redeclipse.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')

    parser.add_argument('--redeclipse', type=argparse.FileType('w'), help='Output .mpz file')
    parser.add_argument('--magica', type=argparse.FileType('w'), help='Output .vox file')
    args = parser.parse_args()
    main(**vars(args))