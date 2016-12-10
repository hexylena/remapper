#!/usr/bin/env python
import json
import argparse
from redeclipse.cli import parse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump map as JSON file')
    parser.add_argument('input', help='Input .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)

    print(json.dumps(mymap.to_dict()))
