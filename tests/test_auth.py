from .conftest import login, register


def test_login_success(client):
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200
    # Alice is seeded as a teacher, so should see "Your subjects" or admin subjects
    assert b'Your subjects' in resp.data or b'All subjects' in resp.data


def test_login_fail(client):
    resp = login(client, 'alice', 'wrong')
    assert resp.status_code == 200
    assert b'Invalid credentials' in resp.data


def test_register_student_then_login(client):
    resp = register(client, 'newstudent', 'Secret123!')
    assert resp.status_code == 200
    # Should land on dashboard
    assert b'Dashboard' in resp.data
    # Logout then login again
    resp = client.post('/logout', follow_redirects=True)
    assert resp.status_code == 200
    resp = login(client, 'newstudent', 'Secret123!')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


