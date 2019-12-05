# API composer prototype

The following frameworks and libraries are used:

* [FastAPI](https://fastapi.tiangolo.com/) (based on [Starlette](https://www.starlette.io))
* [HTTPX](https://www.encode.io/httpx)

To install dependencies: `pip install -r requirements.txt` or `poetry install`

To run the server for development: `uvicorn api_composer.app:app --reload`

There is one endpoint:

- `/?market_of_interest=<country name>`

Docs are served at `/docs`.
