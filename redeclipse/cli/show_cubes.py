#!/usr/bin/env python
from redeclipse.cli import parse
import argparse
# import random

def simplify(d):
    d['faces'] = d['faces'][0]
    if d['faces'] == 'F_EMPTY' and d['ext'] is None:
        return ['Empty']

    if len(set(d['edges'])) == 1:
        d['edges'] = '%s * %s' % (len(d['edges']), d['edges'][0])

    if len(set(d['texture'])) == 1:
        d['texture'] = d['texture'][0]

    for k in list(d.keys()):
        if not d[k]:
            del d[k]
    return d

def show_cubes(m, indent=0):
    for c in m:
        print(('\t' * indent), 'CUBE', simplify(c.to_dict(children=False)))
        if c.children:
            show_cubes(c.children, indent=indent + 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    show_cubes(mymap.world)
