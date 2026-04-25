"""Tests for envoy/rating.py"""

import pytest
from unittest.mock import patch
from envoy.rating import set_rating, get_rating, remove_rating, list_ratings, RatingError


@pytest.fixture
def isolated_store(tmp_path):
    manifest = {"alpha": "alpha.env", "beta": "beta.env"}
    with patch("envoy.rating.get_store_dir", return_value=tmp_path), \
         patch("envoy.rating.load_manifest", return_value=manifest):
        yield tmp_path


def test_set_rating_persists(isolated_store):
    entry = set_rating("alpha", 4)
    assert entry["score"] == 4
    assert entry["note"] == ""
    result = get_rating("alpha")
    assert result["score"] == 4


def test_set_rating_with_note(isolated_store):
    entry = set_rating("alpha", 5, note="excellent")
    assert entry["note"] == "excellent"
    assert get_rating("alpha")["note"] == "excellent"


def test_set_rating_overwrites_existing(isolated_store):
    set_rating("alpha", 3)
    set_rating("alpha", 5, note="updated")
    result = get_rating("alpha")
    assert result["score"] == 5
    assert result["note"] == "updated"


def test_set_rating_invalid_score_raises(isolated_store):
    with pytest.raises(RatingError, match="Score must be one of"):
        set_rating("alpha", 6)


def test_set_rating_zero_score_raises(isolated_store):
    with pytest.raises(RatingError):
        set_rating("alpha", 0)


def test_set_rating_missing_project_raises(isolated_store):
    with pytest.raises(RatingError, match="not found"):
        set_rating("ghost", 3)


def test_get_rating_missing_returns_none(isolated_store):
    assert get_rating("alpha") is None


def test_remove_rating_success(isolated_store):
    set_rating("alpha", 2)
    remove_rating("alpha")
    assert get_rating("alpha") is None


def test_remove_rating_missing_raises(isolated_store):
    with pytest.raises(RatingError, match="No rating found"):
        remove_rating("alpha")


def test_list_ratings_empty(isolated_store):
    assert list_ratings() == {}


def test_list_ratings_multiple(isolated_store):
    set_rating("alpha", 3)
    set_rating("beta", 5, note="top")
    ratings = list_ratings()
    assert len(ratings) == 2
    assert ratings["alpha"]["score"] == 3
    assert ratings["beta"]["note"] == "top"
