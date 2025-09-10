from .conftest import login


def test_teacher_subject_overview_and_filter(client):
    # Login as seeded teacher 'alice'
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200
    # Overview page
    resp = client.get('/teacher/feedback')
    assert resp.status_code == 200
    assert b'Your subjects' in resp.data

    # Per-subject page
    resp = client.get('/teacher/feedback?subject_id=1')
    assert resp.status_code == 200
    assert b'Your feedback' in resp.data

    # Unread filter
    resp = client.get('/teacher/feedback?subject_id=1&unread=1')
    assert resp.status_code == 200
    assert b'Show all' in resp.data


