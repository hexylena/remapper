#!/usr/bin/env python
from redeclipse.cli import parse
from redeclipse.objects import MapModel
import argparse
import random

def add_trees(m, num=20):
    # type is a number from:
    #
    #    cat simple.cfg | grep mmodel |  awk '{printf("%d %s\n" , NR-1 , $0)}'
    #
    for i in range(num):
        tree = MapModel(
            x=random.randint(0, 1024),
            y=random.randint(0, 1024),
            z=512,
            type=random.randint(115, 129), # Tree
            yaw=random.randint(0, 360),
        )
        m.ents.append(tree)

    return m


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')

    parser.add_argument('--num', type=int, default=20, help="Number of trees to add")
    args = parser.parse_args()

    mymap = parse(args.input)
    newmap = add_trees(mymap)

    newmap.write(args.output)
