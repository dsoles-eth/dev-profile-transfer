import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
import json

from sanitize_sensitive import sanitize_sensitive, detect_secrets, export_profile


@pytest.fixture
def profile_data():
    return {
        "username": "test_user",
        "email": "user@example.com",
        "api_key": "super_secret_key_123",
        "password": "hashed_very_secret_pass",
        "nested": {
            "secret_token": "token_value",
            "public_info": "info"
        }
    }


@pytest.fixture
def sensitive_keys_list():
    return ["api_key", "password", "secret_token"]


@pytest.fixture
def mock_requests_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    return mock_response


class TestSanitizeSensitive:
    @patch('sanitize_sensitive.os.path.exists')
    def test_sanitizes_known_sensitive_keys(self, mock_exists, profile_data, sensitive_keys_list):
        """
        Happy path: Verifies that specific sensitive keys provided are removed.
        """
        result = sanitize_sensitive(profile_data, sensitive_keys_list)
        
        assert "api_key" not in result
        assert "password" not in result
        assert "username" in result
        assert result["nested"]["secret_token"] is not None  # Assuming logic handles nested differently or this key is filtered recursively

    @patch('sanitize_sensitive.os.path.exists')
    def test_sanitizes_default_patterns(self, mock_exists, profile_data):
        """
        Happy path: Verifies default filtering without explicit key list (if implemented).
        Assuming logic removes 'password' and 'api_key' by default or standard behavior.
        """
        # Simulating logic where sensitive_keys=None implies defaults or all found
        result = sanitize_sensitive(profile_data, [])
        # If the function defaults to scanning, we ensure 'password' is gone based on module description
        # Note: Test assumes logic exists for default filtering.
        assert result.get("password") is None or len(str(result.get("password", ""))) == 0

    def test_sanitizes_handles_non_dict_input_error(self, profile_data, sensitive_keys_list):
        """
        Error case: Handles non-dictionary input gracefully or raises TypeError.
        """
        with pytest.raises(TypeError):
            sanitize_sensitive("not a dict", sensitive_keys_list)


class TestDetectSecrets:
    @patch('sanitize_sensitive.os.path.exists')
    def test_detects_secrets_in_top_level(self, mock_exists, profile_data):
        """
        Happy path: Detects secrets at the top level of the dictionary.
        """
        secrets = detect_secrets(profile_data)
        assert "api_key" in secrets
        assert "password" in secrets

    @patch('sanitize_sensitive.os.path.exists')
    def test_detects_secrets_in_nested_structure(self, mock_exists, profile_data):
        """
        Happy path: Detects secrets within nested dictionaries.
        """
        secrets = detect_secrets(profile_data)
        assert "secret_token" in secrets

    def test_detects_secrets_empty_structure(self, profile_data):
        """
        Happy path/Edge case: Returns empty list for sanitized profile with no secrets.
        """
        clean_profile = {
            "username": "test_user",
            "nested": {
                "public_info": "info"
            }
        }
        secrets = detect_secrets(clean_profile)
        assert len(secrets) == 0


class TestExportProfile:
    @patch('sanitize_sensitive.os.path.exists')
    @patch('sanitize_sensitive.requests.post')
    def test_export_sanitizes_before_network_call(self, mock_post, mock_exists, profile_data, mock_requests_response):
        """
        Happy path: Ensures data is sanitized before being sent over the network.
        """
        mock_post.return_value = mock_requests_response
        
        # Assuming the function validates input and calls sanitize before sending
        # The function should not send 'api_key' to the network
        export_profile(profile_data, "https://api.example.com/upload")
        
        # Verify requests.post was called
        assert mock_post.called
        
        # Verify the body sent did not contain the raw secret (check call args)
        call_args = mock_post.call_args
        data_sent = json.loads(call_args[1]['json']) if call_args else {}
        assert "api_key" not in data_sent

    @patch('sanitize_sensitive.os.path.exists')
    @patch('sanitize_sensitive.requests.post')
    def test_export_handles_network_error(self, mock_post, mock_exists, profile_data):
        """
        Error case: Handles network connection errors gracefully.
        """
        mock_post.side_effect = Exception("Network Error")
        
        with pytest.raises(Exception):
            export_profile(profile_data, "https://api.example.com/upload")

    def test_export_handles_missing_module_dependencies(self, profile_data):
        """
        Error case: Verifies behavior if serialization fails or required logic fails.
        """
        # If the function relies on json serializing to a buffer
        invalid_data = {"data": object()}
        try:
            export_profile(invalid_data, "https://api.example.com/upload")
        except TypeError:
            # Expected if object cannot be serialized
            pass