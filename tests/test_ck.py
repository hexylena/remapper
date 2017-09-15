from redeclipse.prefabs import Room
from redeclipse.vector import CoarseVector, FineVector
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST
from redeclipse.prefabs.construction_kit import wall_points, column_points, ConstructionKitMixin


def test_wall_points():
    a = list(wall_points(
        4, '-z'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(i, j, 0) in a
