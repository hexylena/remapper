import argparse
import os
import glob


def main():
    parser = argparse.ArgumentParser(description='Generate CFG file from directory of images')
    parser.add_argument('input', help='Directory containing PNG files')
    args = parser.parse_args()

    print("""setshader stdworld
texture c "textures/sky.png" 0 0 0 1.000000 // 0

setshader stdworld
texture c "textures/default.png" 0 0 0 0.500000 // 1

""")

    for idx, file in enumerate(sorted(glob.glob(args.input + os.path.sep + "*"))):
        print("""setshader stdworld
texture c "%s" 0 0 0 1.000000 // %s
""" % (file, idx + 2))

    # Some example ents
    print("""
mmodel "unnamed/rocks/rock01"
mmodel "unnamed/rocks/rock02"
mmodel "vegetation/bush01"
mmodel "vegetation/tree00"
mmodel "vegetation/tree01"
mmodel "vegetation/tree02"
mmodel "vegetation/tree03"
mmodel "vegetation/tree04"
mmodel "vegetation/tree05"
mmodel "vegetation/tree06"
mmodel "vegetation/tree07"
mmodel "vegetation/tree08"
mmodel "vegetation/tree09"
mmodel "vegetation/tree10"
mmodel "vegetation/tree11"
mmodel "vegetation/tree12"
mmodel "vegetation/weeds"

mapsound "sounds/ambience/alienwind" 100
mapsound "sounds/ambience/blowwind" 80
mapsound "sounds/ambience/cavedrip" 100
mapsound "sounds/ambience/creek" 80
    """)


if __name__ == '__main__':
    main()
