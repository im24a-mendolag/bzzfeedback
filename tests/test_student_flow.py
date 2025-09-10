from .conftest import login


def test_student_dashboard_and_submit_feedback(client):
    # Login as seeded student by registering first
    client.post('/logout', follow_redirects=True)
    client.post('/register', data={'username': 'stud1', 'password': 'Passw0rd!', 'password2': 'Passw0rd!'}, follow_redirects=True)

    # View dashboard
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'Choose your teacher' in resp.data

    # Grab first teacher link from dashboard page
    # For simplicity, directly navigate to choose-subject for teacher_id=1
    resp = client.get('/choose-subject/1')
    assert resp.status_code == 200
    assert b'Choose a subject' in resp.data

    # Submit feedback with custom category (required)
    resp = client.post('/submit-feedback', data={
        'teacher_id': '1',
        'subject_id': '1',
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


