import csv
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for

app = Flask(__name__)
SQLITE_DB_PATH = 'gym.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('all_course', username=request.form.get('username')))

    return render_template('mem_login.html')


@app.route('/course/<username>')
def all_course(username):
    db = get_db()
    sql = "SELECT c.courseTitle, ch.name, c.courseDay, c.courseTime, c.dateStart, c.dateEnd FROM course AS c, coach AS ch WHERE c.dateStart > date(\'now\') and c.coachID == ch.coachID ORDER BY c.dateStart"
    data = db.execute(sql).fetchall()
    course_data = []
    for d in data:
        course_data.append({
            'Title':d[0],
            'c_Name':d[1],
            'Day':d[2]+"  "+d[3],
            'Start':d[4],
            'End':d[5]
        })
    return render_template(
        'all_course.html',
        username = username,
        course_data = course_data
    )


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
