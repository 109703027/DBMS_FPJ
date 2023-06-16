#看見賬號後的確定按鈕
import sqlite3
from flask import Flask, g, Blueprint
from flask import render_template, request, redirect, url_for
import datetime

#hi
#app_router = Flask(__name__)
app_router = Blueprint("app_router", __name__)
SQLITE_DB_PATH = 'gym.db'


def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(SQLITE_DB_PATH)
		# Enable foreign key check
		db.execute("PRAGMA foreign_keys = ON")
	return db


@app_router.route('/')
def start():
	return render_template('login_new.html')


@app_router.route('/login_error')
def login_wrong():
	return render_template('login_wrong.html')


@app_router.route('/forget_error')
def forget_wrong():
	return render_template('forget_wrong.html')

@app_router.route('/login', methods=['POST'])
def login():
	username = request.form['Uname']
	password = request.form['Pass']

	db = get_db()

	# Check if the username and password exist in the member table
	query = "SELECT * FROM member WHERE memberID = ? AND birth = ?"
	cursor = db.execute(query, (username, password))
	result = cursor.fetchone()

	if result:
		# Login successful, redirect to a success page
		return redirect(url_for('app_router.frame', username=username))
	else:
		query = "SELECT * FROM coach WHERE coachID = ? AND birth = ?"
		cursor = db.execute(query, (username, password))
		result = cursor.fetchone()
		if result:
			# Login successful, redirect to a success page
			return redirect(url_for('app_router.frame', username=username))
	
		# Login failed, redirect back to the login form with an error message
		return redirect(url_for('app_router.login_wrong'))


@app_router.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		name = request.form['name']
		sex = request.form['sex']
		birth = request.form['birth']
		phone = request.form['phone']
		address = request.form['address']
		email = request.form['email']
		
		db = get_db()
		cursor = db.cursor()
		query = "SELECT COUNT(*) FROM member"
		cursor.execute(query)
		result = cursor.fetchone()
		num = result[0]+1
		memberID = 'M0' + str(num)

		memberExp = datetime.date.today()
		memberExp = memberExp.year + 1

		cursor = db.cursor()
		query = "INSERT INTO member (memberID, name, sex, birth, phone, email, address, memberExp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
		cursor.execute(query, (memberID, name, sex, birth, phone, email, address, memberExp))
		db.commit()
		
		# 注册成功后重定向到登录页面
		return render_template('register_success.html', member_id = memberID)
	
	return render_template('register.html')


@app_router.route('/forget_id', methods=['GET', 'POST'])
def forget_id():
	if request.method == 'POST':
		name = request.form['name']
		birth = request.form['birth']
		phone = request.form['phone']
		email = request.form['email']

		db = get_db()

		query = "SELECT memberID FROM member WHERE name = ? AND birth = ? AND phone = ? AND email = ?"
		cursor = db.execute(query, (name, birth, phone, email))
		result = cursor.fetchone()

		if result:
			return render_template('show_id.html', member_id = result[0])
		else:
			return redirect(url_for('app_router.forget_wrong'))
	return render_template('forget_id.html')


@app_router.route('/member_profile/<username>', methods=['GET', 'POST'])
def member_profile(username):
    db = get_db()
    query = "SELECT * FROM member WHERE memberID = ?"
    data = db.execute(query, (username,)).fetchall()
    member_data = []
    for d in data:
        
        member_data.append({
            'id':d[0],
            'name':d[1],
            'sex':d[2],
            'birth':d[3],
            'phone':d[4],
            'email':d[5],
            'address':d[6],
            'memExp':d[7],
            'voucher':d[8]
        })
    
    return render_template(
        'member_profile.html',
        member_data = member_data,
    )


@app_router.route('/coach_profile/<username>', methods=['GET', 'POST'])
def coach_profile(username):
    db = get_db()
    query = "SELECT * FROM coach WHERE coachID = ?"
    data = db.execute(query, (username,)).fetchall()
    coach_data = []
    for d in data:
        
        coach_data.append({
            'id':d[0],
            'name':d[1],
            'expertise':d[2],
            'experience':d[3],
            'birth':d[4],
        })
    
    query2 = "SELECT courseID FROM course WHERE coachID = ?"
    data2 = db.execute(query2, (username,)).fetchall()
    coach_course = [row[0] for row in data2]
    # print(coach_course)
    
    return render_template(
        'coach_profile.html',
        coach_data = coach_data,
		coach_course = coach_course
    )


@app_router.route('/evaluate/<course_id>', methods=['GET', 'POST'])
def evaluate(course_id):
    db = get_db()
    query = "SELECT * FROM record WHERE courseID = ?"
    data = db.execute(query, (course_id,)).fetchall()
    # print(data[0])
    # print('hi')

    return render_template('evaluate.html', course_ev = data)


@app_router.route('/frame/<username>')
def frame(username):
    if username[0] == "M":
        root = "/member_base/"+username
        start_root = "/my_course/"+username
    else:
        root = "/coach_base/"+username
        start_root = "/coachcourse/"+username

    return render_template(
        'frame.html',
        root = root,
        start_root = start_root
    )


@app_router.route('/member_base/<username>')
def member_base(username):
    return render_template(
                'member_base.html',
                root="/my_course/"+username,
                course_root = "/course/"+username,
				profile_root = "/member_profile/"+username,
				comm_root = "/commodity/"+username
				# eq_root = "/equipment_router"+username
    )


@app_router.route('/coach_base/<username>')
def coach_base(username):
	return render_template(
		'coach_base.html',
		root="/coachcourse/"+username,
		coach_root = "/coach_profile/"+username,
		coach_Offerings = "/Offerings/" + username,
		# eq_root = "/equipment_router"+username
)


#@app_router.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()


if __name__ == '__main__':
	app_router.run(debug=True)
