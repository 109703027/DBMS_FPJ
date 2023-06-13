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
	return render_template('login.html')

@app_router.route('/login_error')
def wrong():
	return render_template('wrong.html')

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
		return redirect(url_for('app_router.base'))
	else:
		# Login failed, redirect back to the login form with an error message
		return redirect(url_for('app_router.wrong'))


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
		return redirect(url_for('app_router.login'))
	
	return render_template('register.html')


@app_router.route('/base')
def base():
	return render_template('base.html')


#@app_router.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()


if __name__ == '__main__':
	app_router.run(debug=True)
