from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
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
        email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = verify_login(email, password)
        if user:
            login_user(user)
            current_app.logger.info(f"login success user_id={user.id} username={user.username}")
            return redirect(url_for('routes.dashboard'))
        current_app.logger.info(f"login failed username={email}")
        flash('Invalid credentials', 'error')
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        class_name = request.form.get('class_name', '').strip()

        if not username or not password:
            flash('Please fill all required fields', 'error')
            return render_template('register.html')
        # display_name deprecated; keep local var for backward compat but do not store
        if password != password2:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        # Class selection is required for all registrations (students only)
        if not class_name:
            flash('Please select your class', 'error')
            return render_template('register.html')

        existing = query_one('SELECT id FROM users WHERE username=%s', (username,))
        if existing:
            flash('Username already taken', 'error')
            current_app.logger.info(f"register duplicate username={username}")
            return render_template('register.html')

        # All registrations are students now
        user_id = execute(
            'INSERT INTO users (username, password_hash, role, class_name) VALUES (%s, %s, %s, %s)',
            (username, hash_password(password), 'student', class_name),
        )

        current_app.logger.info(f"register student user_id={user_id} username={username} class={class_name}")

        # Auto-login after register
        user_row = query_one('SELECT id, username, role, class_name FROM users WHERE id=%s', (user_id,))
        if user_row:
            from .auth import User  # local import to avoid circular at top
            login_user(User(user_row['id'], user_row['username'], user_row['role'], user_row['class_name']))
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
        current_app.logger.info(f"view teacher dashboard user_id={current_user.id}")
        return redirect(url_for('routes.teacher_feedback'))
    if current_user.role == 'admin':
        return redirect(url_for('routes.admin_feedback'))
    # student flow: choose teacher then subject
    # Get student's class information
    student_info = query_one('SELECT class_name FROM users WHERE id=%s', (current_user.id,))
    student_class = student_info['class_name'] if student_info else None
    
    if not student_class:
        # If student has no class assigned, show all teachers (fallback)
        teachers = query_all(
            """
            SELECT t.id, u.username
            FROM teachers t
            JOIN users u ON u.id = t.user_id
            ORDER BY u.username
            """
        )
        current_app.logger.warning(f"student {current_user.id} has no class assigned, showing all teachers")
    else:
        # Show only teachers that teach the student's class
        teachers = query_all(
            """
            SELECT DISTINCT t.id, u.username
            FROM teachers t
            JOIN users u ON u.id = t.user_id
            JOIN teacher_classes tc ON tc.teacher_id = t.id
            WHERE tc.class_name = %s
            ORDER BY u.username
            """,
            (student_class,)
        )
    
    current_app.logger.info(f"view student dashboard user_id={current_user.id} class={student_class} teachers={len(teachers)}")
    return render_template('student_dashboard.html', teachers=teachers, student_class=student_class)


@bp.get('/my-feedback')
@login_required
def my_feedback():
    if current_user.role != 'student':
        return redirect(url_for('routes.dashboard'))

    rows = query_all(
        """
        SELECT f.id, f.title, f.info, f.is_read, f.moderation_status, f.created_at,
               s.name AS subject_name,
               u.username AS teacher_name,
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
    current_app.logger.info(f"view my_feedback user_id={current_user.id} count={len(rows)}")
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
    current_app.logger.info(f"delete feedback id={feedback_id} by user_id={current_user.id}")
    return redirect(url_for('routes.my_feedback'))


@bp.route('/feedback/<int:feedback_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_feedback(feedback_id: int):
    # only the student who created it can edit
    if current_user.role != 'student':
        return redirect(url_for('routes.dashboard'))
    
    # Get feedback details
    fb = query_one(
        """
        SELECT f.id, f.student_id, f.teacher_id, f.subject_id, f.category_id, f.title, f.info,
               s.name AS subject_name,
               u.username AS teacher_name,
               fc.name AS category_name
        FROM feedback f
        JOIN subjects s ON s.id = f.subject_id
        JOIN teachers t ON t.id = f.teacher_id
        JOIN users u ON u.id = t.user_id
        LEFT JOIN feedback_categories fc ON fc.id = f.category_id
        WHERE f.id=%s
        """,
        (feedback_id,),
    )
    
    if not fb:
        flash('Feedback not found', 'error')
        return redirect(url_for('routes.my_feedback'))
    
    if fb['student_id'] != int(current_user.id):
        flash('You can only edit your own feedback', 'error')
        return redirect(url_for('routes.my_feedback'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        info = request.form.get('info', '').strip()
        category_id = request.form.get('category_id')
        custom_category = request.form.get('custom_category', '').strip()
        
        if not title or not info:
            flash('Title and feedback content are required', 'error')
            return redirect(url_for('routes.edit_feedback', feedback_id=feedback_id))
        
        # Handle category selection
        if category_id == '__custom__':
            if custom_category:
                # Check if custom category already exists for this subject
                existing = query_one(
                    "SELECT id FROM feedback_categories WHERE subject_id=%s AND name=%s",
                    (fb['subject_id'], custom_category),
                )
                if existing:
                    category_id = existing['id']
                else:
                    category_id = execute(
                        "INSERT INTO feedback_categories (subject_id, name) VALUES (%s, %s)",
                        (fb['subject_id'], custom_category),
                    )
            else:
                flash('Please provide a custom category name', 'error')
                return redirect(url_for('routes.edit_feedback', feedback_id=feedback_id))
        elif category_id:
            category_id = int(category_id)
        else:
            flash('Please choose a category', 'error')
            return redirect(url_for('routes.edit_feedback', feedback_id=feedback_id))
        
        execute(
            "UPDATE feedback SET title=%s, info=%s, category_id=%s WHERE id=%s",
            (title, info, category_id, feedback_id)
        )
        flash('Feedback updated successfully', 'success')
        current_app.logger.info(f"edit feedback id={feedback_id} by user_id={current_user.id}")
        return redirect(url_for('routes.my_feedback'))
    
    # Get available categories for this subject
    categories = query_all(
        """
        SELECT id, name FROM feedback_categories 
        WHERE subject_id IS NULL OR subject_id = %s 
        ORDER BY name
        """,
        (fb['subject_id'],)
    )
    
    return render_template('edit_feedback.html', feedback=fb, categories=categories)


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
    
    # Get teacher's name
    teacher_info = query_one(
        """
        SELECT u.username
        FROM teachers t
        JOIN users u ON u.id = t.user_id
        WHERE t.id = %s
        """,
        (teacher_id,),
    )
    teacher_name = teacher_info['username'] if teacher_info else 'Unknown Teacher'
    
    current_app.logger.info(f"choose_subject user_id={current_user.id} teacher_id={teacher_id} subjects={len(subjects)}")
    return render_template('choose_subject.html', teacher_id=teacher_id, teacher_name=teacher_name, subjects=subjects, categories=categories)


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

        # Determine category id based on selection (required)
        if category_id == '__custom__':
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
            else:
                flash('Please provide a custom category name', 'error')
                return redirect(url_for('routes.choose_subject', teacher_id=teacher_id))
        elif category_id:
            category_id = int(category_id)
        else:
            flash('Please choose a category', 'error')
            return redirect(url_for('routes.choose_subject', teacher_id=teacher_id))

        execute(
            """
            INSERT INTO feedback (student_id, teacher_id, subject_id, category_id, title, info, moderation_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """,
            (int(current_user.id) if current_user.role == 'student' else None, teacher_id, subject_id, category_id, title, info),
        )
        flash('Feedback submitted', 'success')
        current_app.logger.info(f"submit_feedback by user_id={current_user.id} teacher_id={teacher_id} subject_id={subject_id} category_id={category_id}")
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

    subject_id = request.args.get('subject_id')

    # If no subject selected, show subject overview with counts
    if not subject_id:
        subjects = query_all(
            """
            SELECT s.id, s.name,
                   COALESCE(SUM(CASE WHEN f.is_read = 0 THEN 1 ELSE 0 END), 0) AS unread_count,
                   COALESCE(SUM(CASE WHEN f.is_read = 1 THEN 1 ELSE 0 END), 0) AS read_count,
                   COALESCE(COUNT(f.id), 0) AS total_count
            FROM teacher_subjects ts
            JOIN subjects s ON s.id = ts.subject_id
            LEFT JOIN feedback f ON f.teacher_id = %s AND f.subject_id = s.id AND f.moderation_status = 'approved'
            WHERE ts.teacher_id = %s
            GROUP BY s.id, s.name
            ORDER BY s.name
            """,
            (teacher_id, teacher_id),
        )
        current_app.logger.info(f"view teacher subjects overview user_id={current_user.id} subjects={len(subjects)}")
        return render_template('teacher_subjects.html', subjects=subjects)

    # Per-subject feedback list
    subject_id = int(subject_id)
    show_unread_only = request.args.get('unread') == '1'
    where_clause = "WHERE f.teacher_id=%s AND f.subject_id=%s AND f.moderation_status='approved'" + (' AND f.is_read=0' if show_unread_only else '')
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
        (teacher_id, subject_id),
    )
    current_app.logger.info(f"view teacher_feedback user_id={current_user.id} subject_id={subject_id} unread_only={show_unread_only} count={len(rows)}")
    return render_template('teacher_feedback.html', feedback=rows, show_unread_only=show_unread_only, subject_id=subject_id)


@bp.get('/admin/feedback')
@login_required
def admin_feedback():
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))

    subject_id = request.args.get('subject_id')
    if not subject_id:
        subjects = query_all(
            """
            SELECT s.id, s.name,
                   COALESCE(SUM(CASE WHEN f.moderation_status='pending' THEN 1 ELSE 0 END), 0) AS pending_count,
                   COALESCE(SUM(CASE WHEN f.moderation_status='approved' THEN 1 ELSE 0 END), 0) AS approved_count,
                   COALESCE(SUM(CASE WHEN f.moderation_status='rejected' THEN 1 ELSE 0 END), 0) AS rejected_count,
                   COALESCE(COUNT(f.id), 0) AS total_count
            FROM subjects s
            LEFT JOIN feedback f ON f.subject_id = s.id
            GROUP BY s.id, s.name
            ORDER BY s.name
            """
        )
        return render_template('admin_subjects.html', subjects=subjects)

    subject_id = int(subject_id)
    status = request.args.get('status', 'pending')
    rows = query_all(
        """
        SELECT f.id, f.title, f.info, f.moderation_status, f.created_at,
               s.name AS subject_name,
               u_t.username AS teacher_name
        FROM feedback f
        JOIN subjects s ON s.id = f.subject_id
        JOIN teachers t ON t.id = f.teacher_id
        JOIN users u_t ON u_t.id = t.user_id
        WHERE f.subject_id=%s AND f.moderation_status=%s
        ORDER BY f.created_at DESC
        """,
        (subject_id, status),
    )
    return render_template('admin_feedback.html', feedback=rows, subject_id=subject_id, status=status)


@bp.post('/admin/feedback/<int:feedback_id>/approve')
@login_required
def admin_approve(feedback_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    execute("UPDATE feedback SET moderation_status='approved' WHERE id=%s", (feedback_id,))
    return redirect(request.referrer or url_for('routes.admin_feedback'))


@bp.post('/admin/feedback/<int:feedback_id>/reject')
@login_required
def admin_reject(feedback_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    execute("UPDATE feedback SET moderation_status='rejected' WHERE id=%s", (feedback_id,))
    return redirect(request.referrer or url_for('routes.admin_feedback'))


@bp.post('/admin/feedback/<int:feedback_id>/change-status')
@login_required
def admin_change_status(feedback_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'approved', 'rejected']:
        flash('Invalid status', 'error')
        return redirect(request.referrer or url_for('routes.admin_feedback'))
    
    execute("UPDATE feedback SET moderation_status=%s WHERE id=%s", (new_status, feedback_id))
    flash(f'Feedback status changed to {new_status}', 'success')
    return redirect(request.referrer or url_for('routes.admin_feedback'))


@bp.get('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    users = query_all(
        """
        SELECT u.id, u.username, u.role, u.created_at,
               CASE WHEN t.id IS NOT NULL THEN 1 ELSE 0 END as is_teacher,
               GROUP_CONCAT(s.name ORDER BY s.name SEPARATOR ', ') as subjects
        FROM users u
        LEFT JOIN teachers t ON t.user_id = u.id
        LEFT JOIN teacher_subjects ts ON ts.teacher_id = t.id
        LEFT JOIN subjects s ON s.id = ts.subject_id
        GROUP BY u.id, u.username, u.role, u.created_at, t.id
        ORDER BY u.created_at DESC
        """
    )
    return render_template('admin_users.html', users=users)


@bp.post('/admin/users/<int:user_id>/delete')
@login_required
def admin_delete_user(user_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    if user_id == current_user.id:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('routes.admin_users'))
    
    user = query_one("SELECT username, role FROM users WHERE id=%s", (user_id,))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('routes.admin_users'))
    
    execute("DELETE FROM users WHERE id=%s", (user_id,))
    flash(f'User {user["username"]} has been deleted', 'success')
    return redirect(url_for('routes.admin_users'))


@bp.post('/admin/users/<int:user_id>/promote')
@login_required
def admin_promote_user(user_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    new_role = request.form.get('role')
    if new_role not in ['student', 'teacher', 'admin']:
        flash('Invalid role', 'error')
        return redirect(url_for('routes.admin_users'))
    
    user = query_one("SELECT username, role FROM users WHERE id=%s", (user_id,))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('routes.admin_users'))
    
    # Update user role
    execute("UPDATE users SET role=%s WHERE id=%s", (new_role, user_id))
    
    # If promoting to teacher, ensure teacher record exists
    if new_role == 'teacher':
        teacher_exists = query_one("SELECT id FROM teachers WHERE user_id=%s", (user_id,))
        if not teacher_exists:
            execute("INSERT INTO teachers (user_id) VALUES (%s)", (user_id,))
    
    flash(f'User {user["username"]} role changed to {new_role}', 'success')
    return redirect(url_for('routes.admin_users'))


@bp.get('/admin/teachers/<int:teacher_id>/subjects')
@login_required
def admin_teacher_subjects(teacher_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    teacher = query_one(
        """
        SELECT t.id, u.username
        FROM teachers t
        JOIN users u ON u.id = t.user_id
        WHERE t.id = %s
        """,
        (teacher_id,)
    )
    
    if not teacher:
        flash('Teacher not found', 'error')
        return redirect(url_for('routes.admin_users'))
    
    # Get current subjects
    current_subjects = query_all(
        """
        SELECT s.id, s.name
        FROM subjects s
        JOIN teacher_subjects ts ON ts.subject_id = s.id
        WHERE ts.teacher_id = %s
        ORDER BY s.name
        """,
        (teacher_id,)
    )
    
    # Get all available subjects
    all_subjects = query_all(
        """
        SELECT s.id, s.name
        FROM subjects s
        ORDER BY s.name
        """
    )
    
    return render_template('admin_teacher_subjects.html', 
                         teacher=teacher, 
                         current_subjects=current_subjects, 
                         all_subjects=all_subjects)


@bp.post('/admin/teachers/<int:teacher_id>/subjects/add')
@login_required
def admin_add_teacher_subject(teacher_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    subject_id = request.form.get('subject_id')
    if not subject_id:
        flash('Subject not specified', 'error')
        return redirect(url_for('routes.admin_teacher_subjects', teacher_id=teacher_id))
    
    # Check if relationship already exists
    exists = query_one(
        "SELECT id FROM teacher_subjects WHERE teacher_id=%s AND subject_id=%s",
        (teacher_id, subject_id)
    )
    
    if exists:
        flash('Teacher already assigned to this subject', 'error')
    else:
        execute(
            "INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (%s, %s)",
            (teacher_id, subject_id)
        )
        subject = query_one("SELECT name FROM subjects WHERE id=%s", (subject_id,))
        flash(f'Added {subject["name"]} to teacher', 'success')
    
    return redirect(url_for('routes.admin_teacher_subjects', teacher_id=teacher_id))


@bp.post('/admin/teachers/<int:teacher_id>/subjects/<int:subject_id>/remove')
@login_required
def admin_remove_teacher_subject(teacher_id: int, subject_id: int):
    if current_user.role != 'admin':
        return redirect(url_for('routes.dashboard'))
    
    subject = query_one("SELECT name FROM subjects WHERE id=%s", (subject_id,))
    execute(
        "DELETE FROM teacher_subjects WHERE teacher_id=%s AND subject_id=%s",
        (teacher_id, subject_id)
    )
    flash(f'Removed {subject["name"]} from teacher', 'success')
    
    return redirect(url_for('routes.admin_teacher_subjects', teacher_id=teacher_id))


@bp.get('/account')
@login_required
def account_settings():
    user = query_one("SELECT username, role FROM users WHERE id=%s", (current_user.id,))
    return render_template('account_settings.html', user=user)


@bp.post('/account/change-username')
@login_required
def change_username():
    new_username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not new_username:
        flash('Username is required', 'error')
        return redirect(url_for('routes.account_settings'))
    
    if not password:
        flash('Current password is required', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Verify current password
    if not verify_login(current_user.username, password):
        flash('Incorrect password', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Check if username already exists
    existing = query_one("SELECT id FROM users WHERE username=%s AND id!=%s", (new_username, current_user.id))
    if existing:
        flash('Username already taken', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Update username
    execute("UPDATE users SET username=%s WHERE id=%s", (new_username, current_user.id))
    
    # Update current user object
    current_user.username = new_username
    
    flash('Username updated successfully', 'success')
    return redirect(url_for('routes.account_settings'))


@bp.post('/account/change-password')
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required', 'error')
        return redirect(url_for('routes.account_settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('routes.account_settings'))
    
    if len(new_password) < 8:
        flash('New password must be at least 8 characters long', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Verify current password
    if not verify_login(current_user.username, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Hash new password
    from werkzeug.security import generate_password_hash
    new_password_hash = generate_password_hash(new_password)
    
    # Update password
    execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_password_hash, current_user.id))
    
    flash('Password updated successfully', 'success')
    return redirect(url_for('routes.account_settings'))


@bp.post('/account/delete')
@login_required
def delete_account():
    password = request.form.get('password', '')
    
    if not password:
        flash('Password is required to delete account', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Verify current password
    if not verify_login(current_user.username, password):
        flash('Incorrect password', 'error')
        return redirect(url_for('routes.account_settings'))
    
    # Get user info for flash message
    user = query_one("SELECT username FROM users WHERE id=%s", (current_user.id,))
    username = user['username']
    
    # Delete user (cascades will handle related records)
    execute("DELETE FROM users WHERE id=%s", (current_user.id,))
    
    # Logout user
    logout_user()
    
    flash(f'Account {username} has been deleted', 'success')
    return redirect(url_for('routes.index'))


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
    current_app.logger.info(f"mark_read feedback_id={feedback_id} by teacher_user_id={current_user.id}")
    # Redirect back to current subject/filter if provided, else overview
    subject_id = request.args.get('subject_id')
    unread = request.args.get('unread')
    if subject_id:
        return redirect(url_for('routes.teacher_feedback', subject_id=int(subject_id), unread=unread))
    return redirect(url_for('routes.teacher_feedback'))


@bp.route('/feedback/<int:feedback_id>/thread', methods=['GET', 'POST'])
@login_required
def feedback_thread(feedback_id: int):
    # authorize: teacher who owns it or student who posted it
    fb = query_one(
        """
        SELECT f.id, f.student_id, f.teacher_id, f.title, f.info,
               s.name AS subject_name,
               u_t.username AS teacher_name,
               u_s.username AS student_name
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
            current_app.logger.info(f"thread message feedback_id={feedback_id} by user_id={current_user.id}")
            return redirect(url_for('routes.feedback_thread', feedback_id=feedback_id))

    messages = query_all(
        """
        SELECT fm.id, fm.message, fm.created_at,
               CASE WHEN u.role = 'teacher' THEN CONCAT(u.username, ' (Teacher)') ELSE 'Student' END AS sender_name
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

