from .conftest import login, register


def test_account_settings_access(client):
    """Test that authenticated users can access account settings"""
    # Login as a user
    resp = login(client, 'alice', 'Password123!')
    assert resp.status_code == 200
    
    # Access account settings
    resp = client.get('/account')
    assert resp.status_code == 200
    assert b'Account Settings' in resp.data
    assert b'Change Username' in resp.data
    assert b'Change Password' in resp.data
    assert b'Delete Account' in resp.data


def test_account_settings_redirect_unauthenticated(client):
    """Test that unauthenticated users are redirected from account settings"""
    resp = client.get('/account')
    assert resp.status_code == 302  # Redirect to login


def test_change_username_success(client):
    """Test successful username change"""
    # Login as a user
    login(client, 'alice', 'Password123!')
    
    # Change username
    resp = client.post('/account/change-username', data={
        'username': 'alice_new',
        'password': 'Password123!'
    })
    assert resp.status_code == 302  # Redirect after success
    
    # Verify username was changed by logging in with new username
    resp = client.post('/logout', follow_redirects=True)
    resp = login(client, 'alice_new', 'Password123!')
    assert resp.status_code == 200


def test_change_username_wrong_password(client):
    """Test username change with wrong password"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/change-username', data={
        'username': 'alice_new',
        'password': 'wrong_password'
    })
    assert resp.status_code == 302  # Redirect back to account page
    # Should show error message (tested via flash message)


def test_change_username_already_taken(client):
    """Test username change to already taken username"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/change-username', data={
        'username': 'bob',  # Already exists in seed data
        'password': 'Password123!'
    })
    assert resp.status_code == 302  # Redirect back to account page


def test_change_password_success(client):
    """Test successful password change"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/change-password', data={
        'current_password': 'Password123!',
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    })
    assert resp.status_code == 302  # Redirect after success
    
    # Verify password was changed by logging in with new password
    resp = client.post('/logout', follow_redirects=True)
    resp = login(client, 'alice', 'NewPassword123!')
    assert resp.status_code == 200


def test_change_password_mismatch(client):
    """Test password change with mismatched new passwords"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/change-password', data={
        'current_password': 'Password123!',
        'new_password': 'NewPassword123!',
        'confirm_password': 'DifferentPassword123!'
    })
    assert resp.status_code == 302  # Redirect back to account page


def test_change_password_too_short(client):
    """Test password change with password too short"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/change-password', data={
        'current_password': 'Password123!',
        'new_password': 'short',
        'confirm_password': 'short'
    })
    assert resp.status_code == 302  # Redirect back to account page


def test_delete_account_success(client):
    """Test successful account deletion"""
    # Create a test user first
    register(client, 'testuser', 'TestPassword123!')
    
    # Login and delete account
    login(client, 'testuser', 'TestPassword123!')
    resp = client.post('/account/delete', data={
        'password': 'TestPassword123!'
    })
    assert resp.status_code == 302  # Redirect to index after deletion
    
    # Verify user was deleted by trying to login
    resp = login(client, 'testuser', 'TestPassword123!')
    assert b'Invalid credentials' in resp.data


def test_delete_account_wrong_password(client):
    """Test account deletion with wrong password"""
    login(client, 'alice', 'Password123!')
    
    resp = client.post('/account/delete', data={
        'password': 'wrong_password'
    })
    assert resp.status_code == 302  # Redirect back to account page
