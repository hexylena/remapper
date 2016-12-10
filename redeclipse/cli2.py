from redeclipse import MapParser
from redeclipse.vec import ivec3
import sys
import copy
import random

def main():
    mp = MapParser()
    m = mp.parseMap(sys.argv[1])
    # I think ent[2] is a tree...

    tree = m.ents[1]
    for i in range(20):
        ntree = copy.deepcopy(tree)
        ntree.o = ivec3(
            random.randint(0, 512),
            random.randint(0, 512),
            512
        )
        m.ents.append(ntree)

    m.write(sys.argv[2])


if __name__ == '__main__':
    main()
