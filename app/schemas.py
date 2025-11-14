from pydantic import BaseModel
from typing import Optional

class Board(BaseModel):
    id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True

class ListKanban(BaseModel):
    id: Optional[int] = None
    board_id: int
    name: str

    class Config:
        from_attributes = True

class Card(BaseModel):
    id: Optional[int] = None
    list_id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: str = "todo"

    class Config:
        from_attributes = True