"""Tests for envoy.forecast."""

import pytest

from envoy.forecast import (
    ForecastError,
    generate_forecast,
    get_forecast,
    list_forecasts,
    remove_forecast,
)
from envoy.storage import save_manifest


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage._STORE_DIR", tmp_path)
    monkeypatch.setattr("envoy.forecast.get_store_dir", lambda: tmp_path)
    save_manifest(tmp_path, {"alpha": {}, "beta": {}})
    return tmp_path


def test_generate_forecast_returns_record(isolated_store):
    rec = generate_forecast(
        "alpha",
        {"push_count": 10, "pull_count": 5},
        store_dir=isolated_store,
    )
    assert rec["project"] == "alpha"
    assert "predicted_usage_score" in rec
    assert "recommendation" in rec
    assert isinstance(rec["predicted_usage_score"], float)


def test_generate_forecast_persists(isolated_store):
    generate_forecast("alpha", {"push_count": 20}, store_dir=isolated_store)
    stored = get_forecast("alpha", store_dir=isolated_store)
    assert stored is not None
    assert stored["project"] == "alpha"


def test_generate_forecast_missing_project_raises(isolated_store):
    with pytest.raises(ForecastError, match="Unknown project"):
        generate_forecast("nope", {"push_count": 1}, store_dir=isolated_store)


def test_generate_forecast_empty_signals_raises(isolated_store):
    with pytest.raises(ForecastError, match="signals must not be empty"):
        generate_forecast("alpha", {}, store_dir=isolated_store)


def test_generate_forecast_unknown_signal_raises(isolated_store):
    with pytest.raises(ForecastError, match="Unknown signal"):
        generate_forecast("alpha", {"bogus_metric": 5}, store_dir=isolated_store)


def test_get_forecast_missing_returns_none(isolated_store):
    assert get_forecast("alpha", store_dir=isolated_store) is None


def test_list_forecasts_empty_when_none(isolated_store):
    assert list_forecasts(store_dir=isolated_store) == []


def test_list_forecasts_returns_all(isolated_store):
    generate_forecast("alpha", {"push_count": 5}, store_dir=isolated_store)
    generate_forecast("beta", {"pull_count": 3}, store_dir=isolated_store)
    items = list_forecasts(store_dir=isolated_store)
    assert len(items) == 2
    projects = {i["project"] for i in items}
    assert projects == {"alpha", "beta"}


def test_remove_forecast_success(isolated_store):
    generate_forecast("alpha", {"push_count": 8}, store_dir=isolated_store)
    remove_forecast("alpha", store_dir=isolated_store)
    assert get_forecast("alpha", store_dir=isolated_store) is None


def test_remove_forecast_missing_raises(isolated_store):
    with pytest.raises(ForecastError, match="No forecast found"):
        remove_forecast("alpha", store_dir=isolated_store)


def test_high_usage_recommendation(isolated_store):
    rec = generate_forecast(
        "alpha",
        {"push_count": 100, "pull_count": 100, "access_count": 100},
        store_dir=isolated_store,
    )
    assert "high-usage" in rec["recommendation"]


def test_low_usage_recommendation(isolated_store):
    rec = generate_forecast(
        "alpha",
        {"push_count": 0, "pull_count": 0},
        store_dir=isolated_store,
    )
    assert "low-usage" in rec["recommendation"]
