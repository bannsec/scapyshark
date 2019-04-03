
import threading
import sqlite3

#
# General Database Handler
#

def init():

    global conn
    global db_lock

    db_lock = threading.Lock()

    # Init our db
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row

def execute(query, args=None, fetch_all=False):
    """Safely (via lock) do the query."""

    if args is None:
        args = tuple()

    ret = None
    with db_lock:

        c = conn.cursor()
        c.execute(query, args)

        if fetch_all:
            ret = c.fetchall()
        
        c.close()
        return ret

def tables():
    """Returns list of tables."""
    rows = execute("SELECT name FROM sqlite_master WHERE type='table';", fetch_all=True)
    return [row['name'] for row in rows]

try:
    conn
except:
    init()
