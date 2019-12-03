import asyncio
from functools import wraps
from logging import getLogger
from time import perf_counter
from urllib.parse import urljoin

import httpx
from httpx import StatusCode, HTTPError

from api_composer import settings
from api_composer.hawk import HawkAuth


PAGE_SIZE = 1000
MAX_RESULTS = 10000
NUM_PAGES = MAX_RESULTS // PAGE_SIZE
TIMEOUT_SECS = 10

logger = getLogger(__name__)


def async_trace(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_ts = perf_counter()

        ret = await func(*args, **kwargs)

        end_ts = perf_counter()
        logger.info(
            f'{func.__name__}() args={args} kwargs={kwargs} executed in {end_ts-start_ts:.3f}s',
        )
        return ret

    return wrapper


@async_trace
async def get_composed_companies(market_of_interest):
    dh_companies, ds_companies = await asyncio.gather(
        _get_data_hub_companies(NUM_PAGES),
        _get_data_science_companies(NUM_PAGES, market_of_interest),
    )

    ds_company_mapping = {
        company['datahub_company_id']: company
        for company in ds_companies
        if company['datahub_company_id']
    }

    filtered_dh_companies = [
        {
            'data_hub': company,
            'data_science': ds_company_mapping[company['id']],
        }
        for company in dh_companies
        if company['id'] in ds_company_mapping
    ]

    return {
        'results': filtered_dh_companies,
        'counts': {
            'data_hub_results_fetched': len(dh_companies),
            'data_science_results_fetched': len(ds_companies),
            'data_science_results_fetched_with_data_hub_ids': len(ds_company_mapping),
        },
    }


@async_trace
async def _get_data_hub_companies(num_pages):
    pages = await asyncio.gather(
        *(_get_data_hub_companies_page(page_num) for page_num in range(num_pages)),
    )
    return [
        result
        for page in pages
        for result in page['results']
    ]


@async_trace
async def _get_data_science_companies(num_pages, market_of_interest):
    pages = await asyncio.gather(
        *(
            _get_data_science_companies_page(page_num, market_of_interest)
            for page_num in range(num_pages)
        ),
    )
    return [
        result
        for page in pages
        for result in page['result']
    ]


@async_trace
async def _get_data_hub_companies_page(page_num):
    url = urljoin(str(settings.DATA_HUB_API_URL), '/v4/public/search/company')
    auth = HawkAuth(
        settings.DATA_HUB_API_HAWK_ID,
        str(settings.DATA_HUB_API_HAWK_KEY),
        verify_response=False,
    )
    response = await httpx.post(
        url,
        auth=auth,
        json={
            'original_query': '',
            'offset': PAGE_SIZE * page_num,
            'limit': PAGE_SIZE,
        },
        timeout=TIMEOUT_SECS,
    )
    response.raise_for_status()
    return response.json()


@async_trace
async def _get_data_science_companies_page(page_num, market_of_interest):
    url = urljoin(str(settings.DATA_SCIENCE_API_URL), '/api/v1/company/search/')
    auth = HawkAuth(
        settings.DATA_SCIENCE_API_HAWK_ID,
        str(settings.DATA_SCIENCE_API_HAWK_KEY),
        verify_response=False,
    )

    body = {
        'filters': {
            'market_of_interest': [market_of_interest]
        },
    } if market_of_interest else {}

    try:
        response = await httpx.post(
            url,
            auth=auth,
            params={
                'offset': PAGE_SIZE * page_num,
                'limit': PAGE_SIZE,
            },
            json=body,
            timeout=TIMEOUT_SECS,
        )
        response.raise_for_status()
    except HTTPError as exc:
        if exc.response and exc.response.status_code == StatusCode.NOT_FOUND:
            return {
                'result': [],
            }
        raise

    return response.json()
