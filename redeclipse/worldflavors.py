import logging
log = logging.getLogger(__name__)


def space_station():
    return [
        'gravity 0',
        'impulselimit 120',
        'aircoast 250',
        'impulsestyle 3',
        'impulseregen 1000',
        'impulsecount 10'
    ]


def maliwan():
    return [
        'shotgunrays1 40',
        'shotgunspread1 25',
        'shotgunammoadd 8',
        'shotgunammosub1 4',
        'shotguncolor %d' % 0xff0000,
        'shotgunexplcol1 %d' % 0xff3333,
        'shotgunexplode1 500',
    ]


def crushed_blacks():
    return [
        'ambient 0',
    ]


choices = [
    'space_station',
    'crushed_blacks',
    'maliwan',
]


def update(world, flavors):
    if not flavors:
        return world

    for flavor in flavors:
        extra = globals()[flavor]()
        # Add any config extras.
        world.cfg_extra.extend(extra)

    return world
