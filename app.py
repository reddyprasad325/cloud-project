import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="CourseCloud | Registration", page_icon="🎓", layout="wide")
DB_PATH = Path(__file__).parent / "data" / "courses.db"

COURSES = [
    ("CS101","Python Programming","Programming","Dr. Ananya Rao",8,30,6,"Beginner"),
    ("CS102","Web Development with React","Web Development","Mr. Kiran Kumar",10,25,4,"Intermediate"),
    ("DS201","Data Science Foundations","Data Science","Dr. Meera Nair",12,30,8,"Beginner"),
    ("DS202","Machine Learning Essentials","Data Science","Dr. Rahul Verma",10,20,3,"Intermediate"),
    ("CL301","Cloud Computing Fundamentals","Cloud Computing","Ms. Priya Sharma",8,25,5,"Beginner"),
    ("CY401","Cybersecurity Basics","Cybersecurity","Mr. Arjun Reddy",6,20,2,"Beginner"),
    ("DB210","Database Management Systems","Database","Dr. Neha Singh",8,30,10,"Intermediate"),
    ("UI110","UI/UX Design Principles","Design","Ms. Kavya Iyer",6,18,7,"Beginner"),
]

def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS courses(
            code TEXT PRIMARY KEY, title TEXT, category TEXT, instructor TEXT,
            duration INTEGER, capacity INTEGER, enrolled INTEGER DEFAULT 0, level TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS students(
            student_id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, department TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS registrations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, course_code TEXT,
            registered_at TEXT, UNIQUE(student_id, course_code),
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_code) REFERENCES courses(code))""")
        count=con.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if count == 0:
            con.executemany("INSERT INTO courses VALUES(?,?,?,?,?,?,?,?)", COURSES)
            sample_students=[
                ("STU1001","Aarav Sharma","aarav@example.com","CSE"),
                ("STU1002","Diya Reddy","diya@example.com","Data Science"),
                ("STU1003","Ishaan Kumar","ishaan@example.com","ECE"),
                ("STU1004","Ananya Patel","ananya@example.com","CSE"),
            ]
            con.executemany("INSERT OR IGNORE INTO students VALUES(?,?,?,?)",sample_students)
            seed=[
                ("STU1001","CS101"),("STU1001","DS201"),("STU1002","DS202"),
                ("STU1003","CL301"),("STU1004","UI110"),("STU1002","DB210")
            ]
            for sid,code in seed:
                try:
                    con.execute("INSERT INTO registrations(student_id,course_code,registered_at) VALUES(?,?,?)",
                                (sid,code,datetime.now().isoformat(timespec="seconds")))
                    con.execute("UPDATE courses SET enrolled=enrolled+1 WHERE code=?",(code,))
                except sqlite3.IntegrityError: pass

init_db()

def read_df(query, params=()):
    with connect() as con: return pd.read_sql_query(query,con,params=params)

def register_student(sid,name,email,dept,code):
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO students(student_id,name,email,department) VALUES(?,?,?,?)",(sid,name,email,dept))
        student=con.execute("SELECT student_id FROM students WHERE student_id=? AND email=?",(sid,email)).fetchone()
        if not student:
            raise ValueError("Student ID is already linked to a different email address.")
        course=con.execute("SELECT capacity,enrolled,title FROM courses WHERE code=?",(code,)).fetchone()
        if not course: raise ValueError("Selected course was not found.")
        if con.execute("SELECT 1 FROM registrations WHERE student_id=? AND course_code=?",(sid,code)).fetchone():
            raise ValueError("You are already registered for this course.")
        if course[1] >= course[0]: raise ValueError("Sorry, this course is full.")
        con.execute("INSERT INTO registrations(student_id,course_code,registered_at) VALUES(?,?,?)",
                    (sid,code,datetime.now().isoformat(timespec="seconds")))
        con.execute("UPDATE courses SET enrolled=enrolled+1 WHERE code=?",(code,))
        return course[2]

st.markdown("""
<style>
.stApp{background:#f5f7fb;color:#17233c}
.block-container{padding-top:1.7rem;max-width:1400px}
.hero{background:linear-gradient(115deg,#12264a,#2857a4);padding:28px 32px;border-radius:18px;color:white;margin-bottom:18px}
.hero h1{color:white;font-size:2.15rem;margin:0}.hero p{color:#dce8ff;margin:8px 0 0}
.metric{background:white;border:1px solid #e7ebf2;border-radius:14px;padding:17px 18px}
.metric small{color:#68758d}.metric h2{margin:4px 0 0;color:#1c3766}
.course{background:white;border:1px solid #e7ebf2;border-radius:14px;padding:16px;margin-bottom:10px}
.tag{display:inline-block;background:#eaf0ff;color:#2857a4;padding:4px 9px;border-radius:20px;font-size:12px}
</style>
""",unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>CourseCloud</h1><p>Discover courses. Build skills. Register in seconds.</p></div>',unsafe_allow_html=True)
courses=read_df("SELECT * FROM courses")
regs=read_df("""SELECT r.id,s.student_id,s.name,s.email,s.department,c.code AS course_code,
                c.title AS course_title,r.registered_at
                FROM registrations r JOIN students s ON r.student_id=s.student_id
                JOIN courses c ON r.course_code=c.code ORDER BY r.registered_at DESC""")
students=read_df("SELECT * FROM students")

m1,m2,m3,m4=st.columns(4)
for col,label,val in [(m1,"Available courses",len(courses)),(m2,"Registered students",len(students)),
                      (m3,"Total enrollments",len(regs)),(m4,"Seats remaining",int((courses.capacity-courses.enrolled).clip(lower=0).sum()))]:
    col.markdown(f'<div class="metric"><small>{label}</small><h2>{val:,}</h2></div>',unsafe_allow_html=True)

tab1,tab2,tab3=st.tabs(["📚 Browse & Register","📊 Dashboard & Reports","🛠️ Admin / Course Management"])

with tab1:
    st.subheader("Find your next course")
    f1,f2,f3=st.columns([2,1,1])
    search=f1.text_input("Search by course title, code or instructor",placeholder="e.g. Python, CS101...")
    categories=["All"]+sorted(courses.category.unique().tolist())
    category=f2.selectbox("Category",categories)
    availability=f3.selectbox("Availability",["All courses","Seats available","Full courses"])
    filtered=courses.copy()
    if search:
        mask=filtered.astype(str).apply(lambda x:x.str.contains(search,case=False,na=False)).any(axis=1)
        filtered=filtered[mask]
    if category!="All": filtered=filtered[filtered.category==category]
    if availability=="Seats available": filtered=filtered[filtered.enrolled<filtered.capacity]
    if availability=="Full courses": filtered=filtered[filtered.enrolled>=filtered.capacity]
    st.caption(f"Showing {len(filtered)} course(s)")
    for _,c in filtered.iterrows():
        remaining=max(int(c.capacity-c.enrolled),0)
        with st.container():
            st.markdown(f"""<div class="course"><span class="tag">{c.category}</span>
            <h4 style="margin:9px 0 2px">{c.title} <span style="color:#8190a8;font-size:13px">({c.code})</span></h4>
            <span style="color:#68758d">Instructor: {c.instructor} · {c.duration} weeks · {c.level}</span>
            <p style="margin:8px 0 0;color:#2857a4"><b>{remaining}</b> seats remaining of {c.capacity}</p></div>""",unsafe_allow_html=True)
    if filtered.empty: st.info("No courses match your search. Try another keyword or category.")
    st.divider()
    st.subheader("Student course registration")
    st.write("Enter your details and select an available course to complete registration.")
    available=courses[courses.enrolled<courses.capacity]
    if available.empty:
        st.warning("All courses are currently full.")
    else:
        with st.form("registration_form",clear_on_submit=True):
            a,b=st.columns(2)
            sid=a.text_input("Student ID",placeholder="e.g. STU1020")
            name=b.text_input("Full name")
            email=a.text_input("Email address")
            dept=b.selectbox("Department",["CSE","Data Science","ECE","EEE","IT","Mechanical","Civil","Other"])
            course_options={f"{r.code} — {r.title} ({int(r.capacity-r.enrolled)} seats left)":r.code for _,r in available.iterrows()}
            selected=st.selectbox("Choose course",list(course_options.keys()))
            submitted=st.form_submit_button("Register for course",type="primary",use_container_width=True)
            if submitted:
                if not all([sid.strip(),name.strip(),email.strip(),selected]):
                    st.error("Please complete all fields.")
                elif "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Please enter a valid email address.")
                else:
                    try:
                        title=register_student(sid.strip().upper(),name.strip(),email.strip().lower(),dept,course_options[selected])
                        st.success(f"Registration successful! {name.strip()} is enrolled in {title}.")
                        st.balloons()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("This email address is already registered with another student ID.")
                    except ValueError as e: st.error(str(e))

with tab2:
    st.subheader("Registration overview")
    if regs.empty: st.info("No registrations yet.")
    else:
        c1,c2=st.columns(2)
        by_course=regs.groupby("course_title").size().sort_values(ascending=False).reset_index(name="registrations")
        c1.markdown("**Enrollments by course**")
        c1.bar_chart(by_course.set_index("course_title"))
        by_dept=regs.groupby("department").size().reset_index(name="registrations")
        c2.markdown("**Registrations by department**")
        c2.bar_chart(by_dept.set_index("department"))
    st.markdown("**Course capacity report**")
    report=courses[["code","title","category","capacity","enrolled"]].copy()
    report["seats_remaining"]=(report.capacity-report.enrolled).clip(lower=0)
    report["occupancy_%"]=(report.enrolled/report.capacity*100).round(1)
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.markdown("**Recent registrations**")
    st.dataframe(regs,use_container_width=True,hide_index=True)
    st.download_button("⬇ Download registration report (CSV)",regs.to_csv(index=False).encode("utf-8"),
                       file_name="course_registrations_report.csv",mime="text/csv",use_container_width=True)

with tab3:
    st.subheader("Course management")
    st.caption("Admin view for monitoring course capacity and enrollment.")
    st.dataframe(courses[["code","title","category","instructor","duration","level","capacity","enrolled"]],use_container_width=True,hide_index=True)
    with st.expander("Add a new course"):
        with st.form("add_course"):
            x1,x2=st.columns(2)
            code=x1.text_input("Course code").strip().upper()
            title=x2.text_input("Course title")
            cat=x1.selectbox("Category",["Programming","Web Development","Data Science","Cloud Computing","Cybersecurity","Database","Design","Other"])
            instructor=x2.text_input("Instructor")
            dur=x1.number_input("Duration (weeks)",min_value=1,max_value=52,value=8)
            capacity=x2.number_input("Seat capacity",min_value=1,max_value=500,value=25)
            level=st.selectbox("Difficulty level",["Beginner","Intermediate","Advanced"])
            add=st.form_submit_button("Add course",type="primary")
            if add:
                if not all([code,title,instructor]): st.error("Please complete all course fields.")
                else:
                    try:
                        with connect() as con:
                            con.execute("INSERT INTO courses VALUES(?,?,?,?,?,?,?,?)",(code,title,cat,instructor,dur,capacity,0,level))
                        st.success(f"Course {code} added successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError: st.error("A course with this code already exists.")
    st.info("Prototype note: this admin area is intended for demonstration. Add authentication and role-based permissions before production use.")

st.caption("CourseCloud · Mini Project Prototype · Data stored in SQLite")
