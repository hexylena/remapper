# Redeclipse map library

Library to read in Red Eclipse maps. It isn't polished, but currently will read and write very simple maps.

First playable map! (Albeit specifically for the game mode we play, sniper-counter-sniper.)

![](./media/trollskogen.png)

The end goal is to allow for automated generation of maps.

![](./media/random.png)

The textures in this map were built from [havenlau's rounded pixel texture pack](http://www.minecraftforum.net/forums/mapping-and-modding/resource-packs/1237362-32x-64x-1-0-0-rounded-pixel-under-construction)

## Scripts

A couple of scripts are shipped with this library:

Script                 | Purpose
-----------            | ----
`redeclipse_iso`       | Reads and writes a map, completely unchanged. They *should* be bit-for-bit identical.
`redeclipse_to_json`   | Converts map to a JSON representation which can be operated on by other tools.
`redeclipse_from_json` | Deserializes map back into binary representation (WIP).
`redeclipse_add_trees` | Randomly add trees entities at z=512, across x, y in (0, 1024). Used mostly during my testing.
`redeclipse_cfg_gen`   | Given a directory, build a config file to allow using those textures.
`redeclipse_voxel_1`   | The "tutorial" script which demos adding a line of cubes at across a map diagonally.
`redeclipse_voxel_2`   | First real "test" map with automated landscape, trees, "houses".
`redeclipse_voxel_3`   | Some experiments with pre-fab rooms. WIP.

## Examples

```console
$ redeclipse_voxel_2 ./test/empty.mpz ~/.redeclipse/maps/minecraft.mpz
$ redeclipse_cfg_gen my-texture-directory/ > ~/.redeclipse/maps/minecraft.cfg
```

# License

GPLv3
