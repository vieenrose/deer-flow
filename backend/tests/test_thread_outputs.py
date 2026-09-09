"""Tests for GET /api/threads/{thread_id}/outputs (thread_runs router)."""

from pathlib import Path

from app.gateway.routers import thread_runs


class _FakePaths:
    def __init__(self, root: Path):
        self._root = root

    def sandbox_outputs_dir(self, thread_id: str, *, user_id=None) -> Path:
        return self._root / thread_id / "user-data" / "outputs"


def test_list_thread_output_files(tmp_path, monkeypatch):
    outdir = tmp_path / "t1" / "user-data" / "outputs"
    outdir.mkdir(parents=True)
    (outdir / "report.md").write_text("# report")
    (outdir / "data.csv").write_text("a,b\n1,2\n")

    monkeypatch.setattr(thread_runs, "get_paths", lambda: _FakePaths(tmp_path))

    result = thread_runs._list_thread_output_files("t1", "default")

    assert result["count"] == 2
    by_name = {f["filename"]: f for f in result["files"]}
    assert by_name["report.md"]["size"] > 0
    assert by_name["data.csv"]["path"] == "user-data/outputs/data.csv"


def test_list_thread_output_files_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(thread_runs, "get_paths", lambda: _FakePaths(tmp_path))

    result = thread_runs._list_thread_output_files("nope", "default")

    assert result == {"files": [], "count": 0}
