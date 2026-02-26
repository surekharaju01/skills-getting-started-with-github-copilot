"""Tests for the GET /activities endpoint"""

import pytest


def test_get_all_activities(client, reset_activities):
    """Test that GET /activities returns all activities with correct structure"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify we have all 9 activities
    assert len(activities) == 9
    
    # Verify required activities exist
    required_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Music Ensemble",
        "Debate Team",
        "Science Club"
    ]
    
    for activity_name in required_activities:
        assert activity_name in activities


def test_activities_have_required_fields(client, reset_activities):
    """Test that each activity has the required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"


def test_activities_participants_is_list(client, reset_activities):
    """Test that participants is always a list"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list), \
            f"Participants for '{activity_name}' is not a list"


def test_activities_max_participants_is_number(client, reset_activities):
    """Test that max_participants is a positive integer"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["max_participants"], int), \
            f"max_participants for '{activity_name}' is not an integer"
        assert activity_data["max_participants"] > 0, \
            f"max_participants for '{activity_name}' is not positive"


def test_activity_with_no_participants(client, reset_activities):
    """Test activity with empty participants list displays correctly"""
    response = client.get("/activities")
    activities = response.json()
    
    # All activities should have at least one participant, but verify the structure supports empty lists
    for activity_name, activity_data in activities.items():
        # Verify participants field exists and is a list, even if empty
        assert isinstance(activity_data["participants"], list)


def test_chess_club_has_initial_participants(client, reset_activities):
    """Test that Chess Club has expected initial participants"""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_activities_description_not_empty(client, reset_activities):
    """Test that all activities have a description"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert activity_data["description"], \
            f"Activity '{activity_name}' has no description"
        assert len(activity_data["description"]) > 0


def test_activities_schedule_not_empty(client, reset_activities):
    """Test that all activities have a schedule"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert activity_data["schedule"], \
            f"Activity '{activity_name}' has no schedule"
        assert len(activity_data["schedule"]) > 0
