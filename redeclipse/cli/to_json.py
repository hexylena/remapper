#!/usr/bin/env python
from redeclipse.cli import parse
import json
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump map as JSON file')
    parser.add_argument('input', help='Input .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)

    print(json.dumps(mymap.to_dict()))
