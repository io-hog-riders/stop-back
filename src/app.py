from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.plan.router import router as plan_router
from routes.stops.router import router as stops_router
from routes.plan.mock_router import router as plan_mock_router
from routes.stops.mock_router import router as stops_mock_router

from contextlib import asynccontextmanager
from db.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    # potem rzeczy do wyczyszczenia można tu dodać

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    # "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_mock_router, prefix="/api/mock/route", tags=["Mock"])
app.include_router(stops_mock_router, prefix="/api/mock/stops", tags=["Mock"])

app.include_router(plan_router, prefix="/api/v1/route", tags=["V1"])
app.include_router(stops_router, prefix="/api/v1/stops", tags=["V1"])
