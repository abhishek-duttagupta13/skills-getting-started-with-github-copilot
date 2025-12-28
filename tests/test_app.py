import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Debate Club": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lily@mergington.edu"]
        },
        "Basketball": {
            "description": "Team basketball practice and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["tyler@mergington.edu"]
        },
        "Soccer": {
            "description": "Outdoor soccer training and matches",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Stage performances and theatrical productions",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture instruction",
            "schedule": "Saturdays, 1:00 PM - 3:00 PM",
            "max_participants": 12,
            "participants": ["rachel@mergington.edu", "noah@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
        assert "Debate Club" in activities
        assert "Science Olympiad" in activities
    
    def test_get_activity_structure(self, client):
        """Test that activity objects have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        debate_club = activities["Debate Club"]
        assert "description" in debate_club
        assert "schedule" in debate_club
        assert "max_participants" in debate_club
        assert "participants" in debate_club
        assert isinstance(debate_club["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Debate Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post("/activities/Debate Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Debate Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # alex@mergington.edu is already in Debate Club
        response = client.post(
            "/activities/Debate Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_same_student_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        # alex is already in Debate Club, sign them up for another
        response = client.post(
            "/activities/Chess Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify they're in both activities
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" in activities["Debate Club"]["participants"]
        assert "alex@mergington.edu" in activities["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successfully(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Debate Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post("/activities/Debate Club/unregister?email=alex@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" not in activities["Debate Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister for student not registered returns 400"""
        response = client.post(
            "/activities/Debate Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregister when activity has multiple participants"""
        # Science Olympiad has james@mergington.edu and lily@mergington.edu
        response = client.post(
            "/activities/Science Olympiad/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify james is removed but lily remains
        response = client.get("/activities")
        activities = response.json()
        assert "james@mergington.edu" not in activities["Science Olympiad"]["participants"]
        assert "lily@mergington.edu" in activities["Science Olympiad"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
