"""Integration tests for rating module with real storage."""

import pytest
from unittest.mock import patch
from envoy.rating import set_rating, get_rating, remove_rating, list_ratings, RatingError
from envoy.storage import save_manifest


@pytest.fixture
def isolated_store(tmp_path):
    manifest = {"proj-a": "proj-a.env", "proj-b": "proj-b.env"}
    save_manifest(tmp_path, manifest)
    with patch("envoy.rating.get_store_dir", return_value=tmp_path), \
         patch("envoy.rating.load_manifest", return_value=manifest):
        yield tmp_path


def test_rate_and_retrieve(isolated_store):
    set_rating("proj-a", 3, note="decent")
    result = get_rating("proj-a")
    assert result is not None
    assert result["score"] == 3
    assert result["note"] == "decent"


def test_multiple_ratings_independent(isolated_store):
    set_rating("proj-a", 5)
    set_rating("proj-b", 1, note="poor")
    assert get_rating("proj-a")["score"] == 5
    assert get_rating("proj-b")["note"] == "poor"


def test_overwrite_rating(isolated_store):
    set_rating("proj-a", 2)
    set_rating("proj-a", 4, note="improved")
    result = get_rating("proj-a")
    assert result["score"] == 4


def test_remove_and_rerate(isolated_store):
    set_rating("proj-a", 3)
    remove_rating("proj-a")
    assert get_rating("proj-a") is None
    set_rating("proj-a", 5)
    assert get_rating("proj-a")["score"] == 5


def test_list_reflects_all_ratings(isolated_store):
    set_rating("proj-a", 2)
    set_rating("proj-b", 4)
    ratings = list_ratings()
    assert set(ratings.keys()) == {"proj-a", "proj-b"}


def test_invalid_score_does_not_persist(isolated_store):
    with pytest.raises(RatingError):
        set_rating("proj-a", 10)
    assert get_rating("proj-a") is None
