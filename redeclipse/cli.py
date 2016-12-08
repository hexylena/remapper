from redeclipse import MapParser
import sys

def main():
    mp = MapParser()
    m = mp.parseMap(sys.argv[1])
    m.write(sys.argv[1] + '.out')
