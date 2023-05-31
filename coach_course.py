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
        return redirect(url_for('coach_course', username=request.form.get('username')))
    return render_template('coach_login.html')

@app.route('/coachcourse/<username>')
def coach_course(username):
    db = get_db()
    sql = "SELECT distinct c.courseID, c.courseTitle, c.courseDay, c.courseTime, c.dateStart, c.dateEnd, record.evaluate               FROM course as c, coach, record                                                                                             WHERE c.coachID = ? and c.courseID = record.courseID                                                                        ORDER BY c.dateStart desc, record.evaluate desc"
    cursor = db.cursor()
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    couchcourse_data = []

    prev_id = None
    for d in data:
        if prev_id is not None and d[6] == '':
            continue
        course = {
            'ID':d[0],
            'Title':d[1],
            'Day':d[2]+"  "+d[3],
            'Start':d[4],
            'End':d[5],
            'comment':d[6],
        }
        if prev_id is not None and prev_id == d[0]:
            course['ID'] = ''
            course['Title'] = ''
            course['Day'] = ''
            course['Start']=''
            course['End']=''

        prev_id = d[0]
        couchcourse_data.append(course)

    return render_template(
        'coach_course.html',
        userID = username,
        couchcourse_data = couchcourse_data
    )

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
