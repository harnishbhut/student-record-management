# Student Record Management System

A clean, traditional academic web application built with **Python**, **Flask**, **SQLite**, and vanilla **HTML, CSS, and JavaScript**. Designed for college administrators and teachers to register students, view records, search/filter admissions, update academic details, and manage student information.

This project is tailored for a beginner-level Software Development Intern portfolio, adhering to clean architecture, parameterized SQL queries, RESTful API design, and comprehensive automated testing.

---

## 1. Project Overview & Features

- **Academic Web Interface:** Clean, traditional academic aesthetic with white background, navy headers, comfortable typography, and rectangular buttons without distracting gradients or dashboard widgets.
- **Home Page:** Purpose overview, quick-action navigation, and feature walkthrough.
- **Student Records Directory:** Full tabular display of registered students with unique Student ID, Full Name, Email, Course, Year of Study, and Action buttons.
- **Dynamic Search & Filtering:** Filter students by course and search by name or ID simultaneously (with JavaScript `fetch()` live updates and standard fallback).
- **Add Student Registration:** Intuitive enrollment form with client-side and server-side validation, duplicate email detection, and automatic ID assignment.
- **Student Profile View:** Detailed profile view showing full student record and admission date.
- **Edit Student Details:** Edit existing student details with pre-populated fields while keeping the student ID protected and read-only.
- **Delete Student Records:** Destructive action protected by JavaScript confirmation dialogs with flash feedback.
- **RESTful API:** JSON-based API covering full CRUD operations with standard HTTP status codes (`200`, `201`, `400`, `404`, `409`).
- **Automated Testing:** Comprehensive test suite written with Python's built-in `unittest` using isolated test databases.

---

## 2. Technology Stack

- **Backend:** Python 3 (Flask framework)
- **Database:** SQLite3 (native lightweight relational database)
- **Frontend:** Semantic HTML5, Vanilla CSS3 (academic theme), Vanilla JavaScript (ES6)
- **Testing:** Python `unittest` framework
- **Version Control:** Git

No complex or heavy dependencies (no React, Angular, Bootstrap, Tailwind, or external UI libraries).

---

## 3. Project Directory Structure

```text
student-record-management/
│
├── app.py                   # Main Flask application with Web & REST API routes
├── database.py              # SQLite database initialization & CRUD helper functions
├── requirements.txt         # Project dependencies (Flask)
├── students.db              # SQLite database file (created automatically)
├── .gitignore               # Ignored files (virtual environment, cache, DB)
├── README.md                # Project documentation and guide
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Shared layout with navigation and footer
│   ├── index.html           # Home / Welcome page
│   ├── students.html        # Student records table with search & filter
│   ├── add_student.html     # Registration form for new students
│   ├── edit_student.html    # Form to update existing student records
│   ├── student_details.html # Detailed view of individual student record
│   └── about.html           # Project background and technical summary
│
├── static/                  # Static assets
│   ├── style.css            # Clean academic stylesheet
│   └── script.js            # Delete confirmation, validation & fetch() API demo
│
└── tests/                   # Automated test suite
    └── test_app.py          # 10 automated unit & integration tests
```

---

## 4. SQLite Database Schema

The database table `students` is defined with the following fields:

| Field Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique auto-generated Student ID |
| `full_name` | TEXT | NOT NULL | Student's full name |
| `email` | TEXT | UNIQUE NOT NULL | Unique student email address |
| `phone` | TEXT | NULLABLE | Optional phone contact number |
| `course` | TEXT | NOT NULL | Academic major / course name |
| `year_of_study` | TEXT | NOT NULL | Academic year (Year 1, 2, 3, or 4) |
| `admission_date`| TEXT | NOT NULL | Date of admission (YYYY-MM-DD) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when record was created |

All database queries utilize **parameterized SQL statements** (`?` placeholders) to prevent SQL injection vulnerabilities.

---

## 5. REST API Specification

The application provides a clean JSON REST API:

| Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| `GET` | `/api/students` | Retrieve all students (supports `?search=` and `?course=`) | `200 OK` |
| `GET` | `/api/students/<id>` | Retrieve single student by ID | `200 OK`, `404 Not Found` |
| `POST` | `/api/students` | Create a new student record | `201 Created`, `400 Bad Request`, `409 Conflict` |
| `PUT` | `/api/students/<id>` | Update an existing student | `200 OK`, `400 Bad Request`, `404 Not Found`, `409 Conflict` |
| `DELETE` | `/api/students/<id>` | Delete a student by ID | `200 OK`, `404 Not Found` |

### HTTP Status Codes Explained

- **`200 OK`**: The request was successful (retrieval, update, or deletion).
- **`201 Created`**: The resource was successfully created in the database.
- **`400 Bad Request`**: Validation failed (missing required field, invalid email format, or invalid year of study).
- **`404 Not Found`**: The requested student ID does not exist in the database.
- **`409 Conflict`**: An attempt was made to register or update with an email address already assigned to another student.

---

## 6. Windows Installation & Execution Guide

Follow these exact steps to run the application on Windows:

### Step 1: Open the Project Folder in PowerShell
```powershell
cd C:\Users\harni\.gemini\antigravity\scratch\student-record-management
```

### Step 2: Create a Python Virtual Environment
```powershell
python -m venv .venv
```
*(If `python` is not in your path, use the full path to your Python 3 executable or `py -m venv .venv`)*

### Step 3: Activate the Environment in PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
```
*Note: If PowerShell displays an execution policy restriction, enable script execution for the current user:*
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize and Seed the Database
Run `database.py` directly to create `students.db` and seed it with starter records:
```powershell
python database.py
```

### Step 6: Start the Flask Application
```powershell
python app.py
```

### Step 7: Open the Website in a Web Browser
Open your browser (Edge, Chrome, or Firefox) and navigate to:
```text
http://127.0.0.1:5000
```

### Step 8: Run Automated Tests
Open a terminal in the project directory and run:
```powershell
python -m unittest discover -s tests -v
```
All 10 tests will execute against an isolated temporary database and pass with `OK`.

### Step 9: Test the REST API using PowerShell / curl

**Retrieve all students:**
```powershell
curl http://127.0.0.1:5000/api/students
```

**Retrieve a specific student (ID #1):**
```powershell
curl http://127.0.0.1:5000/api/students/1
```

**Create a new student via POST:**
```powershell
curl -X POST http://127.0.0.1:5000/api/students `
  -H "Content-Type: application/json" `
  -d "{\"full_name\": \"David Miller\", \"email\": \"david.miller@college.edu\", \"phone\": \"555-0199\", \"course\": \"Computer Science\", \"year_of_study\": \"Year 1\", \"admission_date\": \"2024-09-01\"}"
```

**Update a student via PUT:**
```powershell
curl -X PUT http://127.0.0.1:5000/api/students/1 `
  -H "Content-Type: application/json" `
  -d "{\"full_name\": \"Eleanor Vance Updated\", \"email\": \"eleanor.vance@college.edu\", \"phone\": \"555-0142\", \"course\": \"Computer Science\", \"year_of_study\": \"Year 3\", \"admission_date\": \"2024-09-01\"}"
```

**Delete a student via DELETE:**
```powershell
curl -X DELETE http://127.0.0.1:5000/api/students/1
```

### Step 10: Initialize Git and Make the First Commit
```powershell
git init
git add .
git commit -m "Initial commit: Student Record Management System with Flask and SQLite"
```

---

## 7. Beginner-Friendly Explanation of Core Concepts

### What is Flask?
**Flask** is a micro web framework written in Python. It acts as the web server and "traffic director" for your application. When someone visits a URL like `http://127.0.0.1:5000/students` in their browser, Flask receives that HTTP request, executes the corresponding Python function (called a route handler), and returns an HTML page or JSON data.

### What Does Each File Do?
- `app.py`: The control center of your application. It maps URLs to Python functions, validates user inputs, and coordinates between the database and the templates.
- `database.py`: The database manager. It handles establishing the SQLite connection and running queries like `INSERT`, `SELECT`, `UPDATE`, and `DELETE`.
- `requirements.txt`: A plain text file listing external Python packages your application needs (in this case, `Flask`).
- `templates/*.html`: HTML templates using the Jinja2 templating engine. They allow Python variables (such as student records) to be seamlessly inserted into HTML before sending it to the user's browser.
- `static/style.css`: Controls the visual presentation (colors, borders, typography, layout) without touching the logic.
- `static/script.js`: Runs inside the user's browser to handle interactions like delete confirmation alerts and live REST API requests.
- `tests/test_app.py`: Automated code checks that prove your application works correctly without having to click around manually every time.

### What is a REST API and CRUD?
- **CRUD** stands for the four basic operations on any data storage system:
  - **C**reate: Adding new student records.
  - **R**ead: Viewing a list of students or an individual student's details.
  - **U**pdate: Modifying details of an existing student.
  - **D**elete: Removing a student record from the database.
- A **REST API** (Representational State Transfer Application Programming Interface) allows programs to exchange structured data over HTTP using standard JSON (JavaScript Object Notation), rather than full visual HTML pages.

### Differences Between HTTP Methods (GET, POST, PUT, DELETE)
- **`GET`**: Used only to retrieve data from the server. It does not alter server state (e.g., getting the list of students).
- **`POST`**: Used to submit new data to the server to create a new resource (e.g., registering a new student).
- **`PUT`**: Used to replace or update an existing resource completely with new data (e.g., saving updated student information).
- **`DELETE`**: Used to permanently remove a specified resource (e.g., deleting student record #3).

### What is a Database Table and Primary Key?
- A **database table** is like a spreadsheet organized into named columns (fields) and rows (individual student records).
- A **primary key** (`id` in our table) is a unique identifier assigned to every single row. No two students can ever have the same ID. SQLite automatically increments this ID (`1`, `2`, `3`, ...) so every student has a permanent, unchangeable identifier.

### How Python Stores and Retrieves Information using SQLite
Python has a built-in module called `sqlite3`. When you add a student:
1. Python opens a connection to `students.db`.
2. It sends an SQL query with values placed into placeholders (`?`).
3. SQLite parses the query, writes the data safely to disk, and commits the transaction.
4. Python fetches results back using `cursor.fetchall()`, which turns each row into an easy-to-use dictionary.

### How HTML and CSS Create the Website
- **HTML** (HyperText Markup Language) provides the skeleton and semantic structure (headings `<h2>`, tables `<table>`, forms `<form>`, buttons `<button>`).
- **CSS** (Cascading Style Sheets) defines the styling: borders, margins, fonts, and dark blue academic color scheme.

### How JavaScript Communicates with the Backend
JavaScript running in the browser can communicate in the background with Flask using the built-in `fetch()` API. When you type in the search box on the Student Records page, `script.js` sends an asynchronous GET request to `/api/students?search=...`. Flask responds with JSON data, and JavaScript updates the table rows without refreshing the entire webpage.

### How Input Validation and Error Handling Work
- **Client-Side Validation (JavaScript):** Checks that fields are not empty and emails have an `@` symbol immediately when the user clicks Submit, preventing needless network requests.
- **Server-Side Validation (Python):** Never trusts client input alone. Python rigorously verifies that the name is at least 2 characters, the email is valid and not already in use by another student, the year of study matches an approved year, and the admission date is a valid calendar date. If any check fails, helpful error messages are returned.

### How Automated Tests Work
Automated tests in `tests/test_app.py` act as a safety net. Each test runs a specific scenario (e.g., "try adding a student with an invalid email"). The test checks if Flask properly returns HTTP 400 Bad Request. By running tests before deploying, you guarantee that fixing one bug didn't break another part of the system.

### How Git Helps Manage Source Code
**Git** is a distributed version control system. It acts as a time machine for your codebase. Every commit takes a snapshot of your project. If you make a mistake or break a feature, you can view diffs or roll back to an earlier working snapshot.

---

## 8. Complete Step-by-Step Flow: Adding a Student

Here is the exact journey of adding a student:

```text
[User Browser]
      │
      ├─ 1. User fills out Form (Full Name, Email, Course, Year, Date)
      ├─ 2. User clicks "Save Student Record"
      │
[Client-side JavaScript (script.js)]
      │
      ├─ 3. validateStudentForm() checks fields in browser
      │
[HTTP POST Request to /students/add]
      │
[Flask Controller (app.py)]
      │
      ├─ 4. validate_student_input() validates data on server
      ├─ 5. database.get_student_by_email() ensures email is not taken
      │
[Database Layer (database.py)]
      │
      ├─ 6. Executes: INSERT INTO students (...) VALUES (?, ?, ?, ...)
      ├─ 7. SQLite generates unique ID (e.g., #5) and writes to students.db
      │
[Flask Controller (app.py)]
      │
      ├─ 8. flash("Student registered successfully...")
      ├─ 9. HTTP 302 Redirect to /students
      │
[User Browser]
      │
      └─ 10. Loads /students, displaying success alert and new record in table!
```
