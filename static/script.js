/**
 * script.js - Client-side JavaScript for Student Record Management System.
 * Demonstrates:
 * 1. User confirmation dialogs for destructive actions (Delete).
 * 2. Asynchronous API communication using JavaScript fetch().
 * 3. Client-side form validation.
 */

// Function to confirm student deletion
function confirmDelete(studentName, studentId) {
    const message = `Are you sure you want to delete student record #${studentId} (${studentName})?\nThis action cannot be undone.`;
    return confirm(message);
}

// Client-side form validation for Add and Edit student forms
function validateStudentForm(formElement) {
    let isValid = true;

    const fullNameInput = formElement.querySelector("#full_name");
    const emailInput = formElement.querySelector("#email");
    const courseInput = formElement.querySelector("#course");
    const yearInput = formElement.querySelector("#year_of_study");
    const dateInput = formElement.querySelector("#admission_date");

    // Clear previous inline errors
    formElement.querySelectorAll(".field-error.client-error").forEach(el => el.remove());

    function showError(inputElement, errorText) {
        isValid = false;
        const errorDiv = document.createElement("div");
        errorDiv.className = "field-error client-error";
        errorDiv.innerText = errorText;
        inputElement.parentNode.appendChild(errorDiv);
        inputElement.focus();
    }

    // Full name validation
    if (fullNameInput && fullNameInput.value.trim().length < 2) {
        showError(fullNameInput, "Full name must be at least 2 characters.");
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailInput && !emailRegex.test(emailInput.value.trim())) {
        showError(emailInput, "Please enter a valid email address (e.g., student@example.edu).");
    }

    // Course validation
    if (courseInput && courseInput.value.trim() === "") {
        showError(courseInput, "Please select or enter a course name.");
    }

    // Year of study validation
    if (yearInput && yearInput.value.trim() === "") {
        showError(yearInput, "Please select a year of study.");
    }

    // Admission date validation
    if (dateInput && dateInput.value.trim() === "") {
        showError(dateInput, "Please select a valid admission date.");
    }

    return isValid;
}

/**
 * Demonstrate asynchronous communication with the REST API using JavaScript fetch().
 * Queries GET /api/students with the user's search and course filter parameters
 * and dynamically renders the results in the table.
 */
function fetchStudentsLive() {
    const searchInput = document.getElementById("search-input");
    const courseSelect = document.getElementById("course-filter");
    const tableBody = document.getElementById("students-table-body");
    const emptyState = document.getElementById("empty-state");
    const resultCount = document.getElementById("result-count");

    if (!tableBody) return;

    const query = searchInput ? encodeURIComponent(searchInput.value.trim()) : "";
    const course = courseSelect ? encodeURIComponent(courseSelect.value.trim()) : "";

    const url = `/api/students?search=${query}&course=${course}`;

    // Perform REST API GET request
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            return response.json();
        })
        .then(students => {
            // Clear current table rows
            tableBody.innerHTML = "";

            if (resultCount) {
                resultCount.textContent = `Showing ${students.length} student record(s)`;
            }

            if (students.length === 0) {
                if (emptyState) emptyState.style.display = "block";
            } else {
                if (emptyState) emptyState.style.display = "none";

                students.forEach(student => {
                    const tr = document.createElement("tr");

                    // Escape HTML to prevent XSS
                    const escapeHtml = str => String(str || "").replace(/[&<>'"]/g, 
                        tag => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[tag] || tag)
                    );

                    tr.innerHTML = `
                        <td><strong>#${student.id}</strong></td>
                        <td>${escapeHtml(student.full_name)}</td>
                        <td>${escapeHtml(student.email)}</td>
                        <td>${escapeHtml(student.course)}</td>
                        <td>${escapeHtml(student.year_of_study)}</td>
                        <td class="actions-cell">
                            <a href="/students/${student.id}" class="btn btn-secondary btn-sm">View</a>
                            <a href="/students/${student.id}/edit" class="btn btn-primary btn-sm">Edit</a>
                            <form action="/students/${student.id}/delete" method="POST" style="display:inline;" onsubmit="return confirmDelete('${escapeHtml(student.full_name)}', '${student.id}');">
                                <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                            </form>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            }
        })
        .catch(err => {
            console.error("Failed to fetch students from REST API:", err);
        });
}

// Attach live search event listeners once DOM is ready
document.addEventListener("DOMContentLoaded", function () {
    const liveSearchInput = document.getElementById("search-input");
    const liveCourseSelect = document.getElementById("course-filter");

    if (liveSearchInput && liveCourseSelect) {
        // Debounce search input to avoid excessive API requests
        let debounceTimer;
        liveSearchInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchStudentsLive, 250);
        });

        liveCourseSelect.addEventListener("change", function () {
            fetchStudentsLive();
        });
    }

    // Attach form validation handler to student forms
    const studentForm = document.getElementById("student-form");
    if (studentForm) {
        studentForm.addEventListener("submit", function (event) {
            if (!validateStudentForm(studentForm)) {
                event.preventDefault();
            }
        });
    }
});
