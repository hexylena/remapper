#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.objects import cube
import argparse
import sys # noqa
import random # noqa
import math # noqa
import noise # noqa
random.seed(22)
IJ_SIZE = 2**3
K_SIZE = 50
MAP_SEED = 0
octaves = 1
noise_scaling = 32


def main():
    parser = argparse.ArgumentParser(description='Try smoothed terrain')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**5)

    seen = {}

    def point_q(i, j, k):
        # q = noise.pnoise2(i/noise_scaling, j/noise_scaling, octaves=octaves, base=MAP_SEED)
        # q *= 60
        # q += 30
        # return q
        # q1 = math.sin(i / 8) * 3
        # q2 = math.sin(j / 7) * 3
        # return 20 + q1 + q2
        return 20 + i / 2

    def rescale_corner(v):
        v -= int(v)
        return int(v * 16) * 8

    def point(i, j, k):
        q = point_q(i, j, k)
        if (i, j) not in seen:
            print(i, j, q)
            seen[(i, j)] = True

        if i % 10 == 0 and j == 0 and k == 0:
            sys.stderr.write('%s/%s %s\n' % (i, IJ_SIZE, q))

        # four corners around
        corners = list(map(rescale_corner, [
            max(point_q(i - 0.5, j - 0.5, k), math.floor(q)),
            max(point_q(i - 0.5, j + 0.5, k), math.floor(q)),
            max(point_q(i + 0.5, j - 0.5, k), math.floor(q)),
            max(point_q(i + 0.5, j + 0.5, k), math.floor(q))
        ]))

        print(i, j, k, q, corners)

        z = [3, 4, 5, 6, 7, 8]
        z2 = [15, 15, 15, 15, 15, 15]
        if k < math.floor(q):
            return z, None

        if math.floor(q) <= k < math.ceil(q):
            return z2, corners

        return False, None

    for i in range(IJ_SIZE):
        c = cube.newtexcube(tex=i)
        v.set_point(i, i, i, c)

    for i in range(10):
        for j in range(1):
            for k in range(20, 30):
                (q, corners) = point(i, j, k)
                if q:
                    c = cube.newtexcube(tex=q)
                    if corners:
                        c.edges[8] = corners[0]
                        c.edges[9] = corners[2]
                        c.edges[10] = corners[1]
                        c.edges[11] = corners[3]

                    v.set_point(i, j, k, c)

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)


if __name__ == '__main__':
    main()
