import noise
import colorsys
import random
from redeclipse.prefabs.construction_kit import m
from redeclipse.entities import Light
SIZE = 8
_BUILTIN_SIZE = 2 ** 7
_REAL_SIZE = 2 ** 8
SIZE_OFFSET = _BUILTIN_SIZE / _REAL_SIZE






class LightManager:
    def __init__(self, brightness=1.0, saturation=1.0):
        self.brightness = brightness
        self.saturation = saturation

    def light(self, xmap, position, size):
        if random.random() > self.brightness:
            return

        light = self.get_light(position, size,
                               saturation=self.saturation)
        xmap.ents.append(light)

    def hue(self, pos, saturation=1.0):
        nums = list(map(
            lambda x: x * (2 ** -8.4),
            pos
        ))

        # convert a tuple of three nums (x,y,z) + offset into a
        # 0-255 integer.
        def kleur(nums, base):
            return int(abs(noise.pnoise3(*nums, base=base)) * 255)

        # Now we generate our colour:
        r = kleur(nums, 10)
        g = kleur(nums, 0)
        b = kleur(nums, 43)

        # RGB isn't great, because it means low values of RGB are
        # low luminance. So we convert to HSV to get pure hue
        (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
        # We then peg S and V to high and only retain hue
        (r, g, b) = colorsys.hsv_to_rgb(h, saturation, 255)
        # This should give us a bright colour on a continuous range
        return (int(r), int(g), int(b))

    def get_light(self, pos, size, saturation=1.0):
        (red, green, blue) = self.hue(pos, saturation)

        return Light(
            # Center the light in the unit, x&y
            xyz=m(
                SIZE_OFFSET * (pos[0] + size / 2),
                SIZE_OFFSET * (pos[1] + size / 2),
                # Light above player head height
                SIZE_OFFSET * (pos[2] + 4),
            ),
            # Colours
            red=red,
            green=green,
            blue=blue,
            # Make it a relatively small light, nice intimate feel without
            # washing out.
            radius=SIZE_OFFSET * 64,
        )


class BoringLightManager(LightManager):
    def hue(self, pos, saturation=1.0):
        return (255, 255, 255)

class PositionBasedLightManager(LightManager):
    pass
