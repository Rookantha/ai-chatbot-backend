# app/exceptions/errors.py
from fastapi import HTTPException

class GoogleAPIError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Google API Error: {detail}")

class ResponseParseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Response Parsing Error: {detail}")
