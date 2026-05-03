"""Shared pytest fixtures for the VoteWise India test suite.

This conftest.py is discovered automatically by pytest and provides
reusable fixtures across test_api.py, test_rules.py, and test_safety.py.

Example:
    Run the full test suite::

        pytest tests/ -v --tb=short
"""
from __future__ import annotations

import sys
import os

# Ensure both the repo root and the functions/ package are importable.
# This mirrors the PYTHONPATH=.:functions set in the CI workflow.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_functions_dir = os.path.join(_repo_root, "functions")
for _p in (_repo_root, _functions_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Firestore mock fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_db():
    """Return a MagicMock that mimics the Firestore client interface.

    Provides pre-configured return values for the common
    collection -> document -> get / set / update chain.

    Returns:
        unittest.mock.MagicMock: Mock Firestore client.
    """
    db = MagicMock()
    doc_snapshot = MagicMock()
    doc_snapshot.exists = False
    doc_ref = MagicMock()
    doc_ref.get.return_value = doc_snapshot
    db.collection.return_value.document.return_value = doc_ref
    return db


# ---------------------------------------------------------------------------
# Sample request payload fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def basic_chat_payload() -> dict:
    """Return a minimal valid /chat request payload.

    Returns:
        dict: JSON-serialisable request body.
    """
    return {
        "message": "How do I register to vote?",
        "state": "DL",
        "language": "English",
        "history": [],
    }


@pytest.fixture()
def long_message_payload() -> dict:
    """Return a /chat payload whose message exceeds the 500-char server limit.

    Returns:
        dict: JSON-serialisable request body with an oversized message.
    """
    return {
        "message": "x" * 501,
        "state": "MH",
        "language": "English",
        "history": [],
    }


@pytest.fixture()
def partisan_payload() -> dict:
    """Return a /chat payload containing a partisan keyword that must be refused.

    Returns:
        dict: JSON-serialisable request body with forbidden content.
    """
    return {
        "message": "Which party should I vote for BJP or Congress?",
        "state": "UP",
        "language": "English",
        "history": [],
    }
