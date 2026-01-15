from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["Receipt"])
