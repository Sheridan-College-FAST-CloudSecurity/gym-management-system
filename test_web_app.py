import pytest
from web_app import app, calculate_membership_fee
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test if home route returns successful response"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Gym Management System" in response.data  # Match your actual page title

def test_members_route(client):
    """Test members listing page"""
    response = client.get('/members')
    assert response.status_code == 200
    assert b"Members" in response.data  # Check for heading in your template

def test_api_get_member(client):
    """Test API endpoint for getting member data"""
    # First add a test member through the form
    response = client.post('/members/add', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'membership_type': 'Monthly'
    }, follow_redirects=True)
    
    # Now test the API endpoint
    response = client.get('/api/members')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(member['email'] == 'test@example.com' for member in response.json)

def test_calculate_membership_fee():
    """Test membership fee calculation"""
    # Update these assertions to match your actual rates
    assert calculate_membership_fee("Monthly") == 30
    assert calculate_membership_fee("Quarterly") == 80
    assert calculate_membership_fee("Annual") == 300