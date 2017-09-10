import os
import shutil


class Skybox:
    back_ext = '_bk.jpg'
    down_ext = '_dn.jpg'
    front_ext = '_ft.jpg'
    left_ext = '_lf.jpg'
    right_ext = '_rt.jpg'
    up_ext = '_up.jpg'
    basename = 'base'

    def __init__(self, redeclipse_basedir):
        self.basedir = os.path.join(redeclipse_basedir, 'data', 'hxr')
        self.skydir = os.path.join(redeclipse_basedir, 'data', 'hxr', 'skybox')
        if not os.path.exists(self.skydir):
            os.makedirs(self.skydir)

        module_path = os.path.dirname(__file__)
        for fn in self.get_files():
            shutil.copy(
                os.path.join(module_path, fn),
                self.skydir,
            )

    def get_files(self):
        return [
            self.basename + self.back_ext,
            self.basename + self.down_ext,
            self.basename + self.front_ext,
            self.basename + self.left_ext,
            self.basename + self.right_ext,
            self.basename + self.up_ext,
        ]

    def get_short_path(self):
        return 'hxr/skybox/%s' % self.basename


class DesertSky(Skybox):
    basename = 'desert'


class MinecraftSky(Skybox):
    basename = 'minecraft'
