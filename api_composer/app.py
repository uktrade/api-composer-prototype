from fastapi import FastAPI
from starlette.responses import UJSONResponse

from api_composer import settings
from api_composer.api_client import get_composed_companies

app = FastAPI(debug=settings.DEBUG)


@app.get("/", response_class=UJSONResponse)
async def root(market_of_interest: str = None):
    return await get_composed_companies(market_of_interest)
