from logging import getLogger
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.hashing import Hasher
from api.models import UserCreate, UserShow, SearchCreate, SearchShow, HotelFull, RoomFull, SearchFull
from db.dals import UserDAL, SearchDAL, HotelsToSearchDAL, HotelDAL, RoomDAL, RoomCntPerDayDAL
from db.session import get_db
from tasks.tasks import parse_hotels

user_router = APIRouter()
search_router = APIRouter()

logger = getLogger(__name__)


async def _create_new_user(body: UserCreate, session) -> UserShow:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            email=body.email,
            password=Hasher.get_password_hash(body.password),
        )
        return UserShow(
            user_id=user.user_id,
            email=user.email,
        )

async def _get_user_by_id(user_id, db) -> Union[UserShow, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(
                user_id=user_id
            )
            if user is not None:
                return UserShow(
                    user_id=user.user_id,
                    email=user.email
                )


async def _create_search(body: SearchCreate, session: AsyncSession) -> Union[SearchShow, None]:
    async with session.begin():
        search_dal = SearchDAL(session)
        search = await search_dal.create_search(
            user_id=body.user_id,
            longitude=body.longitude,
            latitude=body.latitude,
            address=body.address,
            distance=body.distance,
            distance_type=body.distance_type
        )
        parse_hotels.delay(search.search_id)
        return SearchShow(
            search_id=search.search_id,
            user_id=search.user_id,
            longitude=search.longitude,
            latitude=search.latitude,
            address=search.address,
            distance=search.distance,
            distance_type=search.distance_type
        )


async def _get_searches_by_user_id(user_id, session):
    async with session.begin():
        search_dal = SearchDAL(session)
        db_searches = await search_dal.get_searches_by_user_id(user_id)
        searches = []
        for search in db_searches:
            searches.append(SearchShow(
                search_id=search.search_id,
                user_id=search.user_id,
                longitude=search.longitude,
                latitude=search.latitude,
                address=search.address,
                distance=search.distance,
                distance_type=search.distance_type
            ).dict())
        return searches


async def _get_search_by_id(search_id: UUID, session):
    async with session.begin():
        search_dal = SearchDAL(session)
        search = await search_dal.get_search_by_id(search_id)
        search_full = SearchFull(search_id=search.search_id, user_id=search.user_id, longitude=search.longitude,
                                 latitude=search.latitude, address=search.address, distance=search.distance,
                                 distance_type=search.distance_type)
        if search.completed:
            hotels_to_search_dal = HotelsToSearchDAL(session)
            hotels = await hotels_to_search_dal.get_hotels_by_search_id(search_id)
            hotel_dal = HotelDAL(session)
            hotels_pyd = []
            room_id = 0
            for hotel_id in hotels:
                hotel_today_stat = [[], []]
                hotel = await hotel_dal.get_hotel_by_id(hotel_id)
                hotel_pyd = HotelFull(name=hotel.name, hotel_id=hotel.hotel_id,
                                      longitude=hotel.longitude, latitude=hotel.latitude,
                                      address=hotel.address, link=hotel.link)
                rooms_pyd = []
                room_dal = RoomDAL(session)
                rooms = await room_dal.get_rooms_by_hotel_id(hotel_id)
                for room in rooms:
                    room_pyd = RoomFull(name=room.name, room_id=room_id, room_type=room.room_type)

                    room_stats_dal = RoomCntPerDayDAL(session)
                    stats = await room_stats_dal.get_stats_by_room_id(room.room_id)
                    if stats[0].cnt != 0:
                        if room.name not in hotel_today_stat[1]:
                            hotel_today_stat[0].append(stats[-1].cnt)
                            hotel_today_stat[1].append(room.name)
                        else:
                            pos = hotel_today_stat[1].index(room.name)
                            hotel_today_stat[0][pos] += stats[-1].cnt
                    stats_cnt_pyd = []
                    stats_price_pyd = []
                    for stat in stats:
                        room_cnt_stat = (stat.date, stat.cnt)
                        room_price_stat = (stat.date, stat.price)
                        stats_cnt_pyd.append(room_cnt_stat)
                        stats_price_pyd.append(room_price_stat)
                    room_pyd.room_stats_cnt = stats_cnt_pyd
                    room_pyd.room_stats_price = stats_price_pyd
                    rooms_pyd.append(room_pyd)
                    room_id += 1
                hotel_pyd.last_stat = hotel_today_stat
                hotel_pyd.rooms = rooms_pyd
                hotels_pyd.append(hotel_pyd)
            search_full.hotels = hotels_pyd
        return search_full







@user_router.post("/", response_model=UserShow)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> UserShow:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.get("/", response_model=UserShow)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserShow:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return user


@search_router.post("/", response_model=SearchShow)
async def create_show(body: SearchCreate, db: AsyncSession = Depends(get_db)):
    # TODO auth only
    user = await _get_user_by_id(user_id=body.user_id, db=db)
    if user is not None:
        return await _create_search(body, db)


@search_router.get("/", response_model=list[SearchShow])
async def get_searches_by_user_id(user_id: UUID, db: AsyncSession = Depends(get_db)):
    searches =  await _get_searches_by_user_id(user_id=user_id, session=db)
    return searches


@search_router.get("/show", response_model=SearchFull)
async def get_search_by_id(search_id: UUID, db: AsyncSession = Depends(get_db)) -> SearchFull:
    return await _get_search_by_id(search_id, db)