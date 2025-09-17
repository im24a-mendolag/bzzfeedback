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

        # Ensure an admin user exists (username: admin / password: admin)
        from werkzeug.security import generate_password_hash
        cur.execute("SELECT id FROM users WHERE username=%s", ("admin",))
        admin_row = cur.fetchone()
        admin_hash = generate_password_hash("admin")
        if not admin_row:
            cur2 = conn.cursor()
            cur2.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'admin')",
                ("admin", admin_hash)
            )
            conn.commit()
            cur2.close()
        else:
            cur2 = conn.cursor()
            cur2.execute(
                "UPDATE users SET role='admin', password_hash=%s WHERE id=%s",
                (admin_hash, admin_row['id'])
            )
            conn.commit()
            cur2.close()

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

        # Ensure some students with classes
        student_usernames = [f"stud{i}" for i in range(1, 21)]
        classes = ['Grade 9A', 'Grade 9B', 'Grade 10A', 'Grade 10B', 'Grade 11A', 'Grade 11B', 'Grade 12A', 'Grade 12B']
        
        for i, uname in enumerate(student_usernames):
            cur.execute("SELECT id FROM users WHERE username=%s", (uname,))
            row = cur.fetchone()
            if not row:
                # Simple password placeholder; you can login if needed
                from werkzeug.security import generate_password_hash
                pw = generate_password_hash("Passw0rd!")
                # Assign students to different classes
                student_class = classes[i % len(classes)]
                cur.execute("INSERT INTO users (username, password_hash, role, class_name) VALUES (%s, %s, 'student', %s)", (uname, pw, student_class))
        conn.commit()
        
        # Ensure teacher-class relationships exist (at least 2 teachers per class)
        # First, ensure each class has at least 2 teachers
        for class_name in classes:
            cur.execute("SELECT COUNT(*) as count FROM teacher_classes WHERE class_name=%s", (class_name,))
            count_result = cur.fetchone()
            current_count = count_result['count'] if count_result else 0
            
            if current_count < 2:
                # Get teachers not yet assigned to this class
                cur.execute("""
                    SELECT t.id FROM teachers t 
                    WHERE t.id NOT IN (
                        SELECT tc.teacher_id FROM teacher_classes tc WHERE tc.class_name = %s
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (class_name, 2 - current_count))
                available_teachers = cur.fetchall()
                
                # Assign these teachers to the class
                for teacher in available_teachers:
                    cur.execute("INSERT INTO teacher_classes (teacher_id, class_name) VALUES (%s, %s)", (teacher['id'], class_name))
        
        # Then add some additional random assignments for variety
        for teacher in teachers:
            # Each teacher teaches additional classes (2-4 total)
            cur.execute("SELECT COUNT(*) as count FROM teacher_classes WHERE teacher_id=%s", (teacher['id'],))
            count_result = cur.fetchone()
            current_teacher_count = count_result['count'] if count_result else 0
            
            if current_teacher_count < 4:
                additional_classes = random.sample(classes, min(random.randint(1, 3), 4 - current_teacher_count))
                for class_name in additional_classes:
                    cur.execute("SELECT 1 FROM teacher_classes WHERE teacher_id=%s AND class_name=%s", (teacher['id'], class_name))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO teacher_classes (teacher_id, class_name) VALUES (%s, %s)", (teacher['id'], class_name))
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
            
            # Get student's class
            cur.execute("SELECT class_name FROM users WHERE id=%s", (student['id'],))
            student_class_row = cur.fetchone()
            if not student_class_row or not student_class_row['class_name']:
                continue  # Skip students without class
            
            student_class = student_class_row['class_name']
            
            # Get teachers that teach this student's class
            cur.execute("""
                SELECT t.id FROM teachers t 
                JOIN teacher_classes tc ON tc.teacher_id = t.id 
                WHERE tc.class_name = %s
            """, (student_class,))
            available_teachers = cur.fetchall()
            
            if not available_teachers:
                continue  # Skip if no teachers teach this class
            
            teacher = random.choice(available_teachers)
            
            # Get subjects that this teacher teaches
            cur.execute("""
                SELECT s.id FROM subjects s 
                JOIN teacher_subjects ts ON ts.subject_id = s.id 
                WHERE ts.teacher_id = %s
            """, (teacher['id'],))
            available_subjects = cur.fetchall()
            
            if not available_subjects:
                continue  # Skip if teacher has no subjects
            
            subject = random.choice(available_subjects)
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


