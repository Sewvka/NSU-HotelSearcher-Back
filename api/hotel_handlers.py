from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import HotelCreate, HotelShow
from db.dals import HotelDAL, UserDAL
from db.session import get_db
from tasks.tasks import parse_hotels

hotel_router = APIRouter()


async def _create_new_hotel(body: HotelCreate, session) -> HotelShow:
    async with session.begin():
        hotel_dal = HotelDAL(session)
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(body.user_id)
        if user is not None:
            hotel = await hotel_dal.create_hotel(
                user_id=user.user_id,
                name=body.name,
                longitude=body.longitude,
                latitude=body.latitude,
                address=body.address,
                link=body.link
            )
            return HotelShow(
                user_id=hotel.user_id,
                hotel_id=hotel.hotel_id,
                name=hotel.name,
                longitude=hotel.longitude,
                latitude=hotel.latitude,
                address=hotel.address,
                link=hotel.link
            )


async def _get_hotel_by_id(hotel_id, db) -> Union[HotelShow, None]:
    async with db as session:
        async with session.begin():
            hotel_dal = HotelDAL(session)
            hotel = await hotel_dal.get_hotel_by_id(hotel_id=hotel_id)
            if hotel is not None:
                return HotelShow(
                    user_id=hotel.user_id,
                    hotel_id=hotel.hotel_id,
                    name=hotel.name,
                    longitude=hotel.longitude,
                    latitude=hotel.latitude,
                    address=hotel.address,
                    link=hotel.link
                )


@hotel_router.post("/", response_model=HotelShow)
async def create_hotel(body: HotelCreate, db: AsyncSession = Depends(get_db)) -> HotelShow:
    return await _create_new_hotel(body, db)


@hotel_router.get("/", response_model=HotelShow)
async def get_hotel(hotel_id: UUID, db: AsyncSession = Depends(get_db)) -> HotelShow:
    hotel = await _get_hotel_by_id(hotel_id, db)
    if hotel is None:
        raise HTTPException(status_code=404, detail=f'Hotel with id {hotel_id} not found.')
    return hotel