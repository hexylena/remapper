class BaseTex:
    # shader = 'bumpspecmapworld'
    pass
    # setshader bumpspecmapworld
    # setshaderparam specscale 0.250000 0.250000 0.250000 0.000000
    # texture c "trak/trak6/tile3.jpg" 0 0 0 0.250000 // 3
    # texture n "trak/trak6/tile3_nm.png"
    # texture s "trak/trak6/tile3_gloss.jpg"
    # texcolor 0.750000 0.250000 0.125000


class Sky(BaseTex):
    def conf(self, **kwargs):
        return """
setshader stdworld
texture c "textures/sky.png" 0 0 0 1.000000 // 0
"""

class Default(BaseTex):
    def conf(self, **kwargs):
        return """
setshader stdworld
texture c "textures/default.png" 0 0 0 0.500000 // 1
"""

class BumpSpecMapParallaxWorld:
    scale = 2
    c = None
    n = None
    z = None
    s = None

    def conf(self, idx=0, basepath=""):
        return """setshader bumpspecmapparallaxworld
setshaderparam specscale 0.500000 0.500000 0.500000 {0.scale}
texture c "{basepath}{0.c}" 0 0 0 0.500000 // {idx}
texture n "{basepath}{0.n}"
texture s "{basepath}{0.s}"
texture z "{basepath}{0.z}"
""".format(self, idx=idx, basepath=basepath)

    def files(self):
        yield self.c
        yield self.n
        yield self.s
        yield self.z
