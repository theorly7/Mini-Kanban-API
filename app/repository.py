from sqlalchemy.orm import Session
from app import models, schemas

def get_next_id(db: Session, model):
    last = db.query(model).order_by(model.id.desc()).first()
    return (last.id + 1) if last else 1

def create_board(db: Session, board: schemas.Board):
    db_board = models.Board(name=board.name)
    db_board.id = get_next_id(db, models.Board)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

def get_boards(db: Session):
    return db.query(models.Board).all()

def create_list(db: Session, list_item: schemas.ListKanban):
    board = db.query(models.Board).filter(models.Board.id == list_item.board_id).first()
    if not board:
        return None
    db_list = models.ListKanban(
        id=get_next_id(db, models.ListKanban),
        board_id=list_item.board_id,
        name=list_item.name
    )
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def get_lists_by_board(db: Session, board_id: int):
    return db.query(models.ListKanban).filter(models.ListKanban.board_id == board_id).all()

def create_card(db: Session, card: schemas.Card):
    lst = db.query(models.ListKanban).filter(models.ListKanban.id == card.list_id).first()
    if not lst:
        return None
    db_card = models.Card(
        id=get_next_id(db, models.Card),
        list_id=card.list_id,
        title=card.title,
        description=card.description,
        assignee=card.assignee,
        status=card.status
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def get_card(db: Session, card_id: int):
    return db.query(models.Card).filter(models.Card.id == card_id).first()

def get_cards(db: Session, status: str = None, assignee: str = None):
    query = db.query(models.Card)
    if status:
        query = query.filter(models.Card.status == status)
    if assignee:
        query = query.filter(models.Card.assignee == assignee)
    return query.all()

def update_card(db: Session, card_id: int, updated: schemas.Card):
    db_card = get_card(db, card_id)
    if not db_card:
        return None
    for key, value in updated.model_dump(exclude_unset=True).items():
        if key != 'id':
            setattr(db_card, key, value)
    db.commit()
    db.refresh(db_card)
    return db_card

def delete_card(db: Session, card_id: int):
    db_card = get_card(db, card_id)
    if db_card:
        db.delete(db_card)
        db.commit()

def move_card(db: Session, card_id: int, target_list_id: int):
    lst = db.query(models.ListKanban).filter(models.ListKanban.id == target_list_id).first()
    if not lst:
        return None
    db_card = get_card(db, card_id)
    if not db_card:
        return None
    db_card.list_id = target_list_id
    db.commit()
    db.refresh(db_card)
    return db_card

def board_exists(db: Session, board_id: int):
    return db.query(models.Board).filter(models.Board.id == board_id).first() is not None