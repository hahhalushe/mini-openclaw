"""Mini-OpenClaw backend entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: scan skills, initialize agent, build memory index
    print("[startup] Mini-OpenClaw backend starting...")
    yield
    # Shutdown
    print("[shutdown] Mini-OpenClaw backend stopping...")


app = FastAPI(title="Mini-OpenClaw", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
