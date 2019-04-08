
import os
import sqlite3
import requests
from zipfile import ZipFile
from io import BytesIO
from . import db

here = os.path.dirname(os.path.realpath(__file__))
umbrella_db_file = os.path.join(here, 'umbrella.db')

def build_umbrella_table():

    print('Building DNS database. Please be patient... ', flush=True, end='')

    conn = sqlite3.connect(umbrella_db_file)
    conn.row_factory = sqlite3.Row

    # Blow away table if it is there
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS umbrella''')

    c.execute('''CREATE TABLE umbrella (rank int, dns text PRIMARY KEY)''')
    r = requests.get('http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip')
    zip_f = BytesIO(r.content)
    z = ZipFile(zip_f,'r')
    csv = z.read(z.filelist[0]).decode().strip() # Extract csv

    for line in csv.split('\n'):
        line = line.strip()
        c.execute('''INSERT INTO umbrella values (?, ?)''', line.split(','))

    conn.commit()
    c = conn.cursor()
    c.execute('''VACUUM''')
    conn.commit()
    c.close()
    conn.close()

    print('OK')

def check_umbrella(dns):
    """ Return umbrella rank for the given domain name. """
    rows = db.execute('''SELECT * FROM umbrella WHERE dns == ?''', (dns,), fetch_all=True)

    if rows == []:
        return None

    return rows[0]['rank']

def init():
    global done_init

    if not os.path.exists(umbrella_db_file):
        build_umbrella_table()

    db.execute("ATTACH DATABASE '{}' as umbrella".format(umbrella_db_file))

    try:
        rows = db.execute('SELECT count(*) FROM umbrella', fetch_all=True)

        # Check that we have a full table and not partial
        if rows[0]['count(*)'] != 1000000:
            build_umbrella_table()

    except:
        # Table doesn't exist
        build_umbrella_table()

        # TODO: How would the attached DB handle this change?!

    done_init = True

try:
    done_init
except:
    init()
