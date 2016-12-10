import argparse
import os
import glob


if __name__ == '__main__':
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
""" % (file, idx))

