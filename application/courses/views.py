from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

from application import app, db, login_required
from application.courses.models import Course
from application.reservations.models import Reservation
from application.topics import models
from application.auth import models
from application.courses.forms import CourseForm
from application.reservations import views
from application.reservations.forms import ReservationForm

@app.route("/courses/user_course/")
@login_required(role="ANY")
def my_courses():
	return render_template("courses/user_courses.html", my_courses=Course.find_my_courses(current_user.id))
	
@app.route("/courses/user_course/<course_id>", methods=["POST"])
@login_required(role="ANY")
def delete_attendance(course_id):
	Reservation.query.filter_by(course_id=course_id).filter_by(account_id=current_user.id).delete()
	
	course = Course.query.filter_by(id=course_id).first()
	course.users.clear()
	db.session().commit()
	return render_template("courses/user_courses.html", my_courses=Course.find_my_courses(current_user.id))

@app.route("/courses/<course_id>/info", methods=["POST"])
def course_info(course_id):
	return render_template("courses/info.html", courses = Course.query.filter_by(id=course_id))

@app.route("/courses", methods=["GET"])
def courses_index():
	return render_template("courses/list.html", courses = Course.query.all())

@app.route("/courses/<course_id>/", methods=["POST"])
@login_required(role="ADMIN")
def delete_course(course_id):

	Course.query.filter_by(id=course_id).delete()
	db.session().commit()
	
	return redirect(url_for("courses_index"))

@app.route("/courses/new")
@login_required(role="ADMIN")
def courses_form():
	return render_template("courses/new.html", form = CourseForm())

@app.route("/courses/", methods=["POST"])
@login_required(role="ADMIN")
def courses_create():
	form = CourseForm(request.form)
	
	if not form.validate():
		return render_template("courses/new.html", form = form)
	
	course = Course(form.name.data, form.datestart.data, form.dateend.data, form.place.data, 
					form.teachers.data, form.desc.data, form.topic.data)
					
	db.session().add(course)
	db.session().commit()
	
	return redirect(url_for("courses_index"))