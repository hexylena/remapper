"""Light manager"""
import colorsys
import random
import noise

from redeclipse.entities import Light
from redeclipse.vector.orientations import TILE_CENTER, HALF_HEIGHT

SIZE = 8
SIZE_OFFSET = 1
GLOBAL_BRIGHTNESS_SCALING = 1.0


class LightManager:
    """
    A lighting manager for a map
    """

    def __init__(self, brightness=1.0, saturation=1.0, world_size=2**7):
        """
        :param float brightness: The brightness of the map
        :param float saturation: The saturation level for the lights
        """
        self.brightness = brightness
        self.saturation = saturation
        self._world_size_factor = world_size / 2 ** 6

    def light(self, xmap, position, colour_override=None, autocenter=True, size_factor=1):
        """
        :param xmap: A redeclipse map object, the light will be attached to the entity list.
        :type xmap: redeclipse.Map

        :param position: The position of the light
        :type position: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param colour_override: Override whatever colour the light manager comes up with
        :type colour_override: tuple(int, int, int)

        :param boolean autocenter: Automatically add FineVector(4, 4, 4) to the position
        """
        if autocenter:
            pos = position + TILE_CENTER + HALF_HEIGHT

        if colour_override:
            (red, green, blue) = colour_override
        else:
            (red, green, blue) = self.hue(pos)

        light = self.get_light(pos, red, green, blue, size_factor=size_factor)
        xmap.ents.append(light)

    def hue(self, pos):
        """
        Get a hue for a position. Child classes should implement this in
        more interesting manners. This returns a pure white light by default.

        :param pos: The position
        :type pos: tuple(int, int, int)

        :returns: A colour
        :rtype: tuple(int, int, int)
        """
        return (255, 255, 255)

    def get_light(self, position, red, green, blue, size_factor=1):
        """
        Return a light entity for a position and colour

        :param position: The position
        :type position: tuple(int, int, int)

        :param int red: red component
        :param int green: green component
        :param int blue: blue component

        :returns: An appropriately configured light entity
        :rtype: redeclipse.entities.Light
        """
        return Light(
            xyz=position.entity() / self._world_size_factor,
            # Colours
            red=red,
            green=green,
            blue=blue,
            # Make it a relatively small light, nice intimate feel without
            # washing out.
            radius=SIZE_OFFSET * 64 * size_factor,
        )


class PositionBasedLightManager(LightManager):
    """
    A lighting manager for a map which returns a different colour based on position.
    """

    def hue(self, pos):
        """
        Get a hue for a position. This returns a coloured light that changes hue gradually over x/y/z

        :param pos: The position
        :type pos: tuple(int, int, int)

        :returns: A colour
        :rtype: tuple(int, int, int)
        """
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

        (red1, grn1, blu1) = colorsys.hsv_to_rgb(hue, self.saturation, 255)
        # We then peg S and V to high and only retain hue
        (red, grn, blu) = colorsys.hsv_to_rgb(hue, self.saturation, int(255 * min(self.brightness, 1.0)))
        print(red, grn, blu, red1, grn1, blu1)
        # This should give us a bright colour on a continuous range
        return (int(red), int(grn), int(blu))
