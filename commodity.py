import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for
import datetime

app = Flask(__name__)
SQLITE_DB_PATH = 'gym.db'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(SQLITE_DB_PATH)
		# Enable foreign key check
		db.execute("PRAGMA foreign_keys = ON")
	return db


@app.route('/', methods = ['GET','POST'])
def commodity():
    db = get_db()
    sql = "SELECT commodityID, name, cost, store FROM commodity WHERE store > 0"
    data = db.execute(sql).fetchall()
    comm_data = []
    for d in data:
        
        comm_data.append({
            'id':d[0],
            'name':d[1],
            'cost':d[2],
            'store':d[3]
        })
    
    return render_template(
        'commodity.html',
        comm_data = comm_data,
    )


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)