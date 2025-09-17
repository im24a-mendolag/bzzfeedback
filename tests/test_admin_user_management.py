from .conftest import login
from app.db import execute, query_one


def test_admin_users_page_access(client):
    """Test that admins can access user management page"""
    # Login as admin (admin password is set by seed_demo.py to "admin")
    resp = login(client, 'admin', 'admin')
    assert resp.status_code == 200
    
    # Access user management
    resp = client.get('/admin/users')
    assert resp.status_code == 200
    assert b'User Management' in resp.data
    assert b'alice' in resp.data  # Should show seeded users


def test_admin_users_page_non_admin_redirect(client):
    """Test that non-admins are redirected from user management"""
    # Login as teacher
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200
    
    # Try to access user management
    resp = client.get('/admin/users')
    assert resp.status_code == 302  # Redirect to dashboard


def test_admin_change_user_role(client):
    """Test that admins can change user roles"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # Change alice from teacher to student
    resp = client.post('/admin/users/1/promote', data={'role': 'student'})
    assert resp.status_code == 302  # Redirect after success
    
    # Verify role was changed
    user = query_one("SELECT role FROM users WHERE id=1")
    assert user['role'] == 'student'


def test_admin_promote_user_to_teacher(client):
    """Test that promoting to teacher creates teacher record"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # First ensure user is not a teacher
    execute("DELETE FROM teachers WHERE user_id=1")
    execute("UPDATE users SET role='student' WHERE id=1")
    
    # Promote to teacher
    resp = client.post('/admin/users/1/promote', data={'role': 'teacher'})
    assert resp.status_code == 302  # Redirect after success
    
    # Verify user role and teacher record
    user = query_one("SELECT role FROM users WHERE id=1")
    assert user['role'] == 'teacher'
    
    teacher = query_one("SELECT id FROM teachers WHERE user_id=1")
    assert teacher is not None


def test_admin_delete_user(client):
    """Test that admins can delete users"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # Delete bob (user id 2)
    resp = client.post('/admin/users/2/delete')
    assert resp.status_code == 302  # Redirect after success
    
    # Verify user was deleted
    user = query_one("SELECT id FROM users WHERE id=2")
    assert user is None


def test_admin_cannot_delete_self(client):
    """Test that admins cannot delete their own account"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # Get admin user ID dynamically
    admin_user = query_one("SELECT id FROM users WHERE username='admin'")
    admin_id = admin_user['id']
    
    # Try to delete self
    resp = client.post(f'/admin/users/{admin_id}/delete')
    assert resp.status_code == 302  # Redirect back to users page
    # Should show error message (tested via flash message)
    
    # Verify admin user still exists (check by username, not ID, since other tests might delete users)
    user = query_one("SELECT id FROM users WHERE username='admin'")
    assert user is not None


def test_admin_teacher_subjects_page(client):
    """Test admin can access teacher subject management"""
    # Login as admin
    login(client, 'admin', 'admin')

    # Get alice's teacher id dynamically
    from app.db import query_one
    alice_teacher = query_one("""
        SELECT t.id FROM teachers t 
        JOIN users u ON u.id = t.user_id 
        WHERE u.username = 'alice'
    """)
    
    if not alice_teacher:
        # Create teacher record for alice if it doesn't exist
        from app.db import execute
        execute("INSERT INTO teachers (user_id) SELECT id FROM users WHERE username='alice'")
        alice_teacher = query_one("""
            SELECT t.id FROM teachers t 
            JOIN users u ON u.id = t.user_id 
            WHERE u.username = 'alice'
        """)
    
    teacher_id = alice_teacher['id']

    # Access teacher subjects page
    resp = client.get(f'/admin/teachers/{teacher_id}/subjects')
    assert resp.status_code == 200
    assert b'Manage Subjects' in resp.data
    assert b'alice' in resp.data


def test_admin_add_teacher_subject(client):
    """Test admin can add subjects to teachers"""
    # Login as admin
    login(client, 'admin', 'admin')

    # Get alice's teacher id dynamically
    alice_teacher = query_one("""
        SELECT t.id FROM teachers t 
        JOIN users u ON u.id = t.user_id 
        WHERE u.username = 'alice'
    """)
    
    if not alice_teacher:
        # Create teacher record for alice if it doesn't exist
        execute("INSERT INTO teachers (user_id) SELECT id FROM users WHERE username='alice'")
        alice_teacher = query_one("""
            SELECT t.id FROM teachers t 
            JOIN users u ON u.id = t.user_id 
            WHERE u.username = 'alice'
        """)
    
    teacher_id = alice_teacher['id']

    # Add a subject to alice
    resp = client.post(f'/admin/teachers/{teacher_id}/subjects/add', data={'subject_id': '4'})  # History subject
    assert resp.status_code == 302  # Redirect after success

    # Verify subject was added
    subject = query_one(
        "SELECT s.name FROM subjects s JOIN teacher_subjects ts ON ts.subject_id = s.id WHERE ts.teacher_id=%s AND s.id=4",
        (teacher_id,)
    )
    assert subject is not None
    assert subject['name'] == 'History'


def test_admin_remove_teacher_subject(client):
    """Test admin can remove subjects from teachers"""
    # Login as admin
    login(client, 'admin', 'admin')

    # Get alice's teacher id dynamically
    alice_teacher = query_one("""
        SELECT t.id FROM teachers t 
        JOIN users u ON u.id = t.user_id 
        WHERE u.username = 'alice'
    """)
    
    if not alice_teacher:
        # Create teacher record for alice if it doesn't exist
        execute("INSERT INTO teachers (user_id) SELECT id FROM users WHERE username='alice'")
        alice_teacher = query_one("""
            SELECT t.id FROM teachers t 
            JOIN users u ON u.id = t.user_id 
            WHERE u.username = 'alice'
        """)
    
    teacher_id = alice_teacher['id']

    # Remove a subject from alice (assuming Mathematics subject exists)
    resp = client.post(f'/admin/teachers/{teacher_id}/subjects/1/remove')  # Remove Mathematics
    assert resp.status_code == 302  # Redirect after success

    # Verify subject was removed
    subject = query_one(
        "SELECT s.name FROM subjects s JOIN teacher_subjects ts ON ts.subject_id = s.id WHERE ts.teacher_id=%s AND s.id=1",
        (teacher_id,)
    )
    assert subject is None


def test_admin_teacher_subjects_nonexistent_teacher(client):
    """Test admin gets error for nonexistent teacher"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # Try to access nonexistent teacher
    resp = client.get('/admin/teachers/999/subjects')
    assert resp.status_code == 302  # Redirect with error


def test_admin_add_duplicate_teacher_subject(client):
    """Test admin gets error for adding duplicate subject"""
    # Login as admin
    login(client, 'admin', 'admin')
    
    # Try to add subject that teacher already has
    resp = client.post('/admin/teachers/1/subjects/add', data={'subject_id': '1'})  # Mathematics (already assigned)
    assert resp.status_code == 302  # Redirect with error
