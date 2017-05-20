from itertools import chain

GenericMaterial = [
    'tex%s' % x for x in
    range(4, 9)
]
FloorMaterial = [
    'tex%s' % x for x in
    chain(range(4, 9), range(92, 116), range(504, 505))
]

ColumnMaterial = [
    'tex%s' % x for x in
    chain(range(504, 507), range(161, 180), [134, 123])
]
WallMaterial = [
    'tex%s' % x for x in
    chain([4], range(504, 505))
]
AccentMaterial = [
    'tex%s' % x for x in
    chain([9, 202, 418, 419, 420, 421], range(505, 507))
]
