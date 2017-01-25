#!/usr/bin/env python
from pprint import pformat
from redeclipse.cli import parse
import argparse
# import random

def simplify(d):
    d['faces'] = d['faces'][0]
    if d['octsav'] == 1:
        return ['Empty']

    if len(set(d['edges'])) == 1:
        d['edges'] = '%s * %s' % (len(d['edges']), d['edges'][0])

    for k in list(d.keys()):
        if not d[k]:
            del d[k]
    return d

def show_cubes(m, indent=0, simple=False):
    for c in m:
        z = c.to_dict(children=False)
        del z['_id']

        if simple:
            z = simplify(z)

        print(('\t' * indent), 'CUBE', pformat(z).replace('\n', '\n' + ('\t' * indent)))
        if c.children:
            show_cubes(c.children, indent=indent + 1)

def main():
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('--simplify', action='store_true', help='Reduce output')
    args = parser.parse_args()

    mymap = parse(args.input)
    show_cubes(mymap.world, simple=args.simplify)

if __name__ == '__main__':
    main()
