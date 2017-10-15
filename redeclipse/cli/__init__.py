import logging
import random
from redeclipse import MapParser
from tqdm import tqdm

log = logging.getLogger(__name__)


def parse(input):
    mp = MapParser()
    return mp.read(input)

