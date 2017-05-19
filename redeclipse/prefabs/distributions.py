DEFAULT_TRANSITION_MATIX = [
    #h  hj   p  ps   v
    [0,  0,  0,  0,  0], # 'hallway'
    [    0,  0,  0,  0], # 'hallway_jump'
    [        0,  0,  0], # 'platform'
    [            0,  0], # 'platform_setpiece'
    [                0], # 'vertical'
]


class DistributionManager:
    mirror = False
    transition_probabilities = {}

    def tp(self, a, b):
        key = (a, b)
        if key in self.transition_probabilities:
            return self.transition_probabilities[key]
        elif self.mirror:
            return self.transition_probabilities[(b, a)]
        else:
            raise Exception("Unknown key pair / non-mirrored")

    def for_class(self, clsname):
        filtered = {
            k: v for (k, v)
            in self.transition_probabilities.keys()
            if k == clsname
        }
        return filtered


class TowerDistributionManager(DistributionManager):
    mirror = False
    transition_probabilities = {
        ('hallway', 'hallway')           : 0.001,
        ('hallway', 'hallway_jump')      : 0.001,
        ('hallway', 'oriented')          : 0.001,
        ('hallway', 'platform')          : 0.001,
        ('hallway', 'platform_setpiece') : 0.001,
        ('hallway', 'stair')             : 0.001,
        ('hallway', 'vertical')          : 0.001,

        ('hallway_jump', 'hallway')           : 1.4,
        ('hallway_jump', 'hallway_jump')      : 0.01,
        ('hallway_jump', 'oriented')          : 0.8,
        ('hallway_jump', 'platform')          : 0.6,
        ('hallway_jump', 'platform_setpiece') : 0.1,
        ('hallway_jump', 'stair')             : 0.1,
        ('hallway_jump', 'vertical')          : 0.2,

        ('oriented', 'hallway')           : 2.3,
        ('oriented', 'hallway_jump')      : 0.8,
        ('oriented', 'oriented')          : 0.8,
        ('oriented', 'platform')          : 0.6,
        ('oriented', 'platform_setpiece') : 0.2,
        ('oriented', 'stair')             : 0.8,
        ('oriented', 'vertical')          : 1.3,

        ('platform', 'hallway')           : 0.8,
        ('platform', 'hallway_jump')      : 0.4,
        ('platform', 'oriented')          : 0.6,
        ('platform', 'platform')          : 0.1,
        ('platform', 'platform_setpiece') : 0.05,
        ('platform', 'stair')             : 0.3,
        ('platform', 'vertical')          : 0.5,

        ('platform_setpiece', 'hallway')           : 1.8,
        ('platform_setpiece', 'hallway_jump')      : 0.4,
        ('platform_setpiece', 'oriented')          : 0.8,
        ('platform_setpiece', 'platform')          : 0.1,
        ('platform_setpiece', 'platform_setpiece') : 0.01,
        ('platform_setpiece', 'stair')             : 0.2,
        ('platform_setpiece', 'vertical')          : 0.3,

        ('stair', 'hallway')           : 1.6,
        ('stair', 'hallway_jump')      : 0.2,
        ('stair', 'oriented')          : 0.8,
        ('stair', 'platform')          : 1.2,
        ('stair', 'platform_setpiece') : 0.2,
        ('stair', 'stair')             : 0.2,
        ('stair', 'vertical')          : 1.0,

        ('vertical', 'hallway')           : 1.3,
        ('vertical', 'hallway_jump')      : 0.2,
        ('vertical', 'oriented')          : 0.8,
        ('vertical', 'platform')          : 0.5,
        ('vertical', 'platform_setpiece') : 0.1,
        ('vertical', 'stair')             : 0.1,
        ('vertical', 'vertical')          : 0.1,
    }
