# Map CFG Format

The .cfg file contains texture and resource mappings as well as hand-editable
map parameters. We will completely ignore those parameters because they're
commented out and stored in the binary file.

## Textures

Here's an example

```
setshaderparam specscale 0.250000 0.250000 0.250000 0.000000
texture c "trak/trak6/tile3.jpg" 0 0 0 0.250000 // 2
texture n "trak/trak6/tile3_nm.png"
texture s "trak/trak6/tile3_gloss.jpg"
```

The texture statement seems to be:

```
texture c [file] [args]
```

then one or more of

```
texture [type] [category] [file]
```

Type Characters:

Short Code | Type
---------- | ---
`c `       | Diffuse
`u `       | Unknown
`d `       | Decal
`n `       | Normal
`g `       | Glow
`s `       | Spec
`z `       | Depth
`e `       | Envmap


## Unknown

```

texture water "textures/waterfall.jpg" 0 0 0 1.000000
texture 1 "textures/waterfall.jpg"
texture 1 "textures/watern.jpg"
texture 1 "textures/waterdudv.jpg"
texture 1 "textures/waterfalln.jpg"
texture 1 "textures/waterfalldudv.jpg"

texture water2 "textures/waterfall.jpg" 0 0 0 1.000000
texture 1 "textures/waterfall.jpg"
texture 1 "textures/watern.jpg"
texture 1 "textures/waterdudv.jpg"
texture 1 "textures/waterfalln.jpg"
texture 1 "textures/waterfalldudv.jpg"

texture water3 "textures/waterfall.jpg" 0 0 0 1.000000
texture 1 "textures/waterfall.jpg"
texture 1 "snipergoth/watern.jpg"
texture 1 "snipergoth/waterdudv.jpg"
texture 1 "textures/waterfalln.jpg"
texture 1 "textures/waterfalldudv.jpg"

texture water4 "textures/waterfall.jpg" 0 0 0 1.000000
texture 1 "textures/waterfall.jpg"
texture 1 "snipergoth/watern.jpg"
texture 1 "snipergoth/waterdudv.jpg"
texture 1 "textures/waterfalln.jpg"
texture 1 "textures/waterfalldudv.jpg"

texture lava "textures/lava.jpg" 0 0 0 1.000000
texture 1 "textures/lava.jpg"

texture lava2 "textures/lava.jpg" 0 0 0 1.000000
texture 1 "textures/lava.jpg"

texture lava3 "textures/lava.jpg" 0 0 0 1.000000
texture 1 "textures/lava.jpg"

texture lava4 "textures/lava.jpg" 0 0 0 1.000000
texture 1 "textures/lava.jpg"

setshader stdworld
texture c "textures/sky.png" 0 0 0 1.000000 // 0

setshader stdworld
texture c "textures/default.png" 0 0 0 0.500000 // 1

setshader bumpspecmapworld
setshaderparam specscale 0.250000 0.250000 0.250000 0.000000
texture c "trak/trak6/tile3.jpg" 0 0 0 0.250000 // 2
texture n "trak/trak6/tile3_nm.png"
texture s "trak/trak6/tile3_gloss.jpg"

setshader bumpworld
texture c "appleflap/randomwoodthing.jpg" 0 0 0 1.000000 // 3
texture n "appleflap/randomwoodthing_nm.jpg"

setshader bumpspecmapglowworld
texture c "appleflap/floor.jpg" 0 0 0 1.000000 // 4
texture n "appleflap/floor_nm.jpg"
texture s "appleflap/floor_spec.jpg"
texture g "appleflap/floor_glow.jpg"

setshader glowworld
texture c "appleflap/applequote.jpg" 0 0 0 1.000000 // 5
texture g "appleflap/applequote_g.jpg"
texscroll 0.100000 0.000000

setshader bumpspecmapparallaxworld
setshaderparam specscale 1.000000 1.000000 1.000000 0.000000
setshaderparam parallaxscale 0.028000 0.000000 0.000000 0.000000
texture c "dziq/boards01.jpg" 0 0 0 1.000000 // 6
texture n "dziq/boards01_n.jpg"
texture z "dziq/boards01_b.jpg"
texture s "dziq/boards01_s.jpg"
```
