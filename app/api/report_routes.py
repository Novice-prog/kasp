import os
from uuid import uuid4
from celery.result import AsyncResult
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse

from app.core.celery_app import celery_app
from app.core.rate_limit import limiter
from app.tasks.report_tasks import process_file

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/public/report/export")
@limiter.limit("5/minute")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Empty filename")

    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are allowed"
        )
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024*1024):
            buffer.write(chunk)

    task = process_file.delay(file_path)

    return {
        "task_id": task.id
    }


@router.get("/public/report/export/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.status == "PENDING":
        return {"status": "pending"}

    if task_result.status == "STARTED":
        return {"status": "processing"}

    if task_result.status == "FAILURE":
        return {
            "status": "failed",
            "error": str(task_result.result)
        }

    if task_result.status == "SUCCESS":
        return {
            "status": "done",
            "result": task_result.result
        }

    return {"status": task_result.status}


@router.get("/public/report/download/{task_id}")
async def download(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result.ready():
        raise HTTPException(status_code=400, detail="Task not ready")

    if task_result.status != "SUCCESS":
        raise HTTPException(status_code=400, detail="Task failed")

    file_path = task_result.result["file"]

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename="report.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


