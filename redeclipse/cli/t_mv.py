#!/usr/bin/env python
import argparse
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.prefabs.vector import FineVector
from redeclipse.magicavoxel import to_magicavoxel
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mv_out):
    world = VoxelWorld(2**7)

    for i in range(24):
        world.set_pointv(FineVector(i, 0, 0), None)

    with open('out.vox', 'wb') as handle:
        to_magicavoxel(world, handle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mv_out', type=argparse.FileType('w'), help='Output .vox file')
    args = parser.parse_args()
    main(**vars(args))
