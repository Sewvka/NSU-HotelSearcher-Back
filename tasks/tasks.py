import datetime
import uuid
from logging import getLogger

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from settings import REDIS_BROKER_URL, REAL_DATABASE_URL_CEL, CRONITOR_API_KEY
from tasks.dals import HotelDAL, SearchDAL, HotelToSearchDAL, RoomDAL, RoomCntPerDayDAL
from tasks.parser import get_data, get_hotel_availability
from geopy.distance import geodesic
import cronitor.celery

from tasks.utils import convert_distance

cel_app = Celery('tasks', broker=REDIS_BROKER_URL)
cel_app.conf.broker_url = 'redis://25.56.214.53:6379/0'
logger = getLogger(__name__)
cronitor.api_key = CRONITOR_API_KEY


@cel_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60*3, parse_rooms.s(), name='Parse rooms')

cronitor.celery.initialize(cel_app)

def get_cel_db():
    engine = create_engine(REAL_DATABASE_URL_CEL)
    return engine

@cel_app.task
def parse_hotels(search_id: uuid.UUID):
    completed = False
    with Session(get_cel_db()) as session:
        search_dal = SearchDAL(session)
        search = search_dal.get_search_by_id(search_id)
        if search is not None:
            city = search.address.split(" ")[0]
            hotels = get_data(city)
            for hotel in hotels:
                with Session(get_cel_db()) as session_hotel:
                    hotel_dal = HotelDAL(session_hotel)
                    h = {"name": hotel.name, "longitude":hotel.address[1][0], "latitude":hotel.address[1][1],
                         "address": hotel.address[0], "link":hotel.min_price[1], "city_id": hotel.city_id,
                         "parse_id": hotel.parse_id}
                    new_hotel = hotel_dal.get_or_create_hotel_for_parsing(**h)

                    if new_hotel is not None and geodesic((new_hotel.latitude, new_hotel.longitude), (search.latitude, search.longitude)).km < convert_distance(search.distance, search.distance_type):
                        hotel_to_search_dal = HotelToSearchDAL(session_hotel)
                        appointment = hotel_to_search_dal.create_new_appointment(
                            hotel_id=new_hotel.hotel_id, search_id=search.search_id)
            completed = search_dal.change_search_status_by_id(search_id)
    return completed

@cel_app.task
def parse_rooms():
    with Session(get_cel_db()) as session:
        hotels_to_search_dal = HotelToSearchDAL(session)
        hotels_id = hotels_to_search_dal.get_all_hotels_ids()
        for id in hotels_id:
            hotel_dal = HotelDAL(session)
            hotel = hotel_dal.get_hotel_by_id(id)
            rooms = get_hotel_availability(hotel.parse_id, str(hotel.city_id))
            for room in rooms:
                with Session(get_cel_db()) as session_room:
                    room_dal = RoomDAL(session_room)
                    db_room = room_dal.get_or_create_room(
                        room_type=room.room_type, hotel_id=hotel.hotel_id, name=room.name)
                    room_cnt_dal = RoomCntPerDayDAL(session_room)
                    new_cnt = room_cnt_dal.create(
                        room_id=db_room.room_id,
                        date=datetime.datetime.now(),
                        cnt=room.cnt,
                        price=room.price
                    )
