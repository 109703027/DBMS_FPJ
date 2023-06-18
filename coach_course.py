import csv
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, Blueprint

coach_course_router = Blueprint("coach_course_router", __name__)
SQLITE_DB_PATH = 'gym.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

@coach_course_router.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('coach_course_router.coach_course', username=request.form.get('username')))
    return render_template('coach_login.html')

@coach_course_router.route('/coachcourse/<username>')
def coach_course(username):
    db = get_db()
    sql = "SELECT DISTINCT c.courseID, c.courseTitle, c.courseDay, c.courseTime, c.dateStart, c.dateEnd, record.evaluate FROM course AS c LEFT JOIN record ON c.courseID = record.courseID WHERE c.coachID = ? ORDER BY c.dateStart DESC, record.evaluate DESC"
    cursor = db.cursor()
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    couchcourse_data = []

    prev_id = None
    for d in data:
        if d[6] == '' and prev_id == d[0]:
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

#@coach_course_router.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    coach_course_router.run(debug=True)
