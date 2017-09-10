docs:
	sphinx-apidoc -o docs redeclipse -e -M 
	cd docs && $(MAKE) html

.PHONY: docs
