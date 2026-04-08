import pytest
from unittest.mock import patch, MagicMock, Mock
from validate_env import (
    validate_export_profile,
    fetch_target_constraints,
    verify_before_apply
)

# Test Fixtures

@pytest.fixture
def valid_export_profile():
    return {
        "profile_id": "prof-123",
        "version": "1.0.0",
        "data": {
            "api_key": "sk_test_1234567890",
            "region": "us-east-1",
            "resource_type": "lambda"
        },
        "metadata": {
            "owner": "dev-team",
            "created_at": "2023-01-01T00:00:00Z"
        }
    }

@pytest.fixture
def valid_constraints():
    return {
        "region": ["us-east-1", "us-west-2"],
        "resource_type": ["lambda", "s3"],
        "required_fields": ["api_key", "region"]
    }

@pytest.fixture
def mock_response():
    return {
        "status_code": 200,
        "json": lambda: {"constraints": {"region": ["us-east-1"], "version": "1.0.0"}}
    }

# Test Cases for validate_export_profile

def test_validate_export_profile_success(valid_export_profile):
    """Test that a valid export profile returns True."""
    result = validate_export_profile(valid_export_profile)
    assert result is True

def test_validate_export_profile_invalid_data(valid_export_profile):
    """Test that profile without required 'data' field fails."""
    invalid_profile = {
        "profile_id": "prof-456",
        "version": "1.0.0",
        "metadata": {}
    }
    result = validate_export_profile(invalid_profile)
    assert result is False

def test_validate_export_profile_empty_input(valid_export_profile):
    """Test that None or empty dict input fails gracefully."""
    result_none = validate_export_profile(None)
    result_empty = validate_export_profile({})
    assert result_none is False
    assert result_empty is False

# Test Cases for fetch_target_constraints

@patch('validate_env.requests.get')
def test_fetch_target_constraints_success(mock_get, mock_response):
    """Test successful retrieval of constraints from API."""
    mock_get.return_value = mock_response
    result = fetch_target_constraints("env-prod-01")
    assert result is not None
    assert "constraints" in result
    mock_get.assert_called_once_with("https://api.target/env/env-prod-01/constraints")

@patch('validate_env.requests.get')
def test_fetch_target_constraints_network_error(mock_get):
    """Test handling of network timeout or connection error."""
    mock_get.side_effect = Exception("Network Error")
    with pytest.raises(Exception, match="Network Error"):
        fetch_target_constraints("env-prod-01")

@patch('validate_env.requests.get')
def test_fetch_target_constraints_invalid_env(mock_get):
    """Test handling of API returning 404 for non-existent environment."""
    mock_response_error = MagicMock()
    mock_response_error.status_code = 404
    mock_response_error.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response_error
    with pytest.raises(Exception):
        fetch_target_constraints("non-existent-env")

# Test Cases for verify_before_apply

def test_verify_before_apply_compatible(valid_export_profile, valid_constraints):
    """Test that profile matches all target constraints successfully."""
    # Mock validation function to assume profile is valid
    with patch('validate_env.validate_export_profile', return_value=True):
        result = verify_before_apply(valid_export_profile, valid_constraints)
        assert result["is_compatible"] is True
        assert result["errors"] == []

def test_verify_before_apply_region_mismatch(valid_export_profile, valid_constraints):
    """Test that profile fails if region is not in allowed list."""
    invalid_constraints = {"region": ["us-west-2"], "resource_type": ["lambda"]}
    result = verify_before_apply(valid_export_profile, invalid_constraints)
    assert result["is_compatible"] is False
    assert "Region mismatch" in str(result.get("errors", []))

def test_verify_before_apply_invalid_profile_format(valid_export_profile, valid_constraints):
    """Test that verification fails if profile structure is corrupted."""
    corrupted_profile = {"invalid_field": "value"}
    with patch('validate_env.validate_export_profile', return_value=False):
        result = verify_before_apply(corrupted_profile, valid_constraints)
        assert result["is_compatible"] is False
        assert "Profile validation failed" in str(result.get("errors", []))

# Integration Test Case

@patch('validate_env.validate_export_profile', return_value=True)
@patch('validate_env.fetch_target_constraints', return_value={"region": ["us-east-1"], "resource_type": ["lambda"]})
def test_full_pipeline_integration(mock_constraints, mock_validate):
    """Test the end-to-end workflow simulation."""
    profile = {"profile_id": "123", "data": {"region": "us-east-1", "type": "lambda"}}
    constraints = {"region": ["us-east-1"]}
    
    result = verify_before_apply(profile, constraints)
    assert result["is_compatible"] is True
    
    mock_validate.assert_called_once_with(profile)
    mock_constraints.assert_not_called()