"""
tests/test_classifier.py

Tests for the confidence scoring and classification engine.
"""

from pathlib import Path
import pytest
from models.candidate import Candidate
from scanner.classifier import classify, BLACKLISTED_NAMES, NEVER_AUTOSELECT


def test_safe_case(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython311.pyc").write_text("")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    (tmp_path / "requirements.txt").write_text("flask")

    candidate = Candidate(
        path=tmp_path / "__pycache__",
        ecosystem="python",
        category="deletable",
        matched_rule="__pycache__",
    )

    score_value, label = classify(candidate, tmp_path)
    assert label == "safe"
    assert score_value >= 90

def test_blacklisted_returns_ignore(tmp_path):
    (tmp_path / ".env").mkdir()
    candidate = Candidate(
        path=tmp_path / ".env",
        ecosystem="python",
        category="deletable",
        matched_rule=".env",
    )

    score_value, label = classify(candidate, tmp_path)
    assert label == "ignore"
    assert score_value == 0


def test_never_autoselect_capped_at_review(tmp_path):
    (tmp_path / "datasets").mkdir()

    candidate = Candidate(
        path=tmp_path / "datasets",
        ecosystem="python",
        category="deletable",
        matched_rule="datasets",
    )
    score_value, label = classify(candidate, tmp_path)
    assert label in ["review", "ignore"]


def test_unsafe_contents_scores_low(tmp_path):
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "image.jpg").write_text("fake image content")

    candidate = Candidate(
        path=tmp_path / "dist",
        ecosystem="python",
        category="deletable",
        matched_rule="dist",
    )
    score_value, label = classify(candidate, tmp_path)
    assert label == "ignore"


def test_unknown_ecosystem_scores_lower(tmp_path):
    (tmp_path / "some_folder").mkdir()
    candidate = Candidate(
        path=tmp_path / "some_folder",
        ecosystem="unknown",
        category="deletable",
        matched_rule="some_folder",
    )

    score_value_unknown, label_unknown = classify(candidate, tmp_path)
    candidate_known = Candidate(
        path=tmp_path / "some_folder",
        ecosystem="python",
        category="deletable",
        matched_rule="some_folder",
    )
    score_value_known, label_known = classify(candidate_known, tmp_path)
    assert score_value_unknown < score_value_known