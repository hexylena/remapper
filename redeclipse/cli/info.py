from redeclipse import MapParser
import json
import sys


def show_info(map_path):
    mp = MapParser()
    m = mp.parseMap(map_path)

    data = {
        'magic': bytes.decode(m.magic),
        'version': m.version,
        'headersize': m.headersize,
        # 'meta': [(key, bytes.decode(value) if isinstance(value, bytes) else value) for (key, value) in m.meta.items()],
        # 'mapvars': [(bytes.decode(key), bytes.decode(value) if isinstance(value, bytes) else value) for (key, value) in m.map_vars.items()],
        'texmru': m.texmru,
        'entities': [ent.to_dict() for ent in m.ents],
        # 'world': [x.to_dict() for x in m.world]
    }
    return data


if __name__ == '__main__':
    print(json.dumps(show_info(sys.argv[1])))
    # print(show_info(sys.argv[1]))
