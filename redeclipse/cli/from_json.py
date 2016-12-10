from redeclipse import Map
import json
import argparse



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WARNING: INCOMPLETE. Load map from JSON file')
    parser.add_argument('input', type=argparse.FileType('r'), help='Input .json file')
    parser.add_argument('output', help='Input .mpz file')
    args = parser.parse_args()

    # mymap = parse(args.input)
    mymap = Map.from_dict(json.load(args.input))
    mymap.write(args.output)
