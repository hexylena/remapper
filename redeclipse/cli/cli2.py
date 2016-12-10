from redeclipse import MapParser
# from redeclipse.vec import ivec3
# from redeclipse.enums import EntType
from redeclipse.objects import MapModel
import sys
# import copy
import random

def main():
    mp = MapParser()
    print('============PARSING============')
    m = mp.parseMap(sys.argv[1])
    print('============MODIFIY============')
    # type is a number from:
    #
    #    cat simple.cfg | grep mmodel |  awk '{printf("%d %s\n" , NR-1 , $0)}'
    #
    for i in range(20):
        tree = MapModel(
            x=random.randint(0, 1024),
            y=random.randint(0, 1024),
            z=512,
            type=random.randint(115, 129), # Tree
            yaw=random.randint(0, 360),
        )
        m.ents.append(tree)

    print('============WRITING============')
    m.write(sys.argv[2])


if __name__ == '__main__':
    main()
