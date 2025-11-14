from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class ListKanban(Base):
    __tablename__ = "lists"
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    name = Column(String, nullable=False)

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assignee = Column(String, nullable=True)
    status = Column(String, default="todo")