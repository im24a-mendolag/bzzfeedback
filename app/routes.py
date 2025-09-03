from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .auth import verify_login, hash_password
from .db import query_all, query_one, execute

bp = Blueprint('routes', __name__)


@bp.get('/')
def index():
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = verify_login(email, password)
        if user:
            login_user(user)
            return redirect(url_for('routes.dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('email', '').strip()
        display_name = request.form.get('display_name', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        is_teacher = request.form.get('is_teacher') == 'on'

        if not username or not display_name or not password:
            flash('Please fill all required fields', 'error')
            return render_template('register.html')
        if password != password2:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        existing = query_one('SELECT id FROM users WHERE email=%s', (username,))
        if existing:
            flash('Username already taken', 'error')
            return render_template('register.html')

        role = 'teacher' if is_teacher else 'student'
        user_id = execute(
            'INSERT INTO users (email, password_hash, display_name, role) VALUES (%s, %s, %s, %s)',
            (username, hash_password(password), display_name, role),
        )

        if role == 'teacher':
            execute('INSERT INTO teachers (user_id) VALUES (%s)', (user_id,))

        # Auto-login after register
        user_row = query_one('SELECT id, email, display_name, role FROM users WHERE id=%s', (user_id,))
        if user_row:
            from .auth import User  # local import to avoid circular at top
            login_user(User(user_row['id'], user_row['email'], user_row['display_name'], user_row['role']))
            return redirect(url_for('routes.dashboard'))

        flash('Registration complete. Please login.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('register.html')


@bp.post('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@bp.get('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('routes.teacher_feedback'))
    # student flow: choose teacher then subject
    teachers = query_all(
        """
        SELECT t.id, u.display_name
        FROM teachers t
        JOIN users u ON u.id = t.user_id
        ORDER BY u.display_name
        """
    )
    return render_template('student_dashboard.html', teachers=teachers)


@bp.get('/my-feedback')
@login_required
def my_feedback():
    if current_user.role != 'student':
        return redirect(url_for('routes.dashboard'))

    rows = query_all(
        """
        SELECT f.id, f.title, f.info, f.is_read, f.created_at,
               s.name AS subject_name,
               u.display_name AS teacher_name,
               COALESCE(fc.name, '') AS category_name
        FROM feedback f
        JOIN subjects s ON s.id = f.subject_id
        JOIN teachers t ON t.id = f.teacher_id
        JOIN users u ON u.id = t.user_id
        LEFT JOIN feedback_categories fc ON fc.id = f.category_id
        WHERE f.student_id=%s
        ORDER BY f.created_at DESC
        """,
        (int(current_user.id),),
    )
    return render_template('my_feedback.html', feedback=rows)


@bp.post('/feedback/<int:feedback_id>/delete')
@login_required
def delete_feedback(feedback_id: int):
    # only the student who created it can delete
    fb = query_one('SELECT id, student_id FROM feedback WHERE id=%s', (feedback_id,))
    if not fb or fb['student_id'] != int(current_user.id):
        return redirect(url_for('routes.dashboard'))
    execute('DELETE FROM feedback WHERE id=%s', (feedback_id,))
    flash('Feedback deleted', 'success')
    return redirect(url_for('routes.my_feedback'))


@bp.get('/choose-subject/<int:teacher_id>')
@login_required
def choose_subject(teacher_id: int):
    subjects = query_all(
        """
        SELECT s.id, s.name
        FROM teacher_subjects ts
        JOIN subjects s ON s.id = ts.subject_id
        WHERE ts.teacher_id = %s
        ORDER BY s.name
        """,
        (teacher_id,),
    )
    categories = query_all(
        "SELECT id, name FROM feedback_categories WHERE subject_id IS NULL ORDER BY name"
    )
    return render_template('choose_subject.html', teacher_id=teacher_id, subjects=subjects, categories=categories)


@bp.route('/submit-feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        teacher_id = int(request.form.get('teacher_id'))
        subject_id = int(request.form.get('subject_id'))
        category_id = request.form.get('category_id')
        custom_category = request.form.get('custom_category', '').strip()
        title = request.form.get('title', '').strip()
        info = request.form.get('info', '').strip()

        if custom_category:
            # upsert category for this subject
            existing = query_one(
                "SELECT id FROM feedback_categories WHERE subject_id=%s AND name=%s",
                (subject_id, custom_category),
            )
            if existing:
                category_id = existing['id']
            else:
                category_id = execute(
                    "INSERT INTO feedback_categories (subject_id, name) VALUES (%s, %s)",
                    (subject_id, custom_category),
                )
        elif category_id:
            category_id = int(category_id)
        else:
            category_id = None

        execute(
            """
            INSERT INTO feedback (student_id, teacher_id, subject_id, category_id, title, info)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (int(current_user.id) if current_user.role == 'student' else None, teacher_id, subject_id, category_id, title, info),
        )
        flash('Feedback submitted', 'success')
        return redirect(url_for('routes.dashboard'))

    # GET expects teacher_id to prefill subject chooser
    teacher_id = int(request.args.get('teacher_id'))
    return redirect(url_for('routes.choose_subject', teacher_id=teacher_id))


@bp.get('/teacher/feedback')
@login_required
def teacher_feedback():
    if current_user.role != 'teacher':
        return redirect(url_for('routes.dashboard'))

    teacher_row = query_one("SELECT id FROM teachers WHERE user_id=%s", (int(current_user.id),))
    if not teacher_row:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('routes.dashboard'))
    teacher_id = teacher_row['id']

    show_unread_only = request.args.get('unread') == '1'
    where_clause = 'WHERE f.teacher_id=%s' + (' AND f.is_read=0' if show_unread_only else '')
    rows = query_all(
        f"""
        SELECT f.id, f.title, f.info, f.is_read, f.created_at,
               s.name AS subject_name,
               fc.name AS category_name
        FROM feedback f
        JOIN subjects s ON s.id = f.subject_id
        LEFT JOIN feedback_categories fc ON fc.id = f.category_id
        {where_clause}
        ORDER BY f.created_at DESC
        """,
        (teacher_id,),
    )
    return render_template('teacher_feedback.html', feedback=rows, show_unread_only=show_unread_only)


@bp.post('/teacher/feedback/<int:feedback_id>/mark-read')
@login_required
def mark_feedback_read(feedback_id: int):
    if current_user.role != 'teacher':
        return redirect(url_for('routes.dashboard'))

    teacher_row = query_one("SELECT id FROM teachers WHERE user_id=%s", (int(current_user.id),))
    if not teacher_row:
        return redirect(url_for('routes.dashboard'))
    teacher_id = teacher_row['id']

    execute(
        "UPDATE feedback SET is_read=1 WHERE id=%s AND teacher_id=%s",
        (feedback_id, teacher_id),
    )
    flash('Marked as read', 'success')
    return redirect(url_for('routes.teacher_feedback'))


@bp.route('/feedback/<int:feedback_id>/thread', methods=['GET', 'POST'])
@login_required
def feedback_thread(feedback_id: int):
    # authorize: teacher who owns it or student who posted it
    fb = query_one(
        """
        SELECT f.id, f.student_id, f.teacher_id, f.title, f.info,
               s.name AS subject_name,
               u_t.display_name AS teacher_name,
               u_s.display_name AS student_name
        FROM feedback f
        JOIN subjects s ON s.id = f.subject_id
        JOIN teachers t ON t.id = f.teacher_id
        JOIN users u_t ON u_t.id = t.user_id
        LEFT JOIN users u_s ON u_s.id = f.student_id
        WHERE f.id=%s
        """,
        (feedback_id,),
    )
    if not fb:
        return redirect(url_for('routes.dashboard'))

    is_teacher = current_user.role == 'teacher'
    is_student = current_user.role == 'student'

    allowed = False
    if is_teacher:
        teacher_row = query_one("SELECT id FROM teachers WHERE user_id=%s", (int(current_user.id),))
        allowed = bool(teacher_row and teacher_row['id'] == fb['teacher_id'])
    elif is_student:
        allowed = (fb['student_id'] == int(current_user.id))

    if not allowed:
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            execute(
                'INSERT INTO feedback_messages (feedback_id, sender_user_id, message) VALUES (%s, %s, %s)',
                (feedback_id, int(current_user.id), message),
            )
            return redirect(url_for('routes.feedback_thread', feedback_id=feedback_id))

    messages = query_all(
        """
        SELECT fm.id, fm.message, fm.created_at,
               CASE WHEN u.role = 'teacher' THEN CONCAT(u.display_name, ' (Teacher)') ELSE 'Student' END AS sender_name
        FROM feedback_messages fm
        JOIN users u ON u.id = fm.sender_user_id
        WHERE fm.feedback_id=%s
        ORDER BY fm.created_at ASC
        """,
        (feedback_id,),
    )
    # Do not leak student identity in header either
    fb_public = dict(fb)
    if fb_public.get('student_id'):
        fb_public['student_name'] = 'Student'
    return render_template('feedback_thread.html', fb=fb_public, messages=messages)

