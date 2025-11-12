import argparse
import os

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from airline_agent.backend.routers.agent import router

API_PREFIX = "/api"

app = FastAPI(
    title="Cleanlab Demo Application",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(router)
app.include_router(api_router, prefix=API_PREFIX)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--mode",
        type=str,
        default="airline",
        choices=["airline", "red-teaming"],
        help="which agent to run: 'airline' for airline agent, 'red-teaming' for red-teaming agent",
    )

    args = parser.parse_args()

    os.environ["AGENT_MODE"] = args.mode

    uvicorn.run(
        "airline_agent.backend.app:app",
        host="127.0.0.1",
        port=args.port,
        reload=args.reload,
    )
