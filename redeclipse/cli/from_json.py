from redeclipse import Map
from redeclipse.objects import VSlot
from redeclipse.entities import Entity
from collections import OrderedDict
import json
import sys


def from_dict(data):
    # TODO
    meta = OrderedDict()
    for (key, value) in data['meta']:
        meta[key] = value

    map_vars = OrderedDict()
    for (key, value) in data['map_vars']:
        if isinstance(value, str):
            map_vars[str.encode(key)] = str.encode(value)
        else:
            map_vars[str.encode(key)] = value

    # TODO
    world = {}

    m = Map(
        magic=str.encode(data['magic']),
        version=data['version'],
        headersize=data['headersize'],
        meta=meta,
        map_vars=map_vars,
        texmru=data['texmru'],
        ents=[Entity.from_dict(x) for x in data['entities']],
        vslots=[VSlot.from_dict(x) for x in data['vslots']],
        chg=data['chg'],
        worldroot=world,
    )

    return m


if __name__ == '__main__':
    m = from_dict(json.load(open(sys.argv[1], 'r')))
    print(m)
    m.write('asdf')
