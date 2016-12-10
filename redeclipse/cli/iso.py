#!/usr/bin/env python
import argparse
from redeclipse.cli import parse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run map through library in order to compare binary outputs')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    m = parse(args.input)
    m.write(args.output)
