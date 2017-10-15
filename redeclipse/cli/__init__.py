import logging
from redeclipse import MapParser

log = logging.getLogger(__name__)


def parse(input):
    mp = MapParser()
    return mp.read(input)
