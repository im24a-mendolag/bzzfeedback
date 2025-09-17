import pytest
from .conftest import login


def test_student_dashboard_and_submit_feedback(client):
    # Login as seeded student by registering first
    client.post('/logout', follow_redirects=True)
    client.post('/register', data={'username': 'stud1', 'password': 'Passw0rd!', 'password2': 'Passw0rd!'}, follow_redirects=True)

    # View dashboard
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'Choose your teacher' in resp.data

    # Get the first available teacher ID from the database
    from app.db import query_one
    teacher = query_one("SELECT id FROM teachers LIMIT 1")
    if not teacher:
        # If no teachers exist, skip this test
        pytest.skip("No teachers available for testing")
    
    teacher_id = teacher['id']
    
    # Navigate to choose-subject for the available teacher
    resp = client.get(f'/choose-subject/{teacher_id}')
    assert resp.status_code == 200
    assert b'Choose a subject' in resp.data

    # Get the first available subject for this teacher
    subject = query_one("""
        SELECT s.id FROM subjects s 
        JOIN teacher_subjects ts ON ts.subject_id = s.id 
        WHERE ts.teacher_id = %s 
        LIMIT 1
    """, (teacher_id,))
    
    if not subject:
        # If no subjects assigned to teacher, skip this test
        pytest.skip("No subjects assigned to teacher for testing")
    
    subject_id = subject['id']

    # Submit feedback with custom category (required)
    resp = client.post('/submit-feedback', data={
        'teacher_id': str(teacher_id),
        'subject_id': str(subject_id),
        'category_id': '__custom__',
        'custom_category': 'TestCat',
        'title': 'Test Title',
        'info': 'This is test feedback.'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Feedback submitted' in resp.data

    # Check my feedback
    resp = client.get('/my-feedback')
    assert resp.status_code == 200
    assert b'Test Title' in resp.data
    # Pending moderation badge should be visible
    assert b'Waiting for validation' in resp.data


