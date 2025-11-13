from fastapi import HTTPException


class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database unavailable"):
        super().__init__(status_code=503, detail=detail)