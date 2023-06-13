from flask import Flask, g, Blueprint
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

if __name__ == '__main__':
	app.run(debug=True)
