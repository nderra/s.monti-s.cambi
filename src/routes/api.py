# src/routes/api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..schemas import schemas
from ..models import models

router = APIRouter()

@router.get("/expansions/", response_model=List[schemas.Expansion])
def get_expansions(db: Session = Depends(get_db)):
   return db.query(models.Expansion).all()

@router.get("/expansions/{expansion_id}", response_model=schemas.Expansion)
def get_expansion(expansion_id: int, db: Session = Depends(get_db)):
   expansion = db.query(models.Expansion).filter(models.Expansion.id == expansion_id).first()
   if not expansion:
       raise HTTPException(status_code=404, detail="Expansion not found")
   return expansion

@router.post("/expansions/", response_model=schemas.Expansion)
def create_expansion(expansion: schemas.ExpansionCreate, db: Session = Depends(get_db)):
   db_expansion = models.Expansion(**expansion.dict())
   db.add(db_expansion)
   db.commit()
   db.refresh(db_expansion)
   return db_expansion

@router.get("/expansions/{expansion_id}/cards/", response_model=List[schemas.Card])
def get_cards_by_expansion(expansion_id: int, db: Session = Depends(get_db)):
   cards = db.query(models.Card).filter(models.Card.expansion_id == expansion_id).all()
   return cards
