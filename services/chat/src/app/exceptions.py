from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BookNotFoundException(HTTPException):
    def __init__(self, book_pk: str, headers: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book not found for {book_pk}",
            headers=headers,
        )


class RoomNotFoundException(HTTPException):
    def __init__(self, room_pk: str, headers: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room not found for {room_pk}",
            headers=headers,
        )


class BookChainNotFoundException(HTTPException):
    def __init__(self, book_pk: str, headers: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book chain not found for {book_pk}",
            headers=headers,
        )
