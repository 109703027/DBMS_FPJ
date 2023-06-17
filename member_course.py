import csv
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, Blueprint

member_course_router = Blueprint("member_course_router", __name__)
SQLITE_DB_PATH = 'gym.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

@member_course_router.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('member_course_router.all_course', username=request.form.get('username')))

    return render_template('mem_login.html')


@member_course_router.route('/course/<username>')
def all_course(username):
    db = get_db()
    money_sql = """SELECT voucher
                   FROM member
                   WHERE memberID = ?"""
    cursor = db.cursor()
    cursor.execute(money_sql, (username,))
    money_data = cursor.fetchone()
    user_data = {
        'ID':username,
        'money':money_data[0]
    }

    sql = """SELECT c.courseTitle, ch.name, c.courseDay, c.courseTime, c.dateStart, c.dateEnd, c.courseID, c.cost, ch.coachID
             FROM course AS c, coach AS ch
             WHERE c.dateStart > date(\'now\') and c.coachID = ch.coachID
             ORDER BY c.dateStart"""
    data = db.execute(sql).fetchall()
    course_data = []
    for d in data:
        
        params1 = (d[6],username)
        params2 = (d[6],)
        params3 = (username,d[5])
        if db.execute("SELECT * FROM record WHERE courseID = ? and memberID = (SELECT memberID FROM member WHERE memberID = ?)",params1).fetchone():
            cond = 1
        elif db.execute("SELECT * FROM record WHERE courseID = ? GROUP BY courseID HAVING COUNT(*) >= 10",params2).fetchone():
            cond = 2
        elif db.execute("SELECT * FROM member WHERE memberID = ? and memberExp < ?",params3).fetchone():
            cond = 3
        else:
            cond = 4

        course_data.append({
            'Title':d[0],
            'c_Name':d[1],
            'Day':d[2]+"  "+d[3],
            'Start':d[4],
            'End':d[5],
            'Condition':cond,
            'courseID':d[6],
            'Cost':d[7],
            'coachID':d[8]
        })
    return render_template(
        'all_course.html',
        user_data = user_data,
        course_data = course_data
    )

@member_course_router.route('/my_course/<username>')
def my_course(username):
    db = get_db()
    sql = """SELECT C.courseTitle, T.name, C.courseDay, C.courseTime, C.dateStart, C.dateEnd, R.evaluate, C.courseID
            FROM course AS C, coach AS T, member as M, record as R
            WHERE C.coachID = T.coachID and R.courseID = C.courseID and R.memberID = M.memberID and M.memberID = ?
            ORDER BY c.dateStart"""
    cursor = db.cursor()
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    course_data = []

    for d in data:
        course_data.append({
            'Title':d[0],
            'c_Name':d[1],
            'Day':d[2]+"  "+d[3],
            'Start':d[4],
            'End':d[5],
            'comment':d[6],
            'courseID':d[7]
        })


    return render_template(
        'my_course.html',
        userID = username,
        course_data = course_data
    )

@member_course_router.route('/save', methods=['POST'])
def save_comment():
    comment = request.form.get('comment')
    userID = request.form.get('userID')
    courseID = request.form.get('courseID')
    db = get_db()
    cursor = db.cursor()
    sql = '''UPDATE record
            set evaluate = ?
            where courseID = ? and memberID = ?'''
    cursor.execute(sql, (comment, courseID, userID))
    db.commit()

    return redirect(url_for('member_course_router.my_course', username=userID))

@member_course_router.route('/insert', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        userID = request.form.get('userID')
        userMoney = int(request.form.get('userMoney'))
        courseID = request.form.get('courseID')
        courseCost = int(request.form.get('courseCost'))

        db = get_db()
        cursor = db.cursor()
        sql = """INSERT INTO record (courseID, memberID, evaluate)
                 VALUES (?, ?, ?)"""
        cursor.execute(sql, (courseID, userID, ""))
        money_sql = """UPDATE member
                       SET voucher = ?
                       WHERE memberID = ?"""
        cursor.execute(money_sql, (userMoney-courseCost, userID))

        db.commit()

    return redirect(url_for('member_course_router.my_course', username=userID))

#@member_course_router.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    member_course_router.run(debug=True)
