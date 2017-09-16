Redeclipse map library 
======================

.. image:: https://travis-ci.org/erasche/remapper.svg?branch=master
   :target: https://travis-ci.org/erasche/remapper

.. image:: https://readthedocs.org/projects/remapper/badge/?version=latest
   :target: https://travis-ci.org/erasche/remappe://remapper.readthedocs.io/en/latest/

.. figure:: ./maps/hxr-4-straumsvik.screenshot.png
   :alt: 

Library to read and write Red Eclipse maps. It isn't polished, but is
"good enough". My gaming group and I play "sniper-counter-sniper", a
very unusual mode for most people who play redeclipse. It involves
stalking and sniping each other, movement speed is nerfed, you have to
listen and watch and be observant and it can be scary as hell. This
library was written to generate some new maps for us to play on, since
none of the existing maps fit extremely well with that style of play.

Here you will find tools for parsing and writing redeclipse maps, and a
voxel→octree translation routine which allows you to construct simple
voxel worlds and have them rendered into a redeclipse octree. You could
theoretically import your minecraft world, if you wished.

See the `maps folder <./maps/>`__ for screenshots and maps you can play

Updates
-------

Some new features and new rooms:

.. figure:: ./maps/straumsvik.screenshot.png
   :alt: 

First enjoyable map: Trollskogen

.. figure:: ./maps/trollskogen-big.png
   :alt: 

Second enjoyable map: Bergen

.. figure:: ./maps/bergen-big.png
   :alt: 

Third map: Lillehammer (with day/night versions)

|image0| |image1|

Screenshots from development:

|image2| |image3|

Humble beginnings:

.. figure:: ./media/random.png
   :alt: 

The textures in the above map were built from `havenlau's rounded pixel
texture
pack <http://www.minecraftforum.net/forums/mapping-and-modding/resource-packs/1237362-32x-64x-1-0-0-rounded-pixel-under-construction>`__

Examples
--------

.. code:: console

    $ redeclipse_voxel_2 ./test/empty.mpz ~/.redeclipse/maps/minecraft.mpz
    $ redeclipse_cfg_gen my-texture-directory/ > ~/.redeclipse/maps/minecraft.cfg

License
=======

GPLv3

.. |image0| image:: ./maps/lillehammer-day-2.png
.. |image1| image:: ./maps/lillehammer-night-2.png
.. |image2| image:: ./maps/sandvika.png
.. |image3| image:: ./maps/fjell-big.png
