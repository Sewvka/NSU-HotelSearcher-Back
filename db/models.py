import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)


class SearchPoint(Base):
    __tablename__ = "search_points"

    search_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    distance = Column(Integer, nullable=False)
    distance_type = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)



class Hotel(Base):
    __tablename__ = 'hotels'

    city_id = Column(Integer, nullable=False)
    parse_id = Column(Integer, nullable=False, unique=True)
    hotel_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String, nullable=False, unique=True)
    link = Column(String, nullable=False, unique=True)


class HotelsToSearchPoint(Base):
    __tablename__ = "hotels_to_search"

    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(ForeignKey("hotels.hotel_id"), nullable=False)
    searchpoint_id = Column(ForeignKey("search_points.search_id"), nullable=False)


class Room(Base):
    __tablename__ = 'rooms'

    __table_args__ = (
        UniqueConstraint('hotel_id', 'room_type', 'name'),
    )

    room_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(ForeignKey("hotels.hotel_id"), nullable=False)
    room_type = Column(String, nullable=False)
    name = Column(String, nullable=False)


class RoomsCntPerDay(Base):
    __tablename__ = "rooms_cnt_per_day"

    roomcnt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(ForeignKey('rooms.room_id'), nullable=False)
    date = Column(DateTime, nullable=False)
    cnt = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

