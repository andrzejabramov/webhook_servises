import pandas as pd
from io import BytesIO
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Set

from src.exceptions.exceptions import FileUploadError, ValidationError

def normalize_columns(columns: list) -> list:
    """Приводит названия колонок к единому виду (например, snake_case)."""
    return [col.strip().lower().replace(" ", "_") for col in columns]

async def read_file_to_dicts(file: UploadFile, required_columns: set) -> List[Dict]:
    """
    Читает .csv / .xlsx и возвращает список строк как dict.
    Проверяет наличие обязательных колонок.
    """
    contents = await file.read()
    await file.seek(0)

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents), encoding="utf-8-sig")
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise ValidationError("file_format", file.filename or "unknown", "Неподдерживаемый формат")
    except Exception as e:
        raise FileUploadError("Ошибка чтения файла")

    df.columns = normalize_columns(list(df.columns))
    missing = required_columns - set(df.columns)
    if missing:
        raise ValidationError("file_columns", str(missing), f"Отсутствуют обязательные колонки: {missing}")

    return df.to_dict(orient="records")