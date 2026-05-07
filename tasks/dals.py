import datetime
import uuid
from typing import Union

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import Hotel, SearchPoint, HotelsToSearchPoint, HotelsToSearchPoint, Room, RoomsCntPerDay


class HotelDAL:
    """Sync Data access layer for hotel"""

    def __init__(self, session: Session):
        self.session = session


    def get_all_hotels(self):
        query = select(Hotel)
        res = self.session.execute(query)
        hotels = res.all()
        if hotels is not None:
            return hotels


    def get_hotel_by_id(self, hotel_id: uuid.UUID) -> Union[Hotel, None]:
        query = select(Hotel).where(Hotel.hotel_id == hotel_id)
        res = self.session.execute(query)
        hotel_row = res.first()
        if hotel_row is not None:
            return hotel_row[0]


    def get_or_create_hotel_for_parsing(self, name: str, longitude: float, latitude: float, address: str,
                                 link: str, city_id: int, parse_id: int) -> Union[Hotel, None]:
        new_hotel = Hotel(
            name=name,
            longitude=longitude,
            latitude=latitude,
            address=address,
            link=link,
            city_id=city_id,
            parse_id=parse_id
        )
        self.session.add(new_hotel)
        try:
            self.session.commit()
            return new_hotel
        except IntegrityError:
            self.session.rollback()
            query = select(Hotel).where(Hotel.name == name, Hotel.address==address)
            hotel = self.session.scalar(query)
            return hotel



class SearchDAL:

    def __init__(self, session: Session):
        self.session = session

    def get_search_by_id(self, search_id: uuid.UUID) -> Union[SearchPoint, None]:
        query = select(SearchPoint).where(SearchPoint.search_id == search_id)
        res = self.session.execute(query)
        search_row = res.first()
        if search_row is not None:
            return search_row[0]


    def change_search_status_by_id(self, search_id: uuid.UUID) -> bool:
        search = self.get_search_by_id(search_id)
        search.completed = True
        self.session.commit()
        return self.get_search_by_id(search_id).completed
        # query = update(SearchPoint).values(completed=True).where(SearchPoint.search_id==search_id)
        # self.session.execute(query)
        # print(self.get_search_by_id(search_id).completed)
        # return True

class HotelToSearchDAL:

    def __init__(self, session: Session):
        self.session = session


    def create_new_appointment(self, hotel_id: uuid.UUID, search_id: uuid.UUID) -> HotelsToSearchPoint:
        new_appointment = HotelsToSearchPoint(hotel_id=hotel_id, searchpoint_id=search_id)
        self.session.add(new_appointment)
        self.session.commit()
        return new_appointment

    def get_all_hotels_ids(self):
        query = select(HotelsToSearchPoint.hotel_id)
        hotels = self.session.scalars(query)
        return hotels.all()

class RoomDAL:

    def __init__(self, session: Session):
        self.session = session

    def get_or_create_room(self, hotel_id: uuid.UUID, room_type: str, name: str):
        new_room = Room(hotel_id=hotel_id, room_type=room_type, name=name)
        self.session.add(new_room)
        try:
            self.session.commit()
            return new_room
        except IntegrityError:
            self.session.rollback()
            query = select(Room).where(Room.hotel_id == hotel_id, Room.room_type == room_type, Room.name == name)
            res = self.session.execute(query).first()
            return res[0]


class RoomCntPerDayDAL:

    def __init__(self, session: Session):
        self.session = session

    def create(self, room_id: uuid.UUID, date: datetime.datetime, cnt: int, price: float):
        new = RoomsCntPerDay(
            room_id=room_id, date=date, cnt=cnt, price=price
        )
        self.session.add(new)
        self.session.commit()
        return new