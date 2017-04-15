#!/usr/bin/env python
import argparse
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.prefabs.construction_kit import mv, m, column, cube_s


def main(mpz_in, mpz_out_1x1, mpz_out_2x2, mpz_out_3x3, size=2**7):
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)


    main_pos = (6, 6, 6)
    cube_s(v, 8, mv(main_pos, (0, 0, 0)), tex=2)

    # Standard code to render octree to file.
    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(mpz_out_1x1.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('mpz_out_1x1', type=argparse.FileType('w'), help='Output .mpz file')
    parser.add_argument('mpz_out_2x2', type=argparse.FileType('w'), help='Output .mpz file')
    parser.add_argument('mpz_out_3x3', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--size', default=2**7, type=int, help="World size. Danger!")
    args = parser.parse_args()
    main(**vars(args))
