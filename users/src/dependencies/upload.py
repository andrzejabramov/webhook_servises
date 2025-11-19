from fastapi import UploadFile, HTTPException

from src.settings import settings
from src.exceptions.exceptions import FileUploadError

async def validate_upload_file(file: UploadFile) -> UploadFile:
    """Валидация файла: размер, расширение."""
    if not file.filename:
        raise FileUploadError("Файл не имеет имени")

    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_UPLOAD_EXTENSIONS))
        raise FileUploadError(f"Разрешены только файлы: {allowed}")

    if file.size and file.size > settings.MAX_UPLOAD_FILE_SIZE:
        max_mb = settings.MAX_UPLOAD_FILE_SIZE // (1024 * 1024)
        raise FileUploadError(f"Файл слишком большой (макс. {max_mb} МБ)")

    return file