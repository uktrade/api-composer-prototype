from httpx import StatusCode
from httpx.middleware import Middleware
from mohawk import Sender


class HawkAuth(Middleware):
    """Hawk authentication middleware."""

    def __init__(self, api_id, api_key, signing_algorithm='sha256', verify_response=True):
        """Initialise the authenticator with the signing parameters."""
        self._api_id = api_id
        self._api_key = api_key
        self._signing_algorithm = signing_algorithm
        self._verify_response = verify_response

    async def __call__(self, request, get_response):
        """Sign a request and verify the response."""
        credentials = {
            'id': self._api_id,
            'key': self._api_key,
            'algorithm': self._signing_algorithm,
        }

        sender = Sender(
            credentials,
            str(request.url),
            request.method,
            content=request.content or '',
            content_type=request.headers.get('Content-Type', ''),
        )

        request.headers['Authorization'] = sender.request_header

        response = await get_response(request)

        if self._verify_response:
            if not (
                StatusCode.is_client_error(response.status_code)
                or StatusCode.is_server_error(response.status_code)
            ):
                sender.accept_response(
                    response.headers['Server-Authorization'],
                    content=await response.read(),
                    content_type=response.headers['Content-Type'],
                )

        return response
