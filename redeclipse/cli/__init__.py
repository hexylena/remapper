import argparse
import json
import logging
from redeclipse import MapParser
from redeclipse.magicavoxel.writer import to_magicavoxel

log = logging.getLogger(__name__)


def parse(input):
    mp = MapParser()
    return mp.read(input)


def output_args(parser):
    parser.add_argument('--mpz_out', type=argparse.FileType('w'), help='Output .mpz file')
    parser.add_argument('--magica', type=argparse.FileType('wb'), help='Output .vox file')
    parser.add_argument('--graph', type=argparse.FileType('w'), help='Output .json file')

def output(v, mymap, upm, prefabs, args):
    if args.magica:
        to_magicavoxel(v, args.magica, prefabs.TEXMAN)

    if args.mpz_out:
        prefabs.TEXMAN.emit_conf(args.mpz_out)
        prefabs.TEXMAN.copy_data()

        mymap.world = v.to_octree()
        mymap.world[0].octsav = 0
        mymap.write(args.mpz_out.name)

    if args.graph:
        data = {
            "nodes": [{'id': id(None), 'name': 'None', 'label': 'None'}],
            "links": []
        }
        for room in upm.rooms:
            data['nodes'].append({
                'id': id(room),
                'name': room.name,
                'label': room.name,
            })

        for a, b in upm.links:
            la = upm.occupied.get(a, None)
            lb = upm.occupied.get(b, None)

            data['links'].append({
                'source': id(la),
                'target': id(lb),
                'type': 'connected'
            })

        json.dump(data, args.graph)
