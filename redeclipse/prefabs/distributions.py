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
            v: self.transition_probabilities[k, v] for (k, v)
            in self.transition_probabilities.keys()
            if k == clsname.room_type
        }
        return filtered


class UniformDistributionManager(DistributionManager):
    mirror = False
    transition_probabilities = {
        ('hallway', 'hallway')           : 1,
        ('hallway', 'hallway_jump')      : 1,
        ('hallway', 'oriented')          : 1,
        ('hallway', 'platform')          : 1,
        ('hallway', 'platform_setpiece') : 1,
        ('hallway', 'stair')             : 1,
        ('hallway', 'vertical')          : 1,

        ('hallway_jump', 'hallway')           : 1,
        ('hallway_jump', 'hallway_jump')      : 1,
        ('hallway_jump', 'oriented')          : 1,
        ('hallway_jump', 'platform')          : 1,
        ('hallway_jump', 'platform_setpiece') : 1,
        ('hallway_jump', 'stair')             : 1,
        ('hallway_jump', 'vertical')          : 1,

        ('oriented', 'hallway')           : 1,
        ('oriented', 'hallway_jump')      : 1,
        ('oriented', 'oriented')          : 1,
        ('oriented', 'platform')          : 1,
        ('oriented', 'platform_setpiece') : 1,
        ('oriented', 'stair')             : 1,
        ('oriented', 'vertical')          : 1,

        ('platform', 'hallway')           : 1,
        ('platform', 'hallway_jump')      : 1,
        ('platform', 'oriented')          : 1,
        ('platform', 'platform')          : 1,
        ('platform', 'platform_setpiece') : 1,
        ('platform', 'stair')             : 1,
        ('platform', 'vertical')          : 1,

        ('platform_setpiece', 'hallway')           : 1,
        ('platform_setpiece', 'hallway_jump')      : 1,
        ('platform_setpiece', 'oriented')          : 1,
        ('platform_setpiece', 'platform')          : 1,
        ('platform_setpiece', 'platform_setpiece') : 1,
        ('platform_setpiece', 'stair')             : 1,
        ('platform_setpiece', 'vertical')          : 1,

        ('stair', 'hallway')           : 1,
        ('stair', 'hallway_jump')      : 1,
        ('stair', 'oriented')          : 1,
        ('stair', 'platform')          : 1,
        ('stair', 'platform_setpiece') : 1,
        ('stair', 'stair')             : 1,
        ('stair', 'vertical')          : 1,

        ('vertical', 'hallway')           : 1,
        ('vertical', 'hallway_jump')      : 1,
        ('vertical', 'oriented')          : 1,
        ('vertical', 'platform')          : 1,
        ('vertical', 'platform_setpiece') : 1,
        ('vertical', 'stair')             : 1,
        ('vertical', 'vertical')          : 1,
    }

class TowerDistributionManager(DistributionManager):
    mirror = False
    transition_probabilities = {
        ('hallway', 'hallway')           : 0.7,
        ('hallway', 'hallway_jump')      : 0.1,
        ('hallway', 'oriented')          : 0.7,
        ('hallway', 'platform')          : 0.3,
        ('hallway', 'platform_setpiece') : 0.4,
        ('hallway', 'stair')             : 1.0,
        ('hallway', 'vertical')          : 1.0,

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

class PlatformDistributionManager(DistributionManager):
    mirror = False
    transition_probabilities = {
        ('hallway', 'hallway')           : 3.7,
        ('hallway', 'hallway_jump')      : 1.1,
        ('hallway', 'oriented')          : 1.7,
        ('hallway', 'platform')          : 0.3,
        ('hallway', 'platform_setpiece') : 0.1,
        ('hallway', 'stair')             : 3.0,
        ('hallway', 'vertical')          : 1.0,

        ('hallway_jump', 'hallway')           : 3.4,
        ('hallway_jump', 'hallway_jump')      : 0.1,
        ('hallway_jump', 'oriented')          : 0.8,
        ('hallway_jump', 'platform')          : 0.1,
        ('hallway_jump', 'platform_setpiece') : 0.1,
        ('hallway_jump', 'stair')             : 3.0,
        ('hallway_jump', 'vertical')          : 1.2,

        ('oriented', 'hallway')           : 8.3,
        ('oriented', 'hallway_jump')      : 0.8,
        ('oriented', 'oriented')          : 0.8,
        ('oriented', 'platform')          : 0.2,
        ('oriented', 'platform_setpiece') : 0.1,
        ('oriented', 'stair')             : 1.8,
        ('oriented', 'vertical')          : 1.3,

        ('platform', 'hallway')           : 8.8,
        ('platform', 'hallway_jump')      : 0.4,
        ('platform', 'oriented')          : 1.6,
        ('platform', 'platform')          : 0.1,
        ('platform', 'platform_setpiece') : 0.2,
        ('platform', 'stair')             : 1.3,
        ('platform', 'vertical')          : 0.5,

        ('platform_setpiece', 'hallway')           : 8.8,
        ('platform_setpiece', 'hallway_jump')      : 0.4,
        ('platform_setpiece', 'oriented')          : 0.8,
        ('platform_setpiece', 'platform')          : 0.1,
        ('platform_setpiece', 'platform_setpiece') : 0.1,
        ('platform_setpiece', 'stair')             : 0.2,
        ('platform_setpiece', 'vertical')          : 0.3,

        ('stair', 'hallway')           : 8.6,
        ('stair', 'hallway_jump')      : 1.2,
        ('stair', 'oriented')          : 0.8,
        ('stair', 'platform')          : 0.2,
        ('stair', 'platform_setpiece') : 0.1,
        ('stair', 'stair')             : 1.2,
        ('stair', 'vertical')          : 1.0,

        ('vertical', 'hallway')           : 8.3,
        ('vertical', 'hallway_jump')      : 0.2,
        ('vertical', 'oriented')          : 0.8,
        ('vertical', 'platform')          : 0.1,
        ('vertical', 'platform_setpiece') : 0.1,
        ('vertical', 'stair')             : 1.0,
        ('vertical', 'vertical')          : 0.1,
    }
