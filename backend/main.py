"""
FastAPI application entry-point.

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.router import router, _process_events


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    # Start the background event-processing loop
    task = asyncio.create_task(_process_events())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI SOC Simulator",
    description=(
        "Live attack simulator with AI-driven detection, response, and compliance logging. "
        "Fully automated — Attack → Detection → AI reasoning → Auto-response → Compliance logging."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the React dev server (port 3000) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve React build artifacts (populated by `npm run build` inside frontend/)
try:
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
except RuntimeError:
    pass  # frontend/build not present yet – API-only mode
