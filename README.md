# CourseCloud – Cloud-Based Online Course Registration System

A functional mini-project prototype built with **Python, Streamlit and SQLite**. It demonstrates the core workflow of browsing courses, searching/filtering, registering students, validating seat availability, and reviewing enrollment reports.

## Features
- Course catalog with title, code, category, instructor, duration, level and seat count.
- Search by course title, code or instructor.
- Category and availability filters.
- Student registration form with input validation.
- Prevents duplicate registrations and over-capacity enrollment.
- Dashboard charts for course and department enrollment.
- Course capacity report and recent registration table.
- Downloadable CSV registration report.
- Admin demo area to add courses.
- Sample courses and registrations are seeded automatically on first launch.

## Tech stack
- Python 3.11+
- Streamlit
- SQLite
- Pandas
- Matplotlib (available for extensions)

## Run locally
```bash
# 1. Extract the ZIP and open the project folder
cd cloud_course_registration

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```
Open the local URL shown by Streamlit (normally http://localhost:8501).

## Sample login / test data
There is no login in this academic prototype. Sample students are preloaded:
- STU1001 – Aarav Sharma – aarav@example.com
- STU1002 – Diya Reddy – diya@example.com
- STU1003 – Ishaan Kumar – ishaan@example.com
- STU1004 – Ananya Patel – ananya@example.com

Try registering a new ID such as `STU1020` with a valid email. A sample student ID cannot register twice for the same course.

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository, e.g. `cloud-based-course-registration`.
2. Extract this ZIP and upload/push all project files to the repository root.
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**, choose your repository and branch, and set the main file path to `app.py`.
5. Deploy. Streamlit installs dependencies from `requirements.txt`.

### Important cloud storage note
This prototype uses a local SQLite database at `data/courses.db`. It is suitable for a classroom demonstration, but the writable filesystem on hosted app services may be ephemeral and is not a reliable shared database for production. For a real multi-user cloud deployment, replace SQLite with a managed database such as PostgreSQL/Supabase and add authentication, authorization, backups and privacy controls. Do not use real student personal data in this prototype.

## Project structure
```
cloud_course_registration/
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .gitignore
├── data/
│   └── README.md
├── screenshots/
│   ├── dashboard_preview.png
│   └── catalog_preview.png
├── tests/
│   ├── test_cases.md
│   └── test_registration.py
└── demo/
    └── live_demo_script.md
```

## Functional workflow
1. Student opens the course catalog.
2. Student searches or filters courses.
3. Student selects a course with available seats.
4. Student enters student details and submits registration.
5. System validates required fields, email format, duplicate enrollment and capacity.
6. System saves registration and updates the course seat count.
7. Dashboard refreshes and displays the new enrollment.
8. Admin downloads the CSV report.

## Screenshots
The `screenshots/` folder contains illustrative UI preview images for the project report. Capture fresh screenshots from the running app for your final submission if your faculty requires actual runtime evidence.
