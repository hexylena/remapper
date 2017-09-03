"""Light manager"""
import colorsys
import random

import noise

from redeclipse.entities import Light
from redeclipse.prefabs.vector import CoarseVector, FineVector
from redeclipse.prefabs.orientations import TILE_CENTER, HALF_HEIGHT

SIZE = 8
_BUILTIN_SIZE = 2 ** 7
_REAL_SIZE = 2 ** 8
SIZE_OFFSET = _BUILTIN_SIZE / _REAL_SIZE


class LightManager:
    def __init__(self, brightness=1.0, saturation=1.0):
        self.brightness = brightness
        self.saturation = saturation

    def light(self, xmap, position, colour_override=None, autocenter=True):
        if random.random() > self.brightness:
            return

        if autocenter:
            pos = position + TILE_CENTER + HALF_HEIGHT
        else:
            pos = position.fine()

        if colour_override:
            (red, green, blue) = colour_override
        else:
            (red, green, blue) = self.hue(pos)

        light = self.get_light(pos, red, green, blue)
        xmap.ents.append(light)

    def hue(self, pos):
        return (255, 255, 255)

    def get_light(self, position, red, green, blue):
        return Light(
            xyz=position,
            # Colours
            red=red,
            green=green,
            blue=blue,
            # Make it a relatively small light, nice intimate feel without
            # washing out.
            radius=SIZE_OFFSET * 64,
        )


class PositionBasedLightManager(LightManager):
    def hue(self, pos):
        nums = [
            x * (2 ** -8.4)
            for x in pos
        ]

        # convert a tuple of three nums (x,y,z) + offset into a
        # 0-255 integer.
        def kleur(nums, base):
            return int(abs(noise.pnoise3(*nums, base=base)) * 255)

        # Now we generate our colour:
        red = kleur(nums, 10)
        grn = kleur(nums, 0)
        blu = kleur(nums, 43)

        # RGB isn't great, because it means low values of RGB are
        # low luminance. So we convert to HSV to get pure hue
        (hue, _, _) = colorsys.rgb_to_hsv(red, grn, blu)
        # We then peg S and V to high and only retain hue
        (red, grn, blu) = colorsys.hsv_to_rgb(hue, self.saturation, 255)
        # This should give us a bright colour on a continuous range
        return (int(red), int(grn), int(blu))
