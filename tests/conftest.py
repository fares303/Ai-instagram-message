"""
Pytest configuration file.
"""

import os
import sys
import pytest

# Add the parent directory to sys.path to allow importing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_message():
    """
    Return a sample message dictionary.
    """
    return {
        "sender": "test_user",
        "timestamp": 1609459200000,  # 2021-01-01 00:00:00 UTC
        "content": "Hello, world! 😊",
        "reactions": [
            {
                "reaction": "❤️",
                "actor": "other_user"
            }
        ],
        "photos": ["photo1.jpg"],
        "videos": [],
        "audio": []
    }

@pytest.fixture
def sample_messages():
    """
    Return a list of sample messages.
    """
    return [
        {
            "sender": "test_user",
            "timestamp": 1609459200000,  # 2021-01-01 00:00:00 UTC
            "content": "Hello, world! 😊",
            "reactions": [],
            "photos": [],
            "videos": [],
            "audio": []
        },
        {
            "sender": "other_user",
            "timestamp": 1609459260000,  # 2021-01-01 00:01:00 UTC
            "content": "Hi there! 👋",
            "reactions": [],
            "photos": [],
            "videos": [],
            "audio": []
        }
    ]
