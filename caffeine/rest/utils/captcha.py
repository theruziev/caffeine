import httpx


class Recaptcha:
    url = "https://www.google.com/recaptcha/api/siteverify"

    def __init__(self, secret):
        self.secret = secret
        self.session = httpx.AsyncClient()

    async def check(self, response):
        response = await self.session.post(
            self.url, data={"response": response, "secret": self.secret}
        )

        if response.status_code != 200:
            return False

        data = response.json()
        return data.get("success", False)

    async def shutdown(self):
        await self.session.close()
