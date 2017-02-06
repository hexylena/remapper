# Map Format

## Header

The first four bytes should be `MAPZ`. The code specifies BFGZ as well, but I haven't seen these myself.

Data               | Position | Size | Example Value
------------------ | -------- | ---- | -------------
Magic              | 0        | 4    | MAPZ
Version            | 4        | 4    | 43
Header Size        | 8        | 4    | 48
World Size         | 12       | 4    | 1024
Number of VSlots   | 16       | 4    | 909
Number of Entities | 20       | 4    | 3
Game Version       | 24       | 4    | 229
Blendmap           | 28       | 4    | 0
Revision           | 32       | 4    | 2
numpvs             | 36       | 4    | 0
lightmaps          | 40       | 4    | 0
gameident | 'fps' 

{'numvars': 155, 'numvslots': 909, 'lightmaps': 0, 'worldsize': 1024, 'revision': 2, 'gamever': 229, 'blendmap': 0, 'numpvs': 0, 'gameident': b'fps', 'numents': 3}
This essentially marks the end of the header
