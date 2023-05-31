import csv
import sqlite3
from flask import Flask, g
from flask import Flask, render_template, request

app = Flask(__name__)
SQLITE_DB_PATH = 'gym.db'
# db = sqlite3.connect(SQLITE_DB_PATH)
# c = db.execute('Select * from coach')
# for row in c:
#     print(row)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    coachID = 'T123'
    if request.method == 'POST':
        course_title = request.form.get('title')
        course_price = request.form.get('price')
        course_start_date = request.form.get('start_date')
        course_end_date = request.form.get('end_date')
        course_weekday = request.form.get('weekday')
        course_start_time = request.form.get('start_time')
        course_end_time = request.form.get('end_time')

        db = get_db()
        course_sum = db.execute('Select count(*) from course').fetchone()
        course_number = 'C{:03d}'.format(course_sum[0] + 1)

        # 處理網站上收到的課程資料
        # print(course_number, course_title, course_price, course_start_date, course_end_date, course_weekday, course_start_time, course_end_time)
        course_title = course_title.capitalize()
        course_start_time = course_start_time.replace(':','')
        course_end_time = course_end_time.replace(':','')
        course_time = str(course_start_time) + '-' + str(course_end_time)
        course_weekday = course_weekday[:3].capitalize()

        course_cursor = db.cursor()
        course_sql = "INSERT INTO course (courseID, courseTitle, cost, dateStart, dateEnd, courseDay, courseTime, coachID) \
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        course_cursor.execute(course_sql, (course_number, course_title, course_price, course_start_date, course_end_date, course_weekday, course_time, coachID))

        db.commit()
        db.close()

    return render_template('coach_courseOfferings.html')


if __name__ == '__main__':
    app.run(debug=True)
