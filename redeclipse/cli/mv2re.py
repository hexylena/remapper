#!/usr/bin/env python
import argparse
import logging
import os
from redeclipse.magicavoxel.reader import Magicavoxel
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class_template = """
class {classname}(Room):
    _height = 1

    def render(self, world, xmap):
        self.light(xmap)
"""

cube_tpl = """        self.x('cube', world, SELF + FineVector({x}, {y}, {z}), tex=TEXMAN.get('auto_{tex}'))
"""

def main(mv_in, py_out):
    model = Magicavoxel.from_file(mv_in)
    classname = os.path.splitext(os.path.basename(mv_in))[0]

    tpl = class_template.format(classname=classname.replace('-', '_'))
    for vox in model.model_voxels.voxels:
        tpl += cube_tpl.format(x=vox.x, y=vox.y, z=vox.z, tex=vox.c + 1)

    py_out.write(tpl)

    for idx, colour in enumerate(model.palette.colours):
        print("class auto_%s(SimpleColourTex):" % (idx + 1))
        print("    r = %s" % (colour.r / 255))
        print("    g = %s" % (colour.g / 255))
        print("    b = %s" % (colour.b / 255))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mv_in', help='Input .vox file')
    parser.add_argument('py_out', type=argparse.FileType('w'), help='Output .py file')
    args = parser.parse_args()
    main(**vars(args))
