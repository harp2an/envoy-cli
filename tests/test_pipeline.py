"""Tests for envoy.pipeline."""
import pytest

from envoy.pipeline import (
    PipelineError,
    create_pipeline,
    delete_pipeline,
    get_pipeline,
    list_pipelines,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.pipeline.get_store_dir", lambda: tmp_path)
    return tmp_path


def test_create_and_get_pipeline(isolated_store):
    create_pipeline("deploy", ["lint", "push"], store_dir=isolated_store)
    steps = get_pipeline("deploy", store_dir=isolated_store)
    assert steps == ["lint", "push"]


def test_create_pipeline_empty_name_raises(isolated_store):
    with pytest.raises(PipelineError, match="empty"):
        create_pipeline("", ["push"], store_dir=isolated_store)


def test_create_pipeline_no_steps_raises(isolated_store):
    with pytest.raises(PipelineError, match="at least one step"):
        create_pipeline("empty", [], store_dir=isolated_store)


def test_create_pipeline_invalid_step_raises(isolated_store):
    with pytest.raises(PipelineError, match="Unknown step"):
        create_pipeline("bad", ["push", "explode"], store_dir=isolated_store)


def test_get_pipeline_missing_raises(isolated_store):
    with pytest.raises(PipelineError, match="not found"):
        get_pipeline("ghost", store_dir=isolated_store)


def test_list_pipelines_empty(isolated_store):
    assert list_pipelines(store_dir=isolated_store) == {}


def test_list_pipelines_multiple(isolated_store):
    create_pipeline("ci", ["lint", "validate", "push"], store_dir=isolated_store)
    create_pipeline("nightly", ["snapshot", "rotate"], store_dir=isolated_store)
    result = list_pipelines(store_dir=isolated_store)
    assert set(result.keys()) == {"ci", "nightly"}
    assert result["ci"] == ["lint", "validate", "push"]


def test_delete_pipeline_success(isolated_store):
    create_pipeline("tmp", ["pull"], store_dir=isolated_store)
    delete_pipeline("tmp", store_dir=isolated_store)
    assert "tmp" not in list_pipelines(store_dir=isolated_store)


def test_delete_pipeline_missing_raises(isolated_store):
    with pytest.raises(PipelineError, match="not found"):
        delete_pipeline("nope", store_dir=isolated_store)


def test_create_pipeline_overwrites_existing(isolated_store):
    create_pipeline("ci", ["lint"], store_dir=isolated_store)
    create_pipeline("ci", ["push", "snapshot"], store_dir=isolated_store)
    assert get_pipeline("ci", store_dir=isolated_store) == ["push", "snapshot"]


def test_create_pipeline_all_valid_steps(isolated_store):
    all_steps = ["push", "pull", "rotate", "snapshot", "lint", "validate"]
    create_pipeline("full", all_steps, store_dir=isolated_store)
    assert get_pipeline("full", store_dir=isolated_store) == all_steps
