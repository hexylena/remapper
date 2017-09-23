GOXEL:=~/projects/goxel/goxel

docs:
	sphinx-apidoc -o docs redeclipse -e -M 
	cd docs && $(MAKE) html


GOX_FILES := $(wildcard redeclipse/prefabs/*.gox)
VOX_FILES := $(GOX_FILES:.gox=.vox)

vox_files: $(VOX_FILES)

%.vox: %.gox
	-../goxel/goxel -e $@ $<

.PHONY: docs vox_files tmp.vox
