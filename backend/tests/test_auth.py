"""
Authentication Tests
"""
import pytest
import json
from app import create_app
from app.extensions import db
from app.models import Admin


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def init_database(app):
    """Initialize test database."""
    with app.app_context():
        db.create_all()
        
        # Create test admin
        admin = Admin(
            username='testadmin',
            email='test@example.com',
            is_active=True
        )
        admin.password = 'testpassword123'
        
        db.session.add(admin)
        db.session.commit()
        
        yield db
        
        db.drop_all()


def test_login_success(client, init_database):
    """Test successful admin login."""
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'username_or_email': 'testadmin',
                              'password': 'testpassword123'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'admin' in data
    assert data['admin']['username'] == 'testadmin'


def test_login_invalid_credentials(client, init_database):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'username_or_email': 'testadmin',
                              'password': 'wrongpassword'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_login_missing_credentials(client, init_database):
    """Test login with missing credentials."""
    response = client.post('/api/auth/login',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_protected_route_without_token(client, init_database):
    """Test accessing protected route without token."""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401


def test_protected_route_with_token(client, init_database):
    """Test accessing protected route with valid token."""
    # First, login to get token
    login_response = client.post('/api/auth/login',
                               data=json.dumps({
                                   'username_or_email': 'testadmin',
                                   'password': 'testpassword123'
                               }),
                               content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # Then use token to access protected route
    response = client.get('/api/auth/profile',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'admin' in data
    assert data['admin']['username'] == 'testadmin'