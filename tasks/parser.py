import datetime
import json
import random
import sys
import time

import requests
from pydantic import BaseModel

user_agents_file = "./user_agent.txt"
def get_user_agent():
    return random.choice(list(open(user_agents_file))).strip()


def get_destination_id(destination: str):
    headers = {"user-agent": get_user_agent()}
    url = f"https://www.travel.ru/hotel/locationresolver/getdestinationandhotellistjsonp?callback=callback&term={destination}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text[9:-1])
        return {"destination_id": data["locationList"][0]["id"], "country": data['locationList'][0]["country"]}


def get_search_ticket(city: str, guests_cnt: str, checkIn: str, checkOut: str) -> str:
    headers = {"user-agent": get_user_agent()}
    data = get_destination_id(city)
    url = f"https://www.travel.ru/hotel/search/?in={checkIn}&out={checkOut}&destid={data['destination_id']}&dest={city}&country={data['country']}&occ={guests_cnt}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        ticket = response.cookies['search_ticket']
        return ticket


def get_hotels(city: str, guests_cnt: str, checkIn: str, checkOut: str) -> [dict]:
    headers = {"user-agent": get_user_agent(), 'content-type': 'application/json;charset=UTF-8'}
    ticket = get_search_ticket(city, guests_cnt, checkIn, checkOut)
    url = "https://www.travel.ru/hotel/search/checkstatus/"
    input_data = {"searchObjectKey": f"SearchObject_{ticket}"}
    while True:
        response = requests.post(url, headers=headers,
                                 json=input_data)
        if response.status_code == 200:
            data = response.json()
            if data['searchObject']['isMainSearchComplete']:
                print("Поиск завершен")
                return data
            print('Жду попытки')
            time.sleep(1)


def get_hotel_availability(hotelId: int, destinationId: str):
    checkIn = datetime.datetime.today().strftime("%d.%m.%Y")
    checkOut = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
    headers = {"user-agent": get_user_agent(), 'content-type': 'application/json'}

    url = "https://www.travel.ru/hotel/hotelavailability/gethotelavailability"
    data = {
              "hotelId": hotelId,
              "query": f"in={checkIn}&out={checkOut}&hid={hotelId}&destid={destinationId}&dest=&country=&occ=1",
              "ticket": None
            }
    while True:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if not response_data['result']['IsCompleted']:
                data["ticket"] = response_data['result']['Ticket']
            else:
                rooms_res = []
                res_data = response.json()["result"]
                rooms = []
                rooms += res_data["RoomsWithMasterContent"] + res_data["RoomsWithoutMasterContent"]
                for hotel in rooms:
                    rooms_res.append(parse_room_json(hotel))
                return rooms_res


city = "Новосибирск"

class Hotel(BaseModel):
    parse_id: int
    city_id: int
    name: str
    address: tuple[str, tuple[str, str]]
    stars: int
    metro: bool
    description: str
    min_price: tuple[int, str]
    links: list[tuple[str, str]]


class Room(BaseModel):
    room_type: str
    name: str
    cnt: int
    price: float


def parse_room_json(inpRoom: dict) -> Room:
    room_type = inpRoom["RoomTypeCode"]
    name = inpRoom["Name"]
    cnt = inpRoom["AvailableCount"]
    price = inpRoom["Rates"][0]["DayPrice"]["RUB"]
    return Room(room_type=room_type, name=name, cnt=cnt, price=price)

def parse_hotel_json(inpHotel: dict, city_id: int):
    name = inpHotel['name']
    address = (inpHotel['address'], (inpHotel['longitude'], inpHotel['latitude']))
    stars = inpHotel['stars']
    metro = inpHotel['hasNearestMetro']
    parse_id = inpHotel['id']
    description = ''
    if inpHotel['brifDescription']:
        description += inpHotel['brifDescription']
    min_price = (sys.float_info.max, "")
    for key in inpHotel['features'].keys():
        if inpHotel['features'][key]['enabled']:
            if key == 'airport':
                description += 'Аэропорт: '
            description += f"{inpHotel['features'][key]['text']}\n "
    for key in inpHotel['hotelPrices'].keys():
        if inpHotel['hotelPrices'][key]['prices'][0]['periodPrice'] < min_price[0]:
            linkUrl = inpHotel['linkUrl'] if inpHotel['linkUrl'] else ""
            min_price = (inpHotel['hotelPrices'][key]['prices'][0]['periodPrice'], linkUrl)
    links = []
    for key in inpHotel['externalLinks']['links'].keys():
        links.append((key, inpHotel['externalLinks']['links'][key]))
    hotel = Hotel(name=name, address=address, stars=stars, metro=metro, description=description, min_price=min_price,
                  links=links, city_id=city_id, parse_id=parse_id)
    return hotel


def get_data(city: str) -> [Hotel]:
    checkIn = datetime.datetime.today().strftime("%d.%m.%Y")
    checkOut = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
    res_data = get_hotels(city, "1", checkIn, checkOut)
    hotels = res_data['hotels']
    city_id = res_data["searchObject"]["searchDestinationId"]
    new_hotels = []
    fl = True
    for hotel in hotels:
        new_hotels.append(parse_hotel_json(hotel, city_id))
        fl = False
    return new_hotels
