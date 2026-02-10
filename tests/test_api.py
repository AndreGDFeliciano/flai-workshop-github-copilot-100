"""Tests for the Activities API endpoints"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
    def test_get_activities_has_correct_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_includes_basketball(self, client):
        """Test that Basketball Team is in the activities"""
        response = client.get("/activities")
        data = response.json()
        assert "Basketball Team" in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_valid_activity(self, client):
        """Test successful signup for a valid activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
        
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball Team/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "james@mergington.edu"  # Already in Basketball Team
        
        response = client.post(f"/activities/Basketball Team/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newcoder@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test successful unregistration of an existing participant"""
        email = "james@mergington.edu"  # Existing participant in Basketball Team
        
        response = client.delete(
            f"/activities/Basketball Team/unregister?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes the participant"""
        email = "james@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Basketball Team/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball Team"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant(self, client):
        """Test unregistering a student who is not registered for the activity"""
        email = "notregistered@mergington.edu"
        
        response = client.delete(
            f"/activities/Basketball Team/unregister?email={email}"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        email = "emma@mergington.edu"
        
        response = client.delete(
            f"/activities/Programming%20Class/unregister?email={email}"
        )
        assert response.status_code == 200


class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test complete workflow: get activities, signup, verify, unregister"""
        email = "testworkflow@mergington.edu"
        activity = "Chess Club"
        
        # 1. Get initial activities
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # 2. Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # 3. Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        assert len(data[activity]["participants"]) == initial_count + 1
        
        # 4. Unregister from activity
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # 5. Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]
        assert len(data[activity]["participants"]) == initial_count
    
    def test_cannot_double_signup_then_unregister(self, client):
        """Test that double signup fails but single unregister works"""
        email = "doubletest@mergington.edu"
        activity = "Drama Club"
        
        # First signup should succeed
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Second signup should fail
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        # Unregister should succeed
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Second unregister should fail
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
