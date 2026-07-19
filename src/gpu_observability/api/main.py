"""HTTP API for GPU observability queries."""

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sanic import Request, Sanic, json
from sanic.exceptions import NotFound
from sanic.response import HTTPResponse

from gpu_observability.config import data_path
from gpu_observability.core import queries

app = Sanic("gpu-observability")


@app.middleware("response")
async def add_cors_headers(_: Request, response: HTTPResponse) -> None:
    response.headers["access-control-allow-origin"] = "*"
    response.headers["access-control-allow-methods"] = "GET, OPTIONS"
    response.headers["access-control-allow-headers"] = "Content-Type"


def _serializable(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _run_query(query: Callable[[Path], list[dict[str, Any]]]) -> HTTPResponse:
    try:
        rows = query(data_path())
    except FileNotFoundError as error:
        raise NotFound(str(error)) from error
    payload = [
        {key: _serializable(value) for key, value in row.items()} for row in rows
    ]
    return json(payload)


@app.get("/summary")
async def summary(_: Request) -> HTTPResponse:
    return _run_query(queries.summary)


@app.get("/waste")
async def waste(_: Request) -> HTTPResponse:
    return _run_query(queries.waste)


@app.get("/by-model")
async def by_model(_: Request) -> HTTPResponse:
    return _run_query(queries.by_model)


@app.get("/trend")
async def trend(_: Request) -> HTTPResponse:
    return _run_query(queries.trend)


@app.get("/failure-rate")
async def failure_rate(_: Request) -> HTTPResponse:
    return _run_query(queries.failure_rate)


@app.get("/by-experiment")
async def by_experiment(_: Request) -> HTTPResponse:
    return _run_query(queries.by_experiment)


@app.get("/")
async def health(_: Request):
    return json({"status": "ok"})