import os

import pytest

from app.tasks import report_tasks


def test_process_file_success(monkeypatch, tmp_path):
    called = {"cleanup": False}

    def fake_cleanup():
        called["cleanup"] = True

    def fake_process_text(_file_path):
        return {"житель": {"total": 1, "per_line": {0: 1}}}

    def fake_create_excel(_stats, output_path):
        with open(output_path, "wb") as f:
            f.write(b"xlsx")

    input_file = tmp_path / "input.txt"
    input_file.write_text("житель")

    monkeypatch.chdir(tmp_path)
    os.makedirs("results", exist_ok=True)
    monkeypatch.setattr(report_tasks, "cleanup_results", fake_cleanup)
    monkeypatch.setattr(report_tasks, "process_text", fake_process_text)
    monkeypatch.setattr(report_tasks, "create_excel", fake_create_excel)

    result = report_tasks.process_file(str(input_file))

    assert called["cleanup"] is True
    assert "file" in result
    assert os.path.exists(result["file"])
    assert not input_file.exists()


def test_process_file_failure(monkeypatch, tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("житель")

    monkeypatch.setattr(report_tasks, "cleanup_results", lambda: None)
    monkeypatch.setattr(report_tasks, "process_text", lambda _p: (_ for _ in ()).throw(ValueError("bad input")))

    with pytest.raises(ValueError):
        report_tasks.process_file(str(input_file))
