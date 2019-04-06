
#
# Simple abstractions for MAC OUI Lookups
#

import logging
logger = logging.getLogger(__name__)

import os
from . import db

here = os.path.dirname(os.path.realpath(__file__))
oui_db = os.path.join(here, 'oui.db')

def init():
    global done_init

    db.execute("ATTACH DATABASE '{}' as oui_lookup".format(oui_db))

    done_init = True

def lookup(oui):
    """Lookup OUI and return answer.

    Args:
        oui (int, bytes): OUI to check manufacturer.

    Returns:
        str answer, or None if it could not be found."""

    assert isinstance(oui, (int, bytes)), "OUI must be of type int or bytes, not {}".format(type(oui))

    if type(oui) is bytes:
        oui = oui.replace(b":",b"").replace(b"-",b"")[0:6]
        oui = int(oui,16)

    if oui > 0xffffff:
        logger.error("OUI too big... If using int, just make int of first 3 bytes.")
        return

    rows = db.execute("SELECT name FROM oui_lookup WHERE prefix == ?", (oui,), fetch_all=True)

    if rows == []:
        return None

    return rows[0]['name']


try:
    done_init
except:
    init()
