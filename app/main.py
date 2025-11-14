import os
from fastapi import FastAPI, HTTPException, Depends, Header
from typing import List, Optional
from app import schemas, repository, models
from app.database import engine, get_db
from sqlalchemy.orm import Session

# Создаём таблицы при старте
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Kanban API")

API_KEY = os.getenv("API_KEY", "api_authorization_key")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")

# Boards
@app.post("/boards", status_code=201, response_model=schemas.Board)
def create_board(board: schemas.Board, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    return repository.create_board(db, board)

@app.get("/boards", response_model=List[schemas.Board])
def list_boards(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    return repository.get_boards(db)

# Lists
@app.post("/lists", status_code=201, response_model=schemas.ListKanban)
def create_list(list_item: schemas.ListKanban, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    db_list = repository.create_list(db, list_item)
    if not db_list:
        raise HTTPException(status_code=404, detail="Board not found")
    return db_list

@app.get("/boards/{board_id}/lists", response_model=List[schemas.ListKanban])
def get_lists_by_board(board_id: int, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    if not repository.board_exists(db, board_id):
        raise HTTPException(status_code=404, detail="Board not found")
    return repository.get_lists_by_board(db, board_id)

# Cards
@app.post("/cards", status_code=201, response_model=schemas.Card)
def create_card(card: schemas.Card, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    db_card = repository.create_card(db, card)
    if not db_card:
        raise HTTPException(status_code=404, detail="List not found")
    return db_card

@app.get("/cards", response_model=List[schemas.Card])
def get_cards(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key)
    return repository.get_cards(db, status, assignee)

@app.get("/cards/{card_id}", response_model=schemas.Card)
def get_card(card_id: int, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    card = repository.get_card(db, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.put("/cards/{card_id}", response_model=schemas.Card)
def update_card(card_id: int, updated: schemas.Card, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    card = repository.update_card(db, card_id, updated)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    repository.delete_card(db, card_id)

@app.post("/cards/{card_id}/move", response_model=schemas.Card)
def move_card(card_id: int, target_list_id: int, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    verify_api_key(x_api_key)
    card = repository.move_card(db, card_id, target_list_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card or target list not found")
    return card