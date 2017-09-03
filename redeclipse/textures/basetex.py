# TODO: Refactor

class BaseTex(object):
    # where the textures are output to
    basepath = "hxr/textures"
    # Where the textures come from
    srcpath = "data/minecraft"
    # shader = 'bumpspecmapworld'
    # setshader bumpspecmapworld
    # setshaderparam specscale 0.250000 0.250000 0.250000 0.000000
    # texture c "trak/trak6/tile3.jpg" 0 0 0 0.250000 // 3
    # texture n "trak/trak6/tile3_nm.png"
    # texture s "trak/trak6/tile3_gloss.jpg"
    # texcolor 0.750000 0.250000 0.125000
    def files(self):
        return []


class Sky(BaseTex):
    scale = 1
    def conf(self, **kwargs):
        return """
setshader stdworld
texture c "textures/sky.png" 0 0 0 {0.scale} // 0 {0.__class__}
""".format(self)

class Default(BaseTex):
    scale = 1
    def conf(self, **kwargs):
        return """
setshader stdworld
texture c "textures/default.png" 0 0 0 {0.scale} // 1 {0.__class__}
""".format(self)


class SimpleColourTex(BaseTex):
    basepath = "hxr/textures"
    srcpath = "data/hxr"
    r = 1
    g = 0
    b = 1
    def conf(self, idx=0, **kwargs):
        return """
setshader stdworld
texture c "{0.basepath}/empty.png" 0 0 0 1 // {idx} {0.__class__}
texcolor {0.r} {0.g} {0.b}
""".format(self, idx=idx)

    def files(self):
        yield 'empty.png'


class SimpleTex(BaseTex):
    c = None

    def conf(self, idx=0, **kwargs):
        return """
setshader stdworld
texture c "{0.basepath}/{0.c}" 0 0 0 {0.scale} // {idx} {0.__class__}
""".format(self, idx=idx)

    def files(self):
        yield self.c

class DefaultBumpSpecMapWorld(BaseTex):
    scale = 2
    c = None
    n = None
    s = None
    basepath = "hxr/textures"
    texcolor = None

    def conf(self, idx=0):
        conf = """setshader bumpspecmapworld
setshaderparam specscale 0.500000 0.500000 0.500000 {0.scale}
texture c "{0.basepath}/{0.c}" 0 0 0 0.500000 // {idx} {0.__class__}
texture n "{0.basepath}/{0.n}"
texture s "{0.basepath}/{0.s}"
""".format(self, idx=idx)

        if self.texcolor:
            conf += "texcolor %s %s %s" % self.texcolor
        return conf

class BumpSpecMapWorld(DefaultBumpSpecMapWorld):
    def files(self):
        yield self.c
        yield self.n
        yield self.s


class DefaultBumpSpecMapParallaxWorld(BaseTex):
    c = None
    n = None
    z = None
    s = None
    basepath = "hxr/textures"
    texcolor = None
    specscale = None
    parallaxscale = None

    def conf(self, idx=0):
        conf = """setshader bumpspecmapparallaxworld\n"""
        if self.specscale:
            conf += """setshaderparam specscale %s %s %s %s\n""" % self.specscale

        if self.parallaxscale:
            conf += """setshaderparam parallaxscale %s %s %s %s\n""" % self.parallaxscale

        conf += """texture c "{0.basepath}/{0.c}" 0 0 0 0.500000 // {idx} {0.__class__}
texture n "{0.basepath}/{0.n}"
texture s "{0.basepath}/{0.s}"
texture z "{0.basepath}/{0.z}"\n""".format(self, idx=idx)

        if self.texcolor:
            conf += "texcolor %s %s %s\n\n" % self.texcolor
        return conf

class BumpSpecMapParallaxWorld(DefaultBumpSpecMapParallaxWorld):
    def files(self):
        yield self.c
        yield self.n
        yield self.s
        yield self.z

class DefaultBumpSpecMapParallaxGlowWorld(BaseTex):
    c = None
    n = None
    z = None
    s = None
    g = None
    basepath = "hxr/textures"
    texcolor = None
    specscale = None
    glowcolor = None
    parallaxscale = None

    def conf(self, idx=0):
        conf = """setshader bumpspecmapparallaxglowworld\n"""
        if self.glowcolor:
            conf += """setshaderparam glowcolor %s %s %s %s\n""" % self.glowcolor

        if self.specscale:
            conf += """setshaderparam specscale %s %s %s %s\n""" % self.specscale

        if self.parallaxscale:
            conf += """setshaderparam parallaxscale %s %s %s %s\n""" % self.parallaxscale

        conf += """texture c "{0.basepath}/{0.c}" 0 0 0 0.500000 // {idx} {0.__class__}
texture n "{0.basepath}/{0.n}"
texture s "{0.basepath}/{0.s}"
texture z "{0.basepath}/{0.z}"
texture g "{0.basepath}/{0.g}"\n""".format(self, idx=idx)

        if self.texcolor:
            conf += "texcolor %s %s %s\n\n" % self.texcolor
        return conf

class BumpSpecMapParallaxGlowWorld(DefaultBumpSpecMapParallaxGlowWorld):
    def files(self):
        yield self.c
        yield self.n
        yield self.s
        yield self.z
        yield self.g
