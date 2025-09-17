from .conftest import login


def test_admin_moderation_flow(client):
    # Promote alice to admin for the test
    # Note: in a real suite you'd isolate users, but here reuse seeded user
    from app.db import execute
    execute("UPDATE users SET role='admin' WHERE username='alice'")

    # Login as alice (now admin)
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200

    # Overview
    resp = client.get('/admin/feedback')
    assert resp.status_code == 200
    assert b'All subjects' in resp.data

    # List pending for subject 1
    resp = client.get('/admin/feedback?subject_id=1&status=pending')
    assert resp.status_code == 200
    # Approve/reject buttons shown for pending
    assert b'Approve' in resp.data or b'No feedback in this filter.' in resp.data


