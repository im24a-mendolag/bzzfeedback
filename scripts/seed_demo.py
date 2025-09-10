import os
import sys
import random
from datetime import datetime, timedelta
import mysql.connector

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DB_CONFIG


def main():
    cfg = DB_CONFIG.copy()
    conn = mysql.connector.connect(**cfg)
    try:
        cur = conn.cursor(dictionary=True)

        # Ensure some teachers and subjects
        teachers = []
        cur.execute("SELECT t.id, u.username FROM teachers t JOIN users u ON u.id=t.user_id ORDER BY t.id")
        teachers = cur.fetchall()
        if not teachers:
            print("No teachers found. Please run scripts/init_db.py first.")
            return

        cur.execute("SELECT id, name FROM subjects ORDER BY id")
        subjects = cur.fetchall()
        if not subjects:
            print("No subjects found. Please run scripts/init_db.py first.")
            return

        # Ensure some students
        student_usernames = [f"stud{i}" for i in range(1, 21)]
        for uname in student_usernames:
            cur.execute("SELECT id FROM users WHERE username=%s", (uname,))
            row = cur.fetchone()
            if not row:
                # Simple password placeholder; you can login if needed
                from werkzeug.security import generate_password_hash
                pw = generate_password_hash("Passw0rd!")
                cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'student')", (uname, pw))
        conn.commit()

        cur.execute("SELECT id, username FROM users WHERE role='student' ORDER BY id")
        students = cur.fetchall()

        # Global categories
        cur.execute("SELECT id, name FROM feedback_categories WHERE subject_id IS NULL")
        global_categories = cur.fetchall()
        if not global_categories:
            cur.executemany(
                "INSERT INTO feedback_categories (subject_id, name) VALUES (NULL, %s)",
                [(n,) for n in ["Homework", "Exams", "Pace", "Clarity", "Materials", "Behavior"]]
            )
            conn.commit()
            cur.execute("SELECT id, name FROM feedback_categories WHERE subject_id IS NULL")
            global_categories = cur.fetchall()

        # Generate feedbacks
        titles = [
            "Homework volume",
            "Lesson pace",
            "Exam difficulty",
            "Classroom clarity",
            "Project guidance",
            "Feedback speed",
            "Materials quality",
            "Group work balance",
        ]
        infos = [
            "I feel the homework is a bit too much this week.",
            "The pace was fast; could we slow down for complex topics?",
            "The exam felt harder than expected compared to lessons.",
            "Sometimes explanations are hard to follow, examples help a lot.",
            "More guidance on the project requirements would be appreciated.",
            "Could we get feedback on assignments a bit sooner?",
            "Some materials are outdated; newer examples might help.",
            "Group distribution could be more balanced across skills.",
        ]

        num_items = 150
        created = 0
        for _ in range(num_items):
            student = random.choice(students)
            teacher = random.choice(teachers)
            subject = random.choice(subjects)
            category = random.choice(global_categories)
            title = random.choice(titles)
            info = random.choice(infos)
            is_read = 1 if random.random() < 0.5 else 0
            # Spread creation times across last 60 days
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))

            cur.execute(
                """
                INSERT INTO feedback (student_id, teacher_id, subject_id, category_id, title, info, is_read, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (student['id'], teacher['id'], subject['id'], category['id'], title, info, is_read, created_at)
            )
            created += 1

        conn.commit()
        print(f"Created {created} demo feedback entries.")

    finally:
        conn.close()


if __name__ == '__main__':
    main()


