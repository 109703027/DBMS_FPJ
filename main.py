from flask import Flask, g, Blueprint, render_template
from app import app_router
from member_course import member_course_router
from coach_course import coach_course_router
from coach_courseOfferings import coach_courseOfferings_router
from Equipment import equipment_router
from comm import comm_router

app = Flask(__name__)
app.register_blueprint(app_router)
app.register_blueprint(member_course_router)
app.register_blueprint(coach_course_router)
app.register_blueprint(coach_courseOfferings_router)
app.register_blueprint(equipment_router)
app.register_blueprint(comm_router)

@app.route('/assets/js/main.js')
def js_router():
	return render_template('main.js')

@app.route('/assets/css/main.css')
def css_router():
	return render_template('main.css')

if __name__ == '__main__':
	app.run(debug=True)
