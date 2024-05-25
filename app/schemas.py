from datetime import date
from uuid import UUID

from pydantic import BaseModel, Json


class SMusician(BaseModel):
    first_name: str
    last_name: str
    birth_date: date


class SMusicianInfo(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    birth_date: date


class SMusicianInfoWithRelationships(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    birth_date: date
    awards: Json[list]
    pieces: Json[list]
