
import logging
logger = logging.getLogger('ScapyShark:Sniffer:Handler:DNS')

import sqlite3
import os
import requests
from zipfile import ZipFile
from io import BytesIO

here = os.path.dirname(os.path.realpath(__file__))

def init():
    global conn

    logger.info('Performing init.')

    conn = sqlite3.connect(os.path.join(here, 'dns.db'))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute('SELECT count(*) FROM umbrella')

        # Check that we have a full table and not partial
        r = next(c)
        if r['count(*)'] != 1000000:
            build_umbrella_table()

    except:
        # Table doesn't exist
        build_umbrella_table()

def build_umbrella_table():

    print('Building DNS database. Please be patient... ', flush=True, end='')

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

    print('OK')

def check_umbrella(dns):
    """ Return umbrella rank for the given domain name. """
    c = conn.cursor()
    c.execute('''SELECT * FROM umbrella WHERE dns == ?''', (dns,))

    try:
        r = next(c)
    except:
        # This domain name wasn't found
        return None

    return r['rank']

try:
    conn
except:
    init()

