import json
import os
import atexit
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

# Настройки
API_KEY = "api_authorization_key"  # для простоты; в продакшене — из переменных окружения
DATA_FILE = "data.json"

# Модели данных
class Board(BaseModel):
    id: Optional[int] = None
    name: str

class ListKanban(BaseModel):
    id: Optional[int] = None
    board_id: int
    name: str

class Card(BaseModel):
    id: Optional[int] = None
    list_id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: str = "todo" 

# Инициализация данных
boards: List[Board] = []
lists: List[ListKanban] = []
cards: List[Card] = []

# Загрузка данных при старте
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        boards = [Board(**b) for b in raw.get("boards", [])]
        lists = [ListKanban(**l) for l in raw.get("lists", [])]
        cards = [Card(**c) for c in raw.get("cards", [])]

# Сохранение при завершении
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "boards": [b.dict() for b in boards],
            "lists": [l.dict() for l in lists],
            "cards": [c.dict() for c in cards],
        }, f, ensure_ascii=False, indent=2)

atexit.register(save_data)

# Вспомогательные функции
def get_next_id(lst):
    return max([item.id for item in lst], default=0) + 1

# FastAPI приложение
app = FastAPI(title="Mini Kanban API")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Эндпоинты

# Доска
@app.post("/boards", status_code=201)
def create_board(board: Board, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    board.id = get_next_id(boards)
    boards.append(board)
    return board

@app.get("/boards")
def list_boards(x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return boards

# Задачи
@app.post("/lists", status_code=201)
def create_list(list_item: ListKanban, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    if not any(b.id == list_item.board_id for b in boards):
        raise HTTPException(status_code=404, detail="Board not found")
    list_item.id = get_next_id(lists)
    lists.append(list_item)
    return list_item

@app.get("/boards/{board_id}/lists")
def get_lists_by_board(board_id: int, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    board_exists = any(b.id == board_id for b in boards)
    if not board_exists:
        raise HTTPException(status_code=404, detail="Board not found")
    return [l for l in lists if l.board_id == board_id]

# Карточка задач
@app.post("/cards", status_code=201)
def create_card(card: Card, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    if not any(l.id == card.list_id for l in lists):
        raise HTTPException(status_code=404, detail="List not found")
    card.id = get_next_id(cards)
    cards.append(card)
    return card

@app.get("/cards")
def get_cards(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    result = cards
    if status:
        result = [c for c in result if c.status == status]
    if assignee:
        result = [c for c in result if c.assignee == assignee]
    return result

@app.get("/cards/{card_id}")
def get_card(card_id: int, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    for c in cards:
        if c.id == card_id:
            return c
    raise HTTPException(status_code=404, detail="Card not found")

@app.put("/cards/{card_id}")
def update_card(card_id: int, updated: Card, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    for i, c in enumerate(cards):
        if c.id == card_id:
            updated.id = card_id
            cards[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Card not found")

@app.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    global cards
    cards = [c for c in cards if c.id != card_id]

@app.post("/cards/{card_id}/move")
def move_card(card_id: int, target_list_id: int, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    if not any(l.id == target_list_id for l in lists):
        raise HTTPException(status_code=404, detail="Target list not found")
    for c in cards:
        if c.id == card_id:
            c.list_id = target_list_id
            return c
    raise HTTPException(status_code=404, detail="Card not found")