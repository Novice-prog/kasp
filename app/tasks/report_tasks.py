from uuid import uuid4

from app.core.celery_app import celery_app
import os

from app.services.excel_service import create_excel
from app.services.text_service import process_text
from app.utils.cleanup import cleanup_results

OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@celery_app.task
def process_file(file_path: str):
    try:
        cleanup_results()

        stats = process_text(file_path)

        result_file = os.path.join("results", f"{uuid4()}.xlsx")

        create_excel(stats, result_file)

        os.remove(file_path)

        return {"file": result_file}

    except Exception as e:
        print(f"[ERROR] {e}")
        raise
