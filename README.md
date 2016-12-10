# Redeclipse map library

Library to read in Red Eclipse maps. It isn't polished, but currently will read
in very, very simple maps.

The end goal is to allow for automated generation of maps.

## Scripts

A couple of scripts are shipped with this library:

Script      | Purpose
----------- | ----
`to_json`   | Converts map to a JSON representation which can be operated on by other tools
`from_json` | Deserializes map back into binary representation (WIP)
`add_trees` | Randomly add trees at z=512, across x, y in (0, 1024)

# License

GPLv3
