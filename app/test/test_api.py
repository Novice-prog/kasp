import asyncio
from io import BytesIO
import os

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile
from fastapi.responses import FileResponse
from starlette.requests import Request

from app.api import report_routes


class DummyTaskResult:
    def __init__(self, task_id: str):
        self.id = task_id


class DummyProcessFile:
    def delay(self, _file_path: str):
        return DummyTaskResult("test-task-id")


def make_request():
    return Request({"type": "http", "method": "POST", "path": "/", "headers": []})


def test_upload_file_success(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    monkeypatch.setattr(report_routes, "UPLOAD_DIR", str(upload_dir))
    monkeypatch.setattr(report_routes, "process_file", DummyProcessFile())

    upload = UploadFile(filename="test.txt", file=BytesIO("житель".encode("utf-8")))
    response = asyncio.run(report_routes.upload_file(request=make_request(), file=upload))

    assert "task_id" in response
    assert response["task_id"] == "test-task-id"


def test_upload_file_invalid_extension():
    upload = UploadFile(filename="test.csv", file=BytesIO("x".encode("utf-8")))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(report_routes.upload_file(request=make_request(), file=upload))

    assert exc.value.status_code == 400


def test_upload_file_empty_filename():
    upload = UploadFile(filename="", file=BytesIO("x".encode("utf-8")))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(report_routes.upload_file(request=make_request(), file=upload))

    assert exc.value.status_code == 400


class StubAsyncResultPending:
    status = "PENDING"


class StubAsyncResultStarted:
    status = "STARTED"


class StubAsyncResultFailure:
    status = "FAILURE"
    result = RuntimeError("boom")


class StubAsyncResultSuccess:
    status = "SUCCESS"
    result = {"file": "results/x.xlsx"}

    def ready(self):
        return True


def test_get_status_pending(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubAsyncResultPending())
    response = asyncio.run(report_routes.get_status("id-1"))
    assert response == {"status": "pending"}


def test_get_status_started(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubAsyncResultStarted())
    response = asyncio.run(report_routes.get_status("id-1"))
    assert response == {"status": "processing"}


def test_get_status_failure(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubAsyncResultFailure())
    response = asyncio.run(report_routes.get_status("id-1"))
    assert response["status"] == "failed"
    assert "boom" in response["error"]


def test_get_status_success(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubAsyncResultSuccess())
    response = asyncio.run(report_routes.get_status("id-1"))
    assert response == {"status": "done", "result": {"file": "results/x.xlsx"}}


class StubDownloadNotReady:
    status = "PENDING"

    def ready(self):
        return False


class StubDownloadFailed:
    status = "FAILURE"

    def ready(self):
        return True


class StubDownloadSuccess:
    status = "SUCCESS"

    def __init__(self, file_path):
        self.result = {"file": file_path}

    def ready(self):
        return True


def test_download_not_ready(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubDownloadNotReady())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(report_routes.download("id-1"))

    assert exc.value.status_code == 400


def test_download_failed(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubDownloadFailed())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(report_routes.download("id-1"))

    assert exc.value.status_code == 400


def test_download_file_missing(monkeypatch):
    monkeypatch.setattr(report_routes, "AsyncResult", lambda *_args, **_kwargs: StubDownloadSuccess("no_such_file.xlsx"))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(report_routes.download("id-1"))

    assert exc.value.status_code == 404


def test_download_success(monkeypatch, tmp_path):
    ready_file = tmp_path / "report.xlsx"
    ready_file.write_bytes(b"test")

    monkeypatch.setattr(
        report_routes,
        "AsyncResult",
        lambda *_args, **_kwargs: StubDownloadSuccess(str(ready_file))
    )

    response = asyncio.run(report_routes.download("id-1"))
    assert isinstance(response, FileResponse)
