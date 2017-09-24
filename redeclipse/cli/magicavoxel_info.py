#!/usr/bin/env python
import sys
import argparse
import logging
import os

from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.voxel import VoxelWorld

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mv_in):
    try:
        model = Magicavoxel.from_file(mv_in)
    except:
        Magicavoxel.SIZE = 255
        model = Magicavoxel.from_file(mv_in)
        print("Odd: colours were shorter than expected.")

    classname = os.path.splitext(os.path.basename(mv_in))[0]

    print("Model: %s" % classname)
    world = VoxelWorld()
    for vox in model.model_voxels.voxels:
        world.set_point(vox.x, vox.y, vox.z, vox.c)
    print("Model boundaries: x in [{0.xmin}, {0.xmax}]; y in [{0.ymin}, {0.ymax}]; z in [{0.zmin}, {0.zmax}]".format(world))

    print("Pallette")
    for idx, colour in enumerate(model.palette.colours):
        if colour.r != 0 or colour.g != 0 or colour.b != 0:
            print("C[%s] = (%s, %s, %s)" % (idx, colour.r, colour.g, colour.b))

    for z in range(world.zmin, world.zmax + 1):
        print("==== z = %s ====" % z)

        sys.stdout.write('0-' + 'x' * 8 + '+')
        sys.stdout.write('\n')
        sys.stdout.write('- ' + ' ' * 8)
        sys.stdout.write('\n')
        for x in range(world.xmin, world.xmax + 1):
            sys.stdout.write('y ')
            for y in range(world.ymin, world.ymax + 1):
                if (x, y, z) in world.world:
                    sys.stdout.write('#')
                else:
                    sys.stdout.write(' ')
            sys.stdout.write('\n')
        sys.stdout.write('+\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mv_in', help='Input .vox file')
    args = parser.parse_args()
    main(**vars(args))
