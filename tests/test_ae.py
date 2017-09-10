from redeclipse import aftereffects as ae

def test_vertical_gradient():
    assert ae.vertical_gradient(0, 0, 0) == 1.0
    assert ae.vertical_gradient(0, 0, 256) == 1.0
