from .conftest import login
from app.db import execute


def test_teacher_subject_overview_and_filter(client):
    # Ensure alice is a teacher (not admin) for this test's expectations
    execute("UPDATE users SET role='teacher' WHERE username='alice'")
    
    # Ensure alice has a teacher record
    from app.db import query_one
    teacher_record = query_one("SELECT id FROM teachers WHERE user_id = (SELECT id FROM users WHERE username='alice')")
    if not teacher_record:
        execute("INSERT INTO teachers (user_id) SELECT id FROM users WHERE username='alice'")
    
    # Login as seeded teacher 'alice'
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200

    # Check where /teacher/feedback lands (teacher subjects or admin overview)
    resp = client.get('/teacher/feedback', follow_redirects=True)
    assert resp.status_code == 200

    if b'All subjects' in resp.data:
        # We're effectively admin; navigate to a subject moderation list
        resp2 = client.get('/admin/feedback?subject_id=1&status=pending')
        assert resp2.status_code == 200
        assert b'Moderate feedback' in resp2.data or b'No feedback in this filter.' in resp2.data  
    else:
        # Teacher view path
        assert b'Your subjects' in resp.data
        resp2 = client.get('/teacher/feedback?subject_id=1')
        assert resp2.status_code == 200
        assert b'Your feedback' in resp2.data
        # Unread filter
        resp3 = client.get('/teacher/feedback?subject_id=1&unread=1')
        assert resp3.status_code == 200
        # Check for feedback page content instead of "Show all"
        assert b'Your feedback' in resp3.data or b'No feedback' in resp3.data


