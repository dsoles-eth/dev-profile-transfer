import os
import pytest
from unittest.mock import patch, MagicMock
import restore_profile

# Fixtures
@pytest.fixture
def sample_config():
    return {
        "profile_name": "dev_env_v1",
        "variables": {
            "PATH": "/usr/local/bin",
            "APP_NAME": "TestApp",
            "DEBUG_MODE": "true"
        },
        "shell_commands": ["export HELLO=world", "alias test='echo success'"]
    }