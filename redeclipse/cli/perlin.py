#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.objects import cube
import argparse
import sys  # noqa
import random  # noqa
import math  # noqa
import noise  # noqa
random.seed(22)
IJ_SIZE = 2**7
K_SIZE = 50
MAP_SEED = 0
octaves = 1
noise_scaling = 32


def main():
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**7)

    treeDensityMap = {}
    for i in range(IJ_SIZE):
        for j in range(IJ_SIZE):
            w = noise.pnoise2(j / noise_scaling, i / noise_scaling, octaves=2, base=MAP_SEED + 128)
            # This is a forrest
            if w < -0.1:
                # Then we take a chance
                if random.random() < (abs(w) / 4):
                    treeDensityMap[i, j] = True

    bldgDensityMap = {}
    for i in range(IJ_SIZE // 4):
        for j in range(IJ_SIZE // 4):
            w = noise.pnoise2(j / noise_scaling, i / noise_scaling, octaves=2, base=MAP_SEED + 64)
            # This is a forrest
            if w < -0.1:
                # Then we take a chance
                if random.random() < (abs(w) / 3):
                    for i2 in range(4 * i, 4 * (i + 1)):
                        for j2 in range(4 * j, 4 * (j + 1)):
                            bldgDensityMap[i2, j2] = True

    def point(i, j, k):
        q = noise.pnoise2(i / noise_scaling, j / noise_scaling, octaves=octaves, base=MAP_SEED)
        q *= 5
        q += 30

        if i % 10 == 0 and j == 0 and k == 0:
            sys.stderr.write('%s / %s %s %s\n' % (i, IJ_SIZE, q, w))

        if (i, j) in treeDensityMap:
            return [58, 58, 58, 58, 59, 59]

        if (i, j) in bldgDensityMap and k < q + 4 and k >= q:
            return [57, 57, 57, 57, 57, 57]

        if k < q:
            return [23, 23, 23, 23, 22, 61]

        return False

    for i in range(IJ_SIZE):
        for j in range(IJ_SIZE):
            for k in range(K_SIZE):
                q = point(i, j, k)
                if q:
                    v.set_point(i, j, k, cube.newtexcube(tex=q))

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)


if __name__ == '__main__':
    main()
