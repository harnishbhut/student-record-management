"""
app.py - Main Flask Application for Student Record Management System.

This module defines:
1. Web routes serving traditional HTML pages with Jinja2 templates.
2. REST API endpoints providing JSON responses with proper HTTP status codes.
"""

import os
import re
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
import database

VALID_YEARS = ["Year 1", "Year 2", "Year 3", "Year 4"]
STANDARD_COURSES = [
    "Computer Science",
    "Information Technology",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Business Administration",
    "Civil Engineering"
]


def validate_student_input(data, student_id=None, db_name=None):
    """
    Validate student form/JSON input.
    Returns a dictionary of error messages by field name.
    """
    errors = {}
    full_name = data.get("full_name", "").strip() if data.get("full_name") else ""
    email = data.get("email", "").strip() if data.get("email") else ""
    course = data.get("course", "").strip() if data.get("course") else ""
    year_of_study = data.get("year_of_study", "").strip() if data.get("year_of_study") else ""
    admission_date = data.get("admission_date", "").strip() if data.get("admission_date") else ""

    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters long."

    if not email:
        errors["email"] = "Email address is required."
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors["email"] = "Please enter a valid email address (e.g., student@example.edu)."
    else:
        existing = database.get_student_by_email(email, db_name=db_name)
        if existing and (student_id is None or existing["id"] != int(student_id)):
            errors["email"] = "A student with this email address already exists."

    if not course:
        errors["course"] = "Course name is required."

    if not year_of_study:
        errors["year_of_study"] = "Year of study is required."
    elif year_of_study not in VALID_YEARS:
        errors["year_of_study"] = f"Year of study must be one of: {', '.join(VALID_YEARS)}."

    if not admission_date:
        errors["admission_date"] = "Admission date is required."
    else:
        try:
            datetime.strptime(admission_date, "%Y-%m-%d")
        except ValueError:
            errors["admission_date"] = "Admission date must be formatted as YYYY-MM-DD."

    return errors


def create_app(db_name=None):
    """
    Application factory to create and configure Flask app.
    Allows passing a custom database name for unit testing.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "student-record-mgmt-secret-2026")
    app.config["DB_NAME"] = db_name or database.DEFAULT_DB_NAME

    # Initialize SQLite database and tables
    database.init_db(app.config["DB_NAME"])

    # -------------------------------------------------------------
    # FRONTEND WEB ROUTES
    # -------------------------------------------------------------

    @app.route("/")
    def index():
        """Home page with welcome banner and quick action buttons."""
        return render_template("index.html")

    @app.route("/students")
    def student_list():
        """
        Student records table view.
        Supports search query (by student name or ID) and course filtering.
        """
        search_query = request.args.get("search", "").strip()
        course_filter = request.args.get("course", "").strip()

        students = database.get_all_students(
            search=search_query,
            course=course_filter,
            db_name=app.config["DB_NAME"]
        )

        # Merge standard course options with courses found in database
        db_courses = database.get_all_courses(db_name=app.config["DB_NAME"])
        all_courses = sorted(list(set(STANDARD_COURSES + db_courses)))

        return render_template(
            "students.html",
            students=students,
            search_query=search_query,
            course_filter=course_filter,
            courses=all_courses
        )

    @app.route("/students/add", methods=["GET", "POST"])
    def add_student_page():
        """Register a new student with validation."""
        errors = {}
        form_data = {
            "full_name": "",
            "email": "",
            "phone": "",
            "course": "",
            "year_of_study": "",
            "admission_date": datetime.today().strftime("%Y-%m-%d")
        }

        if request.method == "POST":
            form_data = {
                "full_name": request.form.get("full_name", ""),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
                "course": request.form.get("course", ""),
                "year_of_study": request.form.get("year_of_study", ""),
                "admission_date": request.form.get("admission_date", "")
            }

            errors = validate_student_input(form_data, db_name=app.config["DB_NAME"])

            if not errors:
                new_id = database.add_student(
                    full_name=form_data["full_name"],
                    email=form_data["email"],
                    phone=form_data["phone"],
                    course=form_data["course"],
                    year_of_study=form_data["year_of_study"],
                    admission_date=form_data["admission_date"],
                    db_name=app.config["DB_NAME"]
                )
                flash(f"Student '{form_data['full_name']}' was registered successfully (Student ID: #{new_id}).", "success")
                return redirect(url_for("student_list"))

        return render_template(
            "add_student.html",
            errors=errors,
            form_data=form_data,
            valid_years=VALID_YEARS,
            standard_courses=STANDARD_COURSES
        )

    @app.route("/students/<int:student_id>")
    def student_details(student_id):
        """View full profile details for a specific student."""
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            return render_template("student_details.html", student=None, student_id=student_id), 404

        return render_template("student_details.html", student=student, student_id=student_id)

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def edit_student_page(student_id):
        """Edit an existing student record."""
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            flash(f"Student #{student_id} does not exist.", "error")
            return redirect(url_for("student_list"))

        errors = {}
        form_data = dict(student)

        if request.method == "POST":
            form_data = {
                "id": student_id,
                "full_name": request.form.get("full_name", ""),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
                "course": request.form.get("course", ""),
                "year_of_study": request.form.get("year_of_study", ""),
                "admission_date": request.form.get("admission_date", "")
            }

            errors = validate_student_input(form_data, student_id=student_id, db_name=app.config["DB_NAME"])

            if not errors:
                database.update_student(
                    student_id=student_id,
                    full_name=form_data["full_name"],
                    email=form_data["email"],
                    phone=form_data["phone"],
                    course=form_data["course"],
                    year_of_study=form_data["year_of_study"],
                    admission_date=form_data["admission_date"],
                    db_name=app.config["DB_NAME"]
                )
                flash(f"Student #{student_id} ('{form_data['full_name']}') updated successfully.", "success")
                return redirect(url_for("student_list"))

        return render_template(
            "edit_student.html",
            student=student,
            errors=errors,
            form_data=form_data,
            valid_years=VALID_YEARS,
            standard_courses=STANDARD_COURSES
        )

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    def delete_student_action(student_id):
        """Delete a student record via HTML form submission."""
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            flash(f"Student #{student_id} was not found or has already been deleted.", "error")
            return redirect(url_for("student_list"))

        database.delete_student(student_id, db_name=app.config["DB_NAME"])
        flash(f"Student #{student_id} ('{student['full_name']}') has been deleted.", "success")
        return redirect(url_for("student_list"))

    @app.route("/about")
    def about():
        """About page describing project context, tech stack, and features."""
        return render_template("about.html")

    # -------------------------------------------------------------
    # REST API ENDPOINTS
    # -------------------------------------------------------------

    @app.route("/api/students", methods=["GET"])
    def api_get_students():
        """
        GET /api/students
        Retrieve all student records, with optional search and course query params.
        Status: 200 OK
        """
        search_query = request.args.get("search", "")
        course_filter = request.args.get("course", "")

        students = database.get_all_students(
            search=search_query,
            course=course_filter,
            db_name=app.config["DB_NAME"]
        )
        return jsonify(students), 200

    @app.route("/api/students/<int:student_id>", methods=["GET"])
    def api_get_student(student_id):
        """
        GET /api/students/<id>
        Retrieve a single student record.
        Status: 200 OK or 404 Not Found
        """
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found"}), 404

        return jsonify(student), 200

    @app.route("/api/students", methods=["POST"])
    def api_create_student():
        """
        POST /api/students
        Create a new student record from JSON.
        Status: 201 Created, 400 Bad Request, or 409 Conflict (Duplicate email)
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        errors = validate_student_input(data, db_name=app.config["DB_NAME"])
        if errors:
            # Check if error is due to duplicate email for 409 Conflict
            if "already exists" in errors.get("email", ""):
                return jsonify({"error": errors["email"], "validation_errors": errors}), 409
            return jsonify({"error": "Validation failed", "validation_errors": errors}), 400

        new_id = database.add_student(
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            course=data.get("course"),
            year_of_study=data.get("year_of_study"),
            admission_date=data.get("admission_date"),
            db_name=app.config["DB_NAME"]
        )

        new_student = database.get_student_by_id(new_id, db_name=app.config["DB_NAME"])
        return jsonify({
            "message": "Student created successfully",
            "student": new_student
        }), 201

    @app.route("/api/students/<int:student_id>", methods=["PUT"])
    def api_update_student(student_id):
        """
        PUT /api/students/<id>
        Update an existing student record from JSON.
        Status: 200 OK, 400 Bad Request, 404 Not Found, or 409 Conflict
        """
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found"}), 404

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        errors = validate_student_input(data, student_id=student_id, db_name=app.config["DB_NAME"])
        if errors:
            if "already exists" in errors.get("email", ""):
                return jsonify({"error": errors["email"], "validation_errors": errors}), 409
            return jsonify({"error": "Validation failed", "validation_errors": errors}), 400

        database.update_student(
            student_id=student_id,
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            course=data.get("course"),
            year_of_study=data.get("year_of_study"),
            admission_date=data.get("admission_date"),
            db_name=app.config["DB_NAME"]
        )

        updated_student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        return jsonify({
            "message": "Student updated successfully",
            "student": updated_student
        }), 200

    @app.route("/api/students/<int:student_id>", methods=["DELETE"])
    def api_delete_student(student_id):
        """
        DELETE /api/students/<id>
        Delete a student record.
        Status: 200 OK or 404 Not Found
        """
        student = database.get_student_by_id(student_id, db_name=app.config["DB_NAME"])
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found"}), 404

        database.delete_student(student_id, db_name=app.config["DB_NAME"])
        return jsonify({"message": f"Student with ID {student_id} deleted successfully"}), 200

    # 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("student_details.html", student=None, student_id=None), 404

    return app


app = create_app()

if __name__ == "__main__":
    print("Starting Student Record Management System on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
