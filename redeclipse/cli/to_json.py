#!/usr/bin/env python
# import json
import sys
import simplejson as json
import argparse
from redeclipse.cli import parse


def main():
    parser = argparse.ArgumentParser(description='Dump map as JSON file')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('--section', help='Section name, e.g. "entities"')
    args = parser.parse_args()

    mymap = parse(args.input)

    if args.section:
        sys.stdout.write(json.dumps(mymap.to_dict()[args.section], iterable_as_array=True))
    else:
        sys.stdout.write(json.dumps(mymap.to_dict(), iterable_as_array=True))


if __name__ == '__main__':
    main()
