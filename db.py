import sqlite3
import unicodedata
import os
import sys
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clima.db')

def collate_noaccent(a, b):
    def norm(s):
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    a = norm(a)
    b = norm(b)
    if a < b:
        return -1
    elif a > b:
        return 1
    return 0

def init_app(app):
    app.teardown_appcontext(close_db)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.create_collation("noaccent", collate_noaccent)
    return g.db

def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        if exception is None:
            db.commit()
        db.close()

def init_db(app):
    db = get_db()
    with app.open_resource('schema.sql', mode='rb') as f:
        db.executescript(f.read().decode('utf-8'))

    count = db.execute("SELECT COUNT(*) as c FROM usuarios").fetchone()['c']
    if count == 0:
        with app.open_resource('seed.sql', mode='rb') as f:
            db.executescript(f.read().decode('utf-8'))
    db.commit()
