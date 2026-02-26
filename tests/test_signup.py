"""Tests for the POST /activities/{activity_name}/signup endpoint"""

import pytest


class TestSignupHappyPath:
    """Happy path tests for successful signup"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup to an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newemail@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_persists_in_activity_list(self, client, reset_activities):
        """Test that signup persists and appears in activity list"""
        # Sign up a student
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Fetch activities and verify student is in the list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        assert "newstudent@mergington.edu" in activities["Programming Class"]["participants"]
    
    def test_signup_to_activity_with_availability(self, client, reset_activities):
        """Test signup succeeds when activity has available spots"""
        response = client.post(
            "/activities/Gym%20Class/signup?email=available@mergington.edu"
        )
        
        assert response.status_code == 200
    
    def test_signup_to_activity_close_to_capacity(self, client, reset_activities):
        """Test signup succeeds when activity has exactly one spot left"""
        # Get Tennis Club which has max 10 and 1 participant (9 spots left)
        response = client.post(
            "/activities/Tennis%20Club/signup?email=spot9@mergington.edu"
        )
        assert response.status_code == 200
        
        response = client.post(
            "/activities/Tennis%20Club/signup?email=spot10@mergington.edu"
        )
        assert response.status_code == 200


class TestSignupErrors:
    """Error handling tests for signup"""
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_enrolled(self, client, reset_activities):
        """Test signup fails if student is already enrolled"""
        # Try to sign up as someone already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_to_full_activity(self, client, reset_activities):
        """Test signup fails when activity is at maximum capacity"""
        # Art Studio has max 18 participants, let's fill it up
        # Currently has 2 participants (maya, lucas), need to add 16 more to fill it
        for i in range(16):
            response = client.post(
                f"/activities/Art%20Studio/signup?email=filler{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Now try to sign up one more - should fail with capacity error
        response = client.post(
            "/activities/Art%20Studio/signup?email=overflow@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "maximum capacity" in data["detail"]
    
    def test_signup_missing_email_parameter(self, client, reset_activities):
        """Test signup fails when email parameter is missing"""
        response = client.post("/activities/Chess%20Club/signup")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_case_sensitive_activity_name(self, client, reset_activities):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess%20club/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404


class TestSignupEdgeCases:
    """Edge case tests for signup"""
    
    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup works with special characters in activity name (with URL encoding)"""
        # All activities have spaces, which are encoded as %20
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 200
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students can sign up for same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Gym%20Class/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for email in emails:
            assert email in activities["Gym Class"]["participants"]
    
    def test_signup_email_with_plus_sign(self, client, reset_activities):
        """Test signup works with valid email formats like plus addressing"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student+tag@mergington.edu"
        )
        
        assert response.status_code == 200
    
    def test_signup_sequential_spots_filling(self, client, reset_activities):
        """Test filling activity to exact capacity and verifying cap enforcement"""
        # Tennis Club: max 10, currently has 1 participant (jessica@mergington.edu)
        # Need to add 9 more to reach capacity
        
        for i in range(9):
            response = client.post(
                f"/activities/Tennis%20Club/signup?email=player{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Should be at capacity now
        activities_response = client.get("/activities")
        tennis_participants = activities_response.json()["Tennis Club"]["participants"]
        assert len(tennis_participants) == 10
        
        # Next signup should fail
        response = client.post(
            "/activities/Tennis%20Club/signup?email=over@mergington.edu"
        )
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]


class TestSignupDataIntegrity:
    """Tests to ensure data integrity after signup"""
    
    def test_participant_list_updated_correctly(self, client, reset_activities):
        """Test that participant list is updated correctly after signup"""
        email = "integrity@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Programming%20Class/signup?email=" + email
        )
        
        # Get updated count
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        
        assert new_count == initial_count + 1
    
    def test_other_activities_not_affected_by_signup(self, client, reset_activities):
        """Test that signing up for one activity doesn't affect others"""
        # Get initial state of all activities
        response = client.get("/activities")
        initial_counts = {
            name: len(data["participants"])
            for name, data in response.json().items()
        }
        
        # Sign up for one activity
        client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        
        # Check that only Chess Club was affected
        response = client.get("/activities")
        new_counts = {
            name: len(data["participants"])
            for name, data in response.json().items()
        }
        
        for activity_name in initial_counts:
            if activity_name == "Chess Club":
                assert new_counts[activity_name] == initial_counts[activity_name] + 1
            else:
                assert new_counts[activity_name] == initial_counts[activity_name]
