"""
tests/test_app.py - Automated Unit and Integration Tests for Student Record Management System.

Tests cover:
- Application startup and route accessibility
- Adding a student via API and Web forms
- Retrieving all students and single student records
- Updating student information
- Deleting a student record
- Validation of invalid input (missing fields, malformed email, bad year)
- Duplicate email detection and rejection (409 Conflict)
- Handling of nonexistent student IDs (404 Not Found)

All tests execute against an isolated test database.
"""

import os
import sys
import tempfile
import unittest

# Ensure the parent directory is in sys.path so app and database can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
import database


class StudentRecordTestCase(unittest.TestCase):
    def setUp(self):
        """Set up an isolated temporary database for each test."""
        self.db_fd, self.test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)  # Close file descriptor so SQLite can open it

        self.app = create_app(db_name=self.test_db_path)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up and remove the temporary test database."""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

    def test_application_starts_correctly(self):
        """Verify the application starts and serves the home page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Record Management System", response.data)
        self.assertIn(b"Welcome to the Student Record Management System", response.data)

    def test_add_new_student_api(self):
        """Verify a new student can be added via the REST API (POST /api/students)."""
        payload = {
            "full_name": "Emma Watson",
            "email": "emma.watson@university.edu",
            "phone": "+1-555-123-4567",
            "course": "Computer Science",
            "year_of_study": "Year 2",
            "admission_date": "2024-09-01"
        }
        response = self.client.post("/api/students", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("student", data)
        self.assertEqual(data["student"]["full_name"], "Emma Watson")
        self.assertEqual(data["student"]["email"], "emma.watson@university.edu")
        self.assertIsNotNone(data["student"]["id"])

    def test_retrieve_all_students_api(self):
        """Verify all students can be retrieved via GET /api/students."""
        # Add two students
        self.client.post("/api/students", json={
            "full_name": "Student One",
            "email": "one@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        })
        self.client.post("/api/students", json={
            "full_name": "Student Two",
            "email": "two@university.edu",
            "course": "Information Technology",
            "year_of_study": "Year 3",
            "admission_date": "2022-09-01"
        })

        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_retrieve_single_student_api(self):
        """Verify a single student can be retrieved via GET /api/students/<id>."""
        create_res = self.client.post("/api/students", json={
            "full_name": "David Miller",
            "email": "david.miller@university.edu",
            "course": "Mechanical Engineering",
            "year_of_study": "Year 4",
            "admission_date": "2021-09-01"
        })
        student_id = create_res.get_json()["student"]["id"]

        response = self.client.get(f"/api/students/{student_id}")
        self.assertEqual(response.status_code, 200)
        student = response.get_json()
        self.assertEqual(student["id"], student_id)
        self.assertEqual(student["full_name"], "David Miller")
        self.assertEqual(student["course"], "Mechanical Engineering")

    def test_update_student_api(self):
        """Verify student information can be updated via PUT /api/students/<id>."""
        create_res = self.client.post("/api/students", json={
            "full_name": "Sarah Connor",
            "email": "sarah.connor@university.edu",
            "course": "Civil Engineering",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        })
        student_id = create_res.get_json()["student"]["id"]

        update_payload = {
            "full_name": "Sarah Connor-Smith",
            "email": "sarah.smith@university.edu",
            "phone": "+1-555-987-6543",
            "course": "Civil Engineering",
            "year_of_study": "Year 2",
            "admission_date": "2024-09-01"
        }
        update_res = self.client.put(f"/api/students/{student_id}", json=update_payload)
        self.assertEqual(update_res.status_code, 200)
        updated_data = update_res.get_json()["student"]
        self.assertEqual(updated_data["full_name"], "Sarah Connor-Smith")
        self.assertEqual(updated_data["email"], "sarah.smith@university.edu")
        self.assertEqual(updated_data["year_of_study"], "Year 2")

    def test_delete_student_api(self):
        """Verify a student can be deleted via DELETE /api/students/<id>."""
        create_res = self.client.post("/api/students", json={
            "full_name": "Lucas Grey",
            "email": "lucas.grey@university.edu",
            "course": "Electrical Engineering",
            "year_of_study": "Year 2",
            "admission_date": "2023-09-01"
        })
        student_id = create_res.get_json()["student"]["id"]

        # Delete student
        delete_res = self.client.delete(f"/api/students/{student_id}")
        self.assertEqual(delete_res.status_code, 200)

        # Confirm student is no longer retrievable
        get_res = self.client.get(f"/api/students/{student_id}")
        self.assertEqual(get_res.status_code, 404)

    def test_invalid_input_rejected(self):
        """Verify invalid input is rejected with HTTP 400 Bad Request."""
        # Missing full_name
        res1 = self.client.post("/api/students", json={
            "full_name": "",
            "email": "test@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        })
        self.assertEqual(res1.status_code, 400)
        self.assertIn("Full name is required", res1.get_json()["validation_errors"]["full_name"])

        # Invalid email format
        res2 = self.client.post("/api/students", json={
            "full_name": "Valid Name",
            "email": "invalid-email-string",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        })
        self.assertEqual(res2.status_code, 400)
        self.assertIn("valid email address", res2.get_json()["validation_errors"]["email"])

        # Invalid year of study
        res3 = self.client.post("/api/students", json={
            "full_name": "Valid Name",
            "email": "valid@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 10",
            "admission_date": "2024-09-01"
        })
        self.assertEqual(res3.status_code, 400)
        self.assertIn("Year of study must be one of", res3.get_json()["validation_errors"]["year_of_study"])

        # Invalid date format
        res4 = self.client.post("/api/students", json={
            "full_name": "Valid Name",
            "email": "valid@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "not-a-date"
        })
        self.assertEqual(res4.status_code, 400)
        self.assertIn("YYYY-MM-DD", res4.get_json()["validation_errors"]["admission_date"])

    def test_duplicate_email_rejected(self):
        """Verify duplicate email addresses are rejected with HTTP 409 Conflict."""
        first_payload = {
            "full_name": "Alice Smith",
            "email": "duplicate@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        }
        res1 = self.client.post("/api/students", json=first_payload)
        self.assertEqual(res1.status_code, 201)

        second_payload = {
            "full_name": "Bob Smith",
            "email": "duplicate@university.edu",
            "course": "Business Administration",
            "year_of_study": "Year 2",
            "admission_date": "2023-09-01"
        }
        res2 = self.client.post("/api/students", json=second_payload)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("already exists", res2.get_json()["error"])

    def test_nonexistent_student_returns_404(self):
        """Verify requesting a nonexistent student returns HTTP 404 Not Found."""
        res_get = self.client.get("/api/students/99999")
        self.assertEqual(res_get.status_code, 404)

        res_put = self.client.put("/api/students/99999", json={
            "full_name": "Ghost Student",
            "email": "ghost@university.edu",
            "course": "Computer Science",
            "year_of_study": "Year 1",
            "admission_date": "2024-09-01"
        })
        self.assertEqual(res_put.status_code, 404)

        res_delete = self.client.delete("/api/students/99999")
        self.assertEqual(res_delete.status_code, 404)

    def test_web_flow_add_view_edit_delete(self):
        """Verify the full web HTML user flow: register, list, details, edit, delete."""
        # 1. Add student via web form POST
        post_response = self.client.post("/students/add", data={
            "full_name": "Jane Doe",
            "email": "jane.doe@university.edu",
            "phone": "555-0100",
            "course": "Business Administration",
            "year_of_study": "Year 3",
            "admission_date": "2023-08-15"
        }, follow_redirects=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertIn(b"Jane Doe", post_response.data)
        self.assertIn(b"registered successfully", post_response.data)

        # 2. View details page
        details_response = self.client.get("/students/1")
        self.assertEqual(details_response.status_code, 200)
        self.assertIn(b"Jane Doe", details_response.data)
        self.assertIn(b"Business Administration", details_response.data)

        # 3. Nonexistent details page returns 404
        missing_details = self.client.get("/students/8888")
        self.assertEqual(missing_details.status_code, 404)
        self.assertIn(b"Student Not Found", missing_details.data)

        # 4. Edit student via web form
        edit_response = self.client.post("/students/1/edit", data={
            "full_name": "Jane Doe Updated",
            "email": "jane.doe@university.edu",
            "phone": "555-0199",
            "course": "Business Administration",
            "year_of_study": "Year 4",
            "admission_date": "2023-08-15"
        }, follow_redirects=True)
        self.assertEqual(edit_response.status_code, 200)
        self.assertIn(b"Jane Doe Updated", edit_response.data)

        # 5. Delete student via web action
        delete_response = self.client.post("/students/1/delete", follow_redirects=True)
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn(b"has been deleted", delete_response.data)


if __name__ == "__main__":
    unittest.main()
