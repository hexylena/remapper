GOXEL:=~/projects/goxel/goxel

docs:
	sphinx-apidoc -o docs redeclipse -e -M 
	cd docs && $(MAKE) html


GOX_FILES := $(wildcard redeclipse/prefabs/original/*.gox) $(wildcard redeclipse/prefabs/spacestation/*.gox) $(wildcard redeclipse/prefabs/castle/*.gox) $(wildcard redeclipse/prefabs/dungeon/*.gox) $(wildcard redeclipse/prefabs/egypt/*.gox)
VOX_FILES := $(GOX_FILES:.gox=.vox)

vox_files: $(VOX_FILES)

%.vox: %.gox
	-../goxel/goxel -e $@ $<

.PHONY: docs vox_files tmp.vox
