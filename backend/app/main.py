from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api.routes import router as api_router
from app.websocket.feed import router as feed_router
from app.websocket.chat import router as chat_router
from app.simulator import run_simulator


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_simulator())
    yield
    task.cancel()


app = FastAPI(title="FinSight AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],    # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(feed_router)
app.include_router(chat_router)