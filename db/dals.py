import uuid
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Hotel, Room, SearchPoint, HotelsToSearchPoint, RoomsCntPerDay


class UserDAL:
    """Data access layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, email: str, password: str
    ) -> User:
        new_user = User(
            email=email,
            password=password
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

class HotelDAL:
    """Data access layer for operating Hotel info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def create_hotel(self, user_id: uuid.UUID, name: str, longitude: float, latitude: float, address: str, link: str) -> Hotel:
        new_hotel = Hotel(
            user_id=user_id,
            name=name,
            longitude=longitude,
            latitude=latitude,
            address=address,
            link=link
        )
        self.db_session.add(new_hotel)
        await  self.db_session.flush()
        return new_hotel

    async def get_hotel_by_id(self, hotel_id: UUID) -> Union[Hotel, None]:
        query = select(Hotel).where(Hotel.hotel_id == hotel_id)
        return await self.db_session.scalar(query)



class RoomDAL:
    """Data access layer for operating Room info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def create_room(self, hotel_id: UUID, room_type: str) -> Room:
        new_room = Room(hotel_id=hotel_id, room_type=room_type)
        self.db_session.add(new_room)
        await  self.db_session.flush()
        return new_room


    async def get_room_by_id(self, room_id:UUID) -> Union[Room, None]:
        query = select(Room).where(Room.room_id == room_id)
        res = await self.db_session.execute(query)
        room_row = res.fetchone()
        if room_row is not None:
            return room_row[0]

    async def get_rooms_by_hotel_id(self, hotel_id:UUID):
        query = select(Room).where(Room.hotel_id == hotel_id)
        res = await self.db_session.scalars(query)
        hotels = res.all()
        return hotels

class SearchDAL:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def create_search(self, user_id: uuid.UUID, longitude: float, latitude: float, address: str, distance: int,
                            distance_type: str):
        new_search = SearchPoint(
            user_id=user_id,
            longitude=longitude,
            latitude=latitude,
            address=address,
            distance=distance,
            distance_type=distance_type
        )
        self.db_session.add(new_search)
        await  self.db_session.flush()
        return new_search


    async def get_searches_by_user_id(self, user_id: uuid.UUID):
        query = select(SearchPoint).where(SearchPoint.user_id == user_id)
        res = await self.db_session.scalars(query)
        return res.all()


    async def get_search_by_id(self, search_id: uuid.UUID):
        query = select(SearchPoint).where(SearchPoint.search_id == search_id)
        search = await self.db_session.scalar(query)
        return search


class HotelsToSearchDAL:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def get_hotels_by_search_id(self, search_id: UUID):
        query = select(HotelsToSearchPoint.hotel_id).where(HotelsToSearchPoint.searchpoint_id == search_id)
        res = await self.db_session.scalars(query)
        return res.all()


class RoomCntPerDayDAL:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def get_stats_by_room_id(self, room_id:UUID):
        query = select(RoomsCntPerDay).where(RoomsCntPerDay.room_id == room_id)
        res = await self.db_session.scalars(query)
        stats = res.all()
        return stats