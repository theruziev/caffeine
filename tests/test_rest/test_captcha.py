import httpx
import pytest
from asynctest import Mock

from caffeine.rest.utils.captcha import Recaptcha


class MockResponse:
    status_code = 200
    data = {}

    def __init__(self, status, data):
        self.data = data
        self.status_code = status

    def json(self):
        return self.data


@pytest.mark.parametrize(
    "code, status, result", [(200, True, True), (404, True, False), (200, False, False)]
)
@pytest.mark.asyncio
async def test_captcha(code, status, result):
    r = Recaptcha("SECRET_KEY")
    await r.shutdown()
    r.client = Mock(httpx.AsyncClient)

    async def side_effect(*args, **kwargs):
        return MockResponse(code, {"success": status})

    r.client.post.side_effect = side_effect
    res = await r.check("blah")
    assert res == result

    await r.shutdown()
