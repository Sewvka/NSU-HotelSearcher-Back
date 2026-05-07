import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from api.auth_handlers import login_router
from api.handlers import user_router, search_router
from api.hotel_handlers import hotel_router

app = FastAPI(title="HotelSearcher")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_api_router = APIRouter()

main_api_router.include_router(login_router, prefix="/login", tags=['login'])
main_api_router.include_router(user_router, prefix='/user', tags=['user'])
main_api_router.include_router(hotel_router, prefix='/hotel', tags=['hotel'])
main_api_router.include_router(search_router, prefix="/search", tags=['search'])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)