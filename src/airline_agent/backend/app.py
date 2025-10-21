import argparse
import os

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.airline_agent.backend.routers.airline_agent import router

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
    parser.add_argument("--kb-path", type=str, required=True)
    parser.add_argument("--vector-db-path", type=str, required=True)
    parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    os.environ["KB_PATH"] = args.kb_path
    os.environ["VECTOR_DB_PATH"] = args.vector_db_path

    uvicorn.run(
        "src.airline_agent.backend.app:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
    )
