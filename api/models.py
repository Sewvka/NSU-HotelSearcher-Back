import datetime
import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, validator, EmailStr

class TunedModel(BaseModel):

    # convert event non dict obj to json
    class Config:
        orm_mode = True


class UserShow(TunedModel):
    user_id: uuid.UUID
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class HotelCreate(BaseModel):
    user_id: uuid.UUID
    radius: int
    name: str
    longitude: float
    latitude: float
    address: str
    link: str


class HotelShow(TunedModel):
    hotel_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    longitude: float
    latitude: float
    address: str
    link: str


class Token(BaseModel):
    access_token: str
    token_type: str


class SearchCreate(BaseModel):
    user_id: uuid.UUID
    longitude: float
    latitude: float
    address: str
    distance: int
    distance_type: str


class SearchShow(TunedModel):
    search_id: uuid.UUID
    user_id: uuid.UUID
    longitude: float
    latitude: float
    address: str
    distance: int
    distance_type: str


class RoomStat(TunedModel):
    roomcnt_id: uuid.UUID
    room_id: uuid.UUID
    date: datetime.datetime
    cnt: int
    price: float


class RoomFull(TunedModel):
    name: str
    room_type: str
    room_id: int
    room_stats_cnt: list[tuple[datetime.datetime, int]] = []
    room_stats_price: list[tuple[datetime.datetime, float]] = []


class HotelFull(TunedModel):
    hotel_id: uuid.UUID
    name: str
    longitude: float
    latitude: float
    address: str
    link: str
    rooms: list[RoomFull] = []
    last_stat: tuple[list[int], list[str]] = ()

class SearchFull(TunedModel):
    search_id: uuid.UUID
    user_id: uuid.UUID
    longitude: float
    latitude: float
    address: str
    distance: int
    distance_type: str
    hotels: list[HotelFull] = []



