#!/usr/bin/env python
import argparse
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse import prefabs as p
from redeclipse.prefabs import magica as m, TEXMAN
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel.writer import to_magicavoxel

from redeclipse.vector import CoarseVector
from redeclipse.vector.orientations import SOUTH, NORTH, WEST, EAST, ABOVE
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# 2 ** 7 = 16 rooms
def main(mpz_in, redeclipse=None, magica=None, world_size=2**7):
    Room = m.castle_large

    mymap = parse(mpz_in.name)
    upm = UnusedPositionManager(world_size, mirror=True, noclip=True)
    v = VoxelWorld(size=world_size)

    kwargs = Room.randOpts(None)
    e = Room(pos=CoarseVector(8 + 3, 8, 0), orientation=EAST, **kwargs)
    kwargs = Room.randOpts(None)
    w = Room(pos=CoarseVector(8 - 3, 8, 0), orientation=WEST, **kwargs)
    kwargs = Room.randOpts(None)
    n = Room(pos=CoarseVector(8, 8 + 3, 0), orientation=NORTH, **kwargs)
    kwargs = Room.randOpts(None)
    s = Room(pos=CoarseVector(8, 8 - 3, 0), orientation=SOUTH, **kwargs)

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

    for i in range(world_size // 8):
        q = p.Room(pos=CoarseVector(i, i, 1), orientation=EAST)
        q.render(v, mymap)

    # for (pos, typ, ori) in upm.unoccupied:
        # r = p.TestRoom(pos, orientation=EAST)
        # r.render(v, mymap)

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
    parser.add_argument('--magica', type=argparse.FileType('wb'), help='Output .vox file')
    args = parser.parse_args()
    main(**vars(args))
